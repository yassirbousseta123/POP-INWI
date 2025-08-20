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
    
    def load_and_clean_csv(self, file_path, encoding='ISO-8859-1'):
        """Charge et nettoie un fichier CSV selon les spécifications"""
        try:
            print(f"\n📄 Traitement du fichier : {file_path.name}")
            
            # Tester différents encodages
            encodings = ['ISO-8859-1', 'utf-8', 'utf-8-sig']
            first_lines = None
            used_encoding = None
            
            # Trouver le bon encodage
            for enc in encodings:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        first_lines = [f.readline() for _ in range(5)]
                    used_encoding = enc
                    break
                except UnicodeDecodeError:
                    continue
            
            if not first_lines:
                print(f"❌ Impossible de lire le fichier")
                return pd.DataFrame()
            
            print(f"   ℹ️ Premières lignes du fichier :")
            for i, line in enumerate(first_lines):
                print(f"   {i+1}: {line.strip()}")
            
            # Déterminer le nombre de lignes à sauter
            skiprows = 0
            for line in first_lines:
                if 'history:' in line or not line.strip():
                    skiprows += 1
                else:
                    break
            
            # Déterminer le vrai délimiteur en analysant le contenu des données
            delimiters = [';', ',', '|', '\t']
            content_sample = ''.join(first_lines[skiprows:])  # Ignorer les lignes d'en-tête
            delimiter_counts = {d: content_sample.count(d) for d in delimiters}
            delimiter = max(delimiter_counts.items(), key=lambda x: x[1])[0]
            print(f"   📊 Délimiteur détecté : '{delimiter}' (occurrences : {delimiter_counts})")
            
            # Déterminer le format en fonction du nom de fichier
            if 'Température' in file_path.name:
                value_col = 'Value (°C)'
            elif 'P.Active' in file_path.name:
                value_col = 'Value (kW)'
            else:
                value_col = 'Value'
            
            # Lire le fichier CSV
            try:
                df = pd.read_csv(
                    file_path,
                    delimiter=delimiter,
                    skiprows=skiprows,
                    encoding=used_encoding,
                    on_bad_lines='skip'
                )
            except Exception as e:
                print(f"   ⚠️ Erreur lors de la première tentative : {str(e)}")
                # Deuxième tentative sans skiprows
                df = pd.read_csv(
                    file_path,
                    delimiter=delimiter,
                    encoding=used_encoding,
                    on_bad_lines='skip'
                )
            
            # Nettoyer les noms de colonnes
            df.columns = df.columns.str.strip()
            df.columns = [col.replace('\ufeff', '').replace('ï»¿', '') for col in df.columns]
            print(f"   📊 Colonnes : {df.columns.tolist()}")
            
            # Standardiser les noms de colonnes
            std_columns = {
                'Value (°C)': value_col,
                'Value(°C)': value_col,
                'Value (kW)': value_col,
                'Value(kW)': value_col,
                'Value': value_col
            }
            df = df.rename(columns=std_columns)
            
            # Supprimer Trend Flags si présent
            if 'Trend Flags' in df.columns:
                df = df.drop(columns=['Trend Flags'])
            
            # Filtrer les statuts
            if 'Status' in df.columns:
                df['Status'] = df['Status'].astype(str)
                df = df[df['Status'].str.lower().str.contains('{ok}')]
            
            # Gérer les dates
            if 'Timestamp' in df.columns:
                df['Timestamp'] = (
                    df['Timestamp']
                    .astype(str)
                    .str.replace(r'\s+(WEST|WET|GMT|UTC|CET|CEST)$', '', regex=True)
                )
                df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                df = df.dropna(subset=['Timestamp'])
            
            # Standardiser les valeurs
            if value_col in df.columns:
                if 'CLIM' in file_path.name and 'Etat' in file_path.name:
                    df[value_col] = df[value_col].astype(str).str.upper()
                    df[value_col] = df[value_col].map({'ON': 1, 'OFF': 0})
                elif 'Porte' in file_path.name:
                    df[value_col] = df[value_col].astype(str).str.upper()
                    df[value_col] = df[value_col].replace({
                        'OUVERTE': 1, 'OUVERT': 1,
                        'FERMÉ': 0, 'FERMÉE': 0, 'FERME': 0, 'FERMEE': 0,
                        'FERMÃ©': 0, 'FERMÃ‰': 0
                    })
                else:
                    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
            
            # Réinitialiser l'index
            df = df.reset_index(drop=True)
            print(f"✅ Fichier chargé avec succès ({len(df)} lignes)")
            return df
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement de {file_path}: {str(e)}")
            return pd.DataFrame()
    
    def load_all_data(self, region=None, pop=None):
        """Charge et nettoie tous les fichiers de données pour un POP spécifique"""
        # Debug: afficher le chemin complet
        base_path = self.data_dir
        if region and pop:
            base_path = self.data_dir / region / pop
        print(f"📂 Chemin de base du dossier data : {self.data_dir}")
        print(f"📂 Chemin complet du POP : {base_path}")
            
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
        
        # Lister tous les fichiers dans le dossier
        print("📄 Fichiers trouvés dans le dossier :")
        for file in base_path.glob('*.csv'):
            print(f"   - {file.name}")
        
        cleaned_data = {}
        for key, filename in data_files.items():
            file_path = base_path / filename
            if file_path.exists():
                print(f"📂 Chargement de {filename}...")
                df = self.load_and_clean_csv(file_path)
                if not df.empty:
                    cleaned_data[key] = df
                    print(f"   Colonnes: {df.columns.tolist()}")
                else:
                    print(f"⚠️ {filename} est vide après nettoyage")
            else:
                print(f"❌ Fichier non trouvé: {filename}")
        
        return cleaned_data
    
    def merge_all_data(self, cleaned_data):
        """Fusionne toutes les données sur Timestamp"""
        if not cleaned_data:
            return pd.DataFrame()
        
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
        
        # États CLIM
        for clim in ['clim_a', 'clim_b', 'clim_c', 'clim_d']:
            if clim in cleaned_data:
                df = cleaned_data[clim][['Timestamp', 'Value']].copy()
                clim_name = f"CLIM_{clim[-1].upper()}_Status"
                df.rename(columns={'Value': clim_name}, inplace=True)
                dfs_to_merge.append(df)
        
        # État Porte
        if 'porte' in cleaned_data:
            df = cleaned_data['porte'][['Timestamp', 'Value']].copy()
            df.rename(columns={'Value': 'Porte_Status'}, inplace=True)
            dfs_to_merge.append(df)
        
        # Fusionner tous les DataFrames
        if dfs_to_merge:
            merged = dfs_to_merge[0]
            for df in dfs_to_merge[1:]:
                merged = pd.merge(merged, df, on='Timestamp', how='outer')
            
            # Trier par Timestamp
            merged = merged.sort_values('Timestamp').reset_index(drop=True)
            
            # Forward-fill pour les données continues
            continuous_cols = ['Temp_Ambiante', 'Temp_Exterieure', 'Puissance_CLIM', 'Puissance_Generale']
            for col in continuous_cols:
                if col in merged.columns:
                    merged[col] = merged[col].ffill(limit=30)
            
            return merged
        
        return pd.DataFrame()
