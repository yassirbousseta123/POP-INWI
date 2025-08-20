import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import pytz

class DataCleaner:
    """Système de nettoyage des données pour les POPs"""
    
    def __init__(self, data_dir="data"):
        # Convertir en chemin absolu si c'est un chemin relatif
        if not Path(data_dir).is_absolute():
            self.data_dir = Path.cwd() / data_dir
        else:
            self.data_dir = Path(data_dir)
        print(f"🔍 Chemin absolu du dossier data : {self.data_dir}")
        
    def get_regions(self):
        """Retourne la liste des régions disponibles"""
        return [d.name for d in self.data_dir.iterdir() if d.is_dir()]
    
    def get_pops(self, region):
        """Retourne la liste des POPs disponibles pour une région donnée"""
        region_path = self.data_dir / region
        if not region_path.exists():
            return []
        return [d.name for d in region_path.iterdir() if d.is_dir()]
        
    def get_pop_path(self, region, pop):
        """Retourne le chemin complet vers un POP spécifique"""
        return self.data_dir / region / pop
        
    def load_and_clean_csv(self, file_path, encoding='ISO-8859-1'):
        """
        Charge et nettoie un fichier CSV selon les spécifications:
        1. Supprime les colonnes 'Trend Flags'
        2. Filtre les lignes où Status != '{ok}'
        3. Valide les dates
        4. Standardise les statuts CLIM et porte
        """
        try:
            print(f"\n📄 Traitement du fichier : {file_path.name}")
            
            # Tester différents encodages
            encodings = ['ISO-8859-1', 'utf-8', 'utf-8-sig']
            first_lines = None
            used_encoding = None
            
            for enc in encodings:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        first_lines = [f.readline() for _ in range(3)]
                    used_encoding = enc
                    break
                except UnicodeDecodeError:
                    continue
                    
            if not first_lines:
                print(f"❌ Impossible de lire le fichier avec les encodages standards")
                return pd.DataFrame()
            print(f"   ℹ️ Premières lignes du fichier :")
            for i, line in enumerate(first_lines):
                print(f"   {i+1}: {line.strip()}")
            
            # Déterminer le délimiteur réel en analysant le contenu
            delimiters = [';', '|', ',', '\t']
            # Vérifier toutes les lignes pour le délimiteur réel
            all_lines_content = ''.join(first_lines)
            delimiter_counts = {d: all_lines_content.count(d) for d in delimiters}
            
            # Si une ligne contient une virgule mais le fichier utilise des point-virgules dans l'en-tête
            if ',' in first_lines[1] or ',' in first_lines[2]:
                delimiter = ','
            else:
                delimiter = max(delimiter_counts.items(), key=lambda x: x[1])[0]
            
            print(f"   📊 Délimiteur détecté : '{delimiter}' (occurrences : {delimiter_counts})")
            
            # Déterminer le nombre de lignes à sauter
            skiprows = 0
            if 'history:' in first_lines[0]:
                # Compter les lignes vides ou d'en-tête jusqu'aux données
                for line in first_lines:
                    if not line.strip() or 'history:' in line:
                        skiprows += 1
                    else:
                        break
                        
            # Déterminer l'unité et le format en fonction du nom de fichier
            # Déterminer le type de valeur en fonction du nom de fichier
            if 'Température' in file_path.name or 'Temperature' in file_path.name:
                value_col = 'Value (°C)'
            elif 'P.Active' in file_path.name or 'Active Power' in file_path.name:
                value_col = 'Value (kW)'
            else:
                value_col = 'Value'
            
            # Lecture du fichier selon son format
            try:
                if 'history:' in first_lines[0]:
                    # Fichiers avec en-tête spécial
                    df = pd.read_csv(
                        file_path,
                        delimiter=delimiter,
                        skiprows=skiprows,
                        names=['Timestamp', 'Trend Flags', 'Status', value_col],
                        encoding=used_encoding,
                        on_bad_lines='skip'
                    )
                else:
                    # Fichiers normaux
                    df = pd.read_csv(
                        file_path,
                        delimiter=delimiter,
                        encoding=used_encoding,
                        on_bad_lines='skip'
                    )
            except Exception as e:
                print(f"   ❌ Erreur lors de la lecture : {str(e)}")
                print("   ⚠️ Tentative de lecture alternative...")
                try:
                    df = pd.read_csv(
                        file_path,
                        delimiter=delimiter,
                        encoding=used_encoding,
                        on_bad_lines='skip'
                    )
                except Exception as e2:
                    print(f"   ❌ Échec de la lecture alternative : {str(e2)}")
                    return pd.DataFrame()
            
            print(f"   📊 Colonnes brutes : {df.columns.tolist()}")
            # Nettoyer les noms de colonnes
            df.columns = df.columns.str.strip()
            # Supprimer le BOM des noms de colonnes
            df.columns = [col.replace('\ufeff', '').replace('ï»¿', '') for col in df.columns]
            print(f"   📊 Colonnes nettoyées : {df.columns.tolist()}")
            
            # 1. Supprimer la colonne Trend Flags si elle existe
            if 'Trend Flags' in df.columns:
                df = df.drop(columns=['Trend Flags'])
            
            # 2. Filtrer les lignes où Status contient {ok}
            if 'Status' in df.columns:
                # Convertir en string d'abord pour éviter les erreurs
                df['Status'] = df['Status'].astype(str)
                df = df[df['Status'].str.lower().str.contains('{ok}')]
            
            # 3. Gérer les dates avec support des fuseaux horaires
            if 'Timestamp' in df.columns:
                # Supprimer les suffixes de fuseau horaire
                df['Timestamp'] = (
                    df['Timestamp']
                    .astype(str)
                    .str.replace(r'\s+(WEST|WET|GMT|UTC|CET|CEST)$', '', regex=True)
                )
                # Convertir en datetime
                df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
                # Supprimer les lignes avec des dates invalides
                df = df.dropna(subset=['Timestamp'])
            
            # 4. Standardiser les statuts CLIM et porte
            value_col = None
            for col in df.columns:
                if 'Value' in col:
                    value_col = col
                    break
                    
            if value_col and 'CLIM' in file_path.name and 'Etat' in file_path.name:
                # Convertir ON/OFF en 1/0
                df[value_col] = df[value_col].str.upper().map({'ON': 1, 'OFF': 0})
                # Renommer la colonne pour uniformité
                df.rename(columns={value_col: 'Value'}, inplace=True)
                
            elif value_col and 'Porte' in file_path.name:
                # Convertir Ouverte/Fermé en 1/0
                # Handle encoding issues - sometimes é becomes Ã©
                df[value_col] = df[value_col].map({
                    'Ouverte': 1, 'Ouvert': 1, 'OUVERTE': 1, 'OUVERT': 1,
                    'Fermé': 0, 'Fermée': 0, 'FERME': 0, 'FERMEE': 0, 'FERME': 0,
                    'FermÃ©': 0, 'FermÃ©e': 0, 'Fermé': 0  # Handle encoding issues
                })
                
                # Si la conversion a produit des NaN, essayer de nettoyer la chaîne
                if df[value_col].isna().any():
                    df[value_col] = df[value_col].str.strip().str.upper()
                    df[value_col] = df[value_col].map({
                        'OUVERTE': 1, 'OUVERT': 1,
                        'FERME': 0, 'FERMEE': 0, 'FERMÉ': 0, 'FERMÉE': 0
                    })
                
                # Renommer la colonne pour uniformité
                df.rename(columns={value_col: 'Value'}, inplace=True)
                
            elif value_col and 'GE' in file_path.name:
                # Pour le générateur, convertir aussi en 1/0 si nécessaire
                if df[value_col].dtype == 'object':
                    df[value_col] = df[value_col].str.upper().map({'ON': 1, 'OFF': 0})
                # Renommer la colonne pour uniformité
                df.rename(columns={value_col: 'Value'}, inplace=True)
            
            # Convertir les colonnes numériques
            for col in df.columns:
                if 'Value' in col and col != 'Value':  # Ne pas convertir les colonnes de statut
                    # Si c'est une colonne numérique (température ou puissance)
                    if any(unit in col for unit in ['°C', 'kW']):
                        df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Réinitialiser l'index
            df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement de {file_path}: {e}")
            return pd.DataFrame()
    
    def load_all_data(self, region=None, pop=None):
        """Charge et nettoie tous les fichiers de données pour un POP spécifique"""
        # Debug: afficher le chemin complet
        base_path = self.data_dir
        if region and pop:
            base_path = self.data_dir / region / pop
            
        print(f"📂 Chemin de base du dossier data : {self.data_dir}")
        print(f"📂 Chemin complet du POP : {base_path}")
        
        # Vérifier si le dossier existe
        if not base_path.exists():
            print(f"❌ Le dossier n'existe pas : {base_path}")
            return {}
        
        # Lister tous les fichiers dans le dossier
        print("📄 Fichiers trouvés dans le dossier :")
        for file in base_path.glob('*.csv'):
            print(f"   - {file.name}")
            
        data_files = {
            'temp_ambiante': 'Température Ambiante.csv',
            'temp_exterieure': 'Température Extérieure.csv',
            'puissance_clim': 'P.Active CLIM.csv',
            'puissance_generale': 'P.Active Générale.csv',
            'clim_a': 'Etat CLIM A.csv',
            'clim_b': 'Etat CLIM B.csv',
            'clim_c': 'Etat CLIM C.csv',
            'clim_d': 'Etat CLIM D.csv',
            'porte': 'Etat Porte.csv'
        }
        
        cleaned_data = {}
        
        # Si région et POP sont spécifiés, utiliser leur chemin
        base_path = self.data_dir
        if region and pop:
            base_path = self.data_dir / region / pop
            
        for key, filename in data_files.items():
            file_path = base_path / filename
            if file_path.exists():
                print(f"📂 Chargement de {filename}...")
                df = self.load_and_clean_csv(file_path)
                if not df.empty:
                    cleaned_data[key] = df
                    print(f"✅ {filename} chargé avec succès ({len(df)} lignes)")
                    # Debug: afficher les colonnes
                    print(f"   Colonnes: {df.columns.tolist()}")
                else:
                    print(f"⚠️ {filename} est vide après nettoyage")
            else:
                print(f"❌ Fichier non trouvé: {filename}")
                
        return cleaned_data
    
    def calculate_puissance_it(self, cleaned_data):
        """Calcule la Puissance IT = Puissance Générale - Puissance CLIM"""
        if 'puissance_generale' in cleaned_data and 'puissance_clim' in cleaned_data:
            df_gen = cleaned_data['puissance_generale']
            df_clim = cleaned_data['puissance_clim']
            
            # Fusionner sur Timestamp
            merged = pd.merge(
                df_gen[['Timestamp', 'Value (kW)']],
                df_clim[['Timestamp', 'Value (kW)']],
                on='Timestamp',
                how='inner',
                suffixes=('_generale', '_clim')
            )
            
            # Calculer Puissance IT
            merged['Puissance_IT (kW)'] = merged['Value (kW)_generale'] - merged['Value (kW)_clim']
            
            return merged[['Timestamp', 'Puissance_IT (kW)']]
        
        return pd.DataFrame()
    
    def merge_all_data(self, cleaned_data):
        """Fusionne toutes les données sur Timestamp"""
        # Préparer les DataFrames à fusionner
        dfs_to_merge = []
        
        # Température ambiante
        if 'temp_ambiante' in cleaned_data:
            df = cleaned_data['temp_ambiante'][['Timestamp', 'Value (°C)']].copy()
            df.rename(columns={'Value (°C)': 'Temp_Ambiante'}, inplace=True)
            dfs_to_merge.append(df)
        
        # Température extérieure
        if 'temp_exterieure' in cleaned_data:
            df = cleaned_data['temp_exterieure'][['Timestamp', 'Value (°C)']].copy()
            df.rename(columns={'Value (°C)': 'Temp_Exterieure'}, inplace=True)
            dfs_to_merge.append(df)
        
        # Puissance CLIM
        if 'puissance_clim' in cleaned_data:
            df = cleaned_data['puissance_clim'][['Timestamp', 'Value (kW)']].copy()
            df.rename(columns={'Value (kW)': 'Puissance_CLIM'}, inplace=True)
            dfs_to_merge.append(df)
        
        # Puissance Générale
        if 'puissance_generale' in cleaned_data:
            df = cleaned_data['puissance_generale'][['Timestamp', 'Value (kW)']].copy()
            df.rename(columns={'Value (kW)': 'Puissance_Generale'}, inplace=True)
            dfs_to_merge.append(df)
        
        # Calculer et ajouter Puissance IT
        puissance_it = self.calculate_puissance_it(cleaned_data)
        if not puissance_it.empty:
            df = puissance_it.copy()
            df.rename(columns={'Puissance_IT (kW)': 'Puissance_IT'}, inplace=True)
            dfs_to_merge.append(df)
        
        # États CLIM
        for clim in ['clim_a', 'clim_b', 'clim_c', 'clim_d']:
            if clim in cleaned_data:
                # Vérifier les colonnes disponibles
                available_cols = cleaned_data[clim].columns.tolist()
                if 'Value' in available_cols:
                    df = cleaned_data[clim][['Timestamp', 'Value']].copy()
                    clim_name = f"CLIM_{clim[-1].upper()}_Status"
                    df.rename(columns={'Value': clim_name}, inplace=True)
                    dfs_to_merge.append(df)
                else:
                    print(f"⚠️ Colonnes disponibles pour {clim}: {available_cols}")
        
        # État Porte - IMPORTANT: garder tous les événements de porte
        if 'porte' in cleaned_data:
            available_cols = cleaned_data['porte'].columns.tolist()
            if 'Value' in available_cols:
                df = cleaned_data['porte'][['Timestamp', 'Value']].copy()
                # Ne PAS filtrer - garder toutes les lignes avec timestamps valides
                df.rename(columns={'Value': 'Porte_Status'}, inplace=True)
                dfs_to_merge.append(df)
            else:
                print(f"⚠️ Colonnes disponibles pour porte: {available_cols}")
        
        # Fusionner tous les DataFrames
        if dfs_to_merge:
            merged = dfs_to_merge[0]
            for df in dfs_to_merge[1:]:
                merged = pd.merge(merged, df, on='Timestamp', how='outer')
            
            # Trier par Timestamp
            merged = merged.sort_values('Timestamp').reset_index(drop=True)
            
            # Forward-fill pour les données continues (température et puissance)
            continuous_cols = ['Temp_Ambiante', 'Temp_Exterieure', 'Puissance_IT', 
                             'Puissance_CLIM', 'Puissance_Generale']
            for col in continuous_cols:
                if col in merged.columns:
                    # Limiter le forward-fill à 30 minutes (environ 30 lignes si données par minute)
                    merged[col] = merged[col].ffill(limit=30)
            
            # DO NOT forward-fill door status - we need to see actual events for cycle detection
            # Door status should only have values at actual state change events
            if 'Porte_Status' in merged.columns:
                # Just leave the NaN values as they are - they represent times when no door event occurred
                pass
            
            return merged
        
        return pd.DataFrame()


if __name__ == "__main__":
    # Test du système de nettoyage
    cleaner = DataCleaner()
    data = cleaner.load_all_data()
    print(f"\n📊 Nombre total de fichiers chargés: {len(data)}")
    
    # Test de la fusion
    merged_data = cleaner.merge_all_data(data)
    if not merged_data.empty:
        print(f"\n✅ Données fusionnées: {merged_data.shape}")
        print("\nColonnes disponibles:")
        for col in merged_data.columns:
            print(f"  - {col}")