import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import pytz
import traceback

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
        
    def _read_file_header(self, file_path, encoding='ISO-8859-1', num_lines=5):
        """Lit les premières lignes du fichier pour analyse"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                lines = [f.readline().strip() for _ in range(num_lines)]
            return lines
        except Exception:
            return []
            
    def _detect_format(self, lines):
        """Détecte le format du fichier basé sur ses premières lignes"""
        if not lines:
            return None, None, []
        
        header_line = lines[0].replace('ï»¿', '').replace('\ufeff', '')
        data_line = lines[1] if len(lines) > 1 else ""
        
        # L'en-tête utilise généralement des points-virgules
        if ';' in header_line:
            columns = [col.strip() for col in header_line.split(';')]
            # Vérifier le format des données
            if data_line:
                # Si la ligne contient plus de virgules que de points-virgules
                comma_count = data_line.count(',')
                semicolon_count = data_line.count(';')
                if comma_count > semicolon_count and comma_count >= 3:
                    return columns, ',', 1
            return columns, ';', 1
        
        # Essayer de détecter le délimiteur dans les données
        delimiters = [',', ';', '|']
        if data_line:
            counts = {d: data_line.count(d) for d in delimiters}
            if counts:
                best_delimiter = max(counts.items(), key=lambda x: x[1])[0]
                return None, best_delimiter, 0
        
        # Par défaut, utiliser le point-virgule
        return None, ';', 0

    def load_and_clean_csv(self, file_path, encoding='ISO-8859-1'):
        """Charge et nettoie un fichier CSV"""
        try:
            print(f"\n📄 Traitement du fichier : {file_path.name}")
            
            # Essayer différents encodages
            encodings = ['ISO-8859-1', 'utf-8', 'utf-8-sig']
            lines = []
            used_encoding = None
            
            for enc in encodings:
                try:
                    lines = self._read_file_header(file_path, enc)
                    if lines:
                        used_encoding = enc
                        break
                except UnicodeDecodeError:
                    continue
            
            if not lines:
                print("❌ Impossible de lire le fichier avec les encodages standards")
                return pd.DataFrame()
            
            # Afficher les premières lignes pour debug
            print("   ℹ️ Premières lignes du fichier :")
            for i, line in enumerate(lines):
                print(f"   {i+1}: {line}")
            
            # Détecter le format
            columns, delimiter, skiprows = self._detect_format(lines)
            print(f"   📊 Délimiteur détecté : '{delimiter}'")
            # Ne pas prédéfinir le nom de colonne, laisser le CSV déterminer
            # Les colonnes seront automatiquement lues du fichier
            
            # Lecture du fichier selon son format
            try:
                if columns:
                    df = pd.read_csv(
                        file_path,
                        delimiter=delimiter,
                        names=columns,
                        skiprows=skiprows,
                        encoding=used_encoding,
                        on_bad_lines='skip',
                        quoting=1  # Pour gérer les valeurs entre guillemets
                    )
                else:
                    df = pd.read_csv(
                        file_path,
                        delimiter=delimiter,
                        encoding=used_encoding,
                        on_bad_lines='skip',
                        quoting=1
                    )
            except Exception as e:
                print(f"   ❌ Première tentative échouée : {str(e)}")
                try:
                    # Deuxième tentative sans le mode quoting
                    if columns:
                        df = pd.read_csv(
                            file_path,
                            delimiter=delimiter,
                            names=columns,
                            skiprows=skiprows,
                            encoding=used_encoding,
                            on_bad_lines='skip'
                        )
                    else:
                        df = pd.read_csv(
                            file_path,
                            delimiter=delimiter,
                            encoding=used_encoding,
                            on_bad_lines='skip'
                        )
                except Exception as e2:
                    print(f"   ❌ Deuxième tentative échouée : {str(e2)}")
                    return pd.DataFrame()
            
            # Nettoyer les noms de colonnes
            df.columns = df.columns.str.strip()
            df.columns = [col.replace('\ufeff', '').replace('ï»¿', '') for col in df.columns]
            print(f"   📊 Colonnes nettoyées : {df.columns.tolist()}")
            
            # Traitement plus flexible du Status
            if 'Status' in df.columns:
                df['Status'] = df['Status'].astype(str)
                # Garder les lignes qui ne contiennent pas d'erreur explicite
                error_keywords = ['error', 'failure', 'failed', 'invalid']
                mask = ~df['Status'].str.lower().str.contains('|'.join(error_keywords))
                df = df[mask]
            
            # Gérer les dates avec support des fuseaux horaires
            if 'Timestamp' in df.columns:
                # Supprimer les suffixes de fuseau horaire et nettoyer
                df['Timestamp'] = (df['Timestamp']
                    .astype(str)
                    .str.replace(r'\s+(WEST|WET|GMT|UTC|CET|CEST)$', '', regex=True)
                    .str.strip())
                # Convertir en datetime avec gestion des erreurs
                df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
                # Supprimer les lignes avec des dates invalides
                df = df.dropna(subset=['Timestamp'])
            
            # Traiter les valeurs
            for col in df.columns:
                if 'Value' in col:
                    # Convertir en string pour le nettoyage initial
                    df[col] = df[col].astype(str).str.strip()
                    
                    if 'CLIM' in file_path.name and 'Etat' in file_path.name:
                        # Nettoyer et standardiser les valeurs ON/OFF
                        df[col] = df[col].str.upper()
                        on_values = ['ON', 'MARCHE', '1', 'TRUE', 'VRAI']
                        off_values = ['OFF', 'ARRET', 'ARRÊT', '0', 'FALSE', 'FAUX']
                        
                        # Créer le mapping
                        value_map = {v: 1 for v in on_values}
                        value_map.update({v: 0 for v in off_values})
                        df[col] = df[col].map(value_map)
                        
                    elif 'Porte' in file_path.name:
                        df[col] = df[col].str.upper()
                        # Mapping étendu pour les états de porte
                        door_map = {
                            'OUVERTE': 1, 'OUVERT': 1, 'OPEN': 1,
                            'FERMÉ': 0, 'FERMÉE': 0, 'FERME': 0, 'FERMEE': 0,
                            'FERMÃ©': 0, 'FERMÃ‰': 0, 'CLOSED': 0, 'CLOSE': 0,
                            '1': 1, '0': 0, 'TRUE': 1, 'FALSE': 0
                        }
                        df[col] = df[col].map(door_map)
                        
                    elif any(unit in col for unit in ['°C', 'kW']):
                        # Nettoyer les valeurs numériques
                        df[col] = (df[col]
                            .str.replace(',', '.')  # Remplacer la virgule par le point décimal
                            .str.replace(r'[^\d.-]+', '', regex=True)  # Garder uniquement les chiffres, le point et le signe
                        )
                        # Convertir en numérique et gérer les erreurs
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        # Filtrer les valeurs aberrantes pour la température et la puissance
                        if '°C' in col:
                            df.loc[df[col] > 60, col] = np.nan  # Température max 60°C
                            df.loc[df[col] < -10, col] = np.nan  # Température min -10°C
                        elif 'kW' in col:
                            df.loc[df[col] < 0, col] = 0  # Puissance ne peut pas être négative
                        
                    # Vérifier si la colonne est entièrement vide après conversion
                    if df[col].isna().all():
                        print(f"⚠️ La colonne {col} est vide après conversion")
                    else:
                        valid_count = df[col].notna().sum()
                        print(f"✓ {valid_count} valeurs valides dans {col}")
            
            print(f"✅ Fichier chargé avec succès ({len(df)} lignes)")
            return df
            
        except Exception as e:
            print(f"❌ Erreur générale : {str(e)}")
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
    
    def validate_data(self, df, expected_columns=None):
        """Valide la qualité des données chargées"""
        if df.empty:
            print("⚠️ DataFrame vide!")
            return False

        print("\n🔍 Validation des données:")
        
        # Vérifier les colonnes requises
        if expected_columns:
            missing_cols = set(expected_columns) - set(df.columns)
            if missing_cols:
                print(f"⚠️ Colonnes manquantes: {missing_cols}")
                return False
        
        # Vérifier la couverture temporelle
        if 'Timestamp' in df.columns:
            time_range = df['Timestamp'].max() - df['Timestamp'].min()
            expected_rows = time_range.total_seconds() / 900  # Pour 15 minutes d'intervalle
            coverage = len(df) / expected_rows if expected_rows > 0 else 0
            print(f"📊 Couverture temporelle: {coverage:.1%}")
            if coverage < 0.5:  # Moins de 50% de couverture
                print("⚠️ Couverture temporelle insuffisante!")
                return False
        
        # Vérifier les valeurs manquantes par colonne
        for col in df.columns:
            if col == 'Timestamp':
                continue
            null_pct = df[col].isna().mean() * 100
            if null_pct > 50:  # Plus de 50% de valeurs manquantes
                print(f"⚠️ {col}: {null_pct:.1f}% valeurs manquantes")
                return False
            elif null_pct > 0:
                print(f"ℹ️ {col}: {null_pct:.1f}% valeurs manquantes")
        
        print("✅ Validation réussie")
        return True
        
    def merge_all_data(self, cleaned_data):
        """Fusionne toutes les données sur Timestamp"""
        if not cleaned_data:
            return pd.DataFrame()
        
        dfs_to_merge = []
        
        # Fonction helper pour trouver la colonne de valeur
        def find_value_column(df):
            value_cols = [col for col in df.columns 
                         if any(x in col.lower() for x in ['value', 'valeur']) and 
                            any(x in col for x in ['°C', 'kW', 'Â°C'])]
            if not value_cols:
                # Fallback to any column with 'Value' in the name
                value_cols = [col for col in df.columns if 'Value' in col]
            return value_cols[0] if value_cols else None
        
        # Température ambiante
        if 'temp_ambiante' in cleaned_data:
            df = cleaned_data['temp_ambiante'].copy()
            value_col = find_value_column(df)
            if value_col and 'Timestamp' in df.columns:
                df = df[['Timestamp', value_col]]
                df.rename(columns={value_col: 'Temp_Ambiante'}, inplace=True)
                dfs_to_merge.append(df)
        
        # Température extérieure
        if 'temp_exterieure' in cleaned_data:
            df = cleaned_data['temp_exterieure'].copy()
            value_col = find_value_column(df)
            if value_col and 'Timestamp' in df.columns:
                df = df[['Timestamp', value_col]]
                df.rename(columns={value_col: 'Temp_Exterieure'}, inplace=True)
                dfs_to_merge.append(df)
        
        # Traitement des puissances et calcul de la Puissance IT
        if 'puissance_generale' in cleaned_data and 'puissance_clim' in cleaned_data:
            # Préparer les DataFrames de puissance
            df_gen = cleaned_data['puissance_generale'].copy()
            df_clim = cleaned_data['puissance_clim'].copy()
            
            value_col_gen = find_value_column(df_gen)
            value_col_clim = find_value_column(df_clim)
            
            if value_col_gen and value_col_clim and 'Timestamp' in df_gen.columns:
                # Préparer DataFrame de puissance générale
                df_gen = df_gen[['Timestamp', value_col_gen]]
                df_gen.rename(columns={value_col_gen: 'Puissance_Generale'}, inplace=True)
                
                # Préparer DataFrame de puissance CLIM
                df_clim = df_clim[['Timestamp', value_col_clim]]
                df_clim.rename(columns={value_col_clim: 'Puissance_CLIM'}, inplace=True)
                
                # Fusionner les données de puissance
                puissance_df = pd.merge(df_gen, df_clim, on='Timestamp', how='outer')
                
                # Convertir en numérique et gérer les valeurs manquantes
                puissance_df['Puissance_Generale'] = pd.to_numeric(puissance_df['Puissance_Generale'], errors='coerce')
                puissance_df['Puissance_CLIM'] = pd.to_numeric(puissance_df['Puissance_CLIM'], errors='coerce')
                
                # Calculer la Puissance IT
                puissance_df['Puissance_IT'] = puissance_df['Puissance_Generale'] - puissance_df['Puissance_CLIM']
                
                # Nettoyer les valeurs aberrantes
                puissance_df.loc[puissance_df['Puissance_IT'] < 0, 'Puissance_IT'] = 0
                
                # Ajouter les colonnes de puissance au DataFrame à fusionner (une seule fois)
                dfs_to_merge.append(puissance_df[['Timestamp', 'Puissance_Generale', 'Puissance_CLIM', 'Puissance_IT']])
                
                # Afficher les statistiques
                valid_data = puissance_df['Puissance_IT'].notna().sum()
                if valid_data > 0:
                    print(f"\n✅ Puissance IT calculée avec succès:")
                    print(f"   - {valid_data} points de données valides")
                    print(f"   - Min: {puissance_df['Puissance_IT'].min():.2f} kW")
                    print(f"   - Max: {puissance_df['Puissance_IT'].max():.2f} kW")
                    print(f"   - Moyenne: {puissance_df['Puissance_IT'].mean():.2f} kW")
        elif 'puissance_generale' in cleaned_data:
            # Si on a seulement puissance générale (sans CLIM)
            df = cleaned_data['puissance_generale'].copy()
            value_col = find_value_column(df)
            if value_col and 'Timestamp' in df.columns:
                df = df[['Timestamp', value_col]]
                df.rename(columns={value_col: 'Puissance_Generale'}, inplace=True)
                dfs_to_merge.append(df)
        elif 'puissance_clim' in cleaned_data:
            # Si on a seulement puissance CLIM (sans générale)
            df = cleaned_data['puissance_clim'].copy()
            value_col = find_value_column(df)
            if value_col and 'Timestamp' in df.columns:
                df = df[['Timestamp', value_col]]
                df.rename(columns={value_col: 'Puissance_CLIM'}, inplace=True)
                dfs_to_merge.append(df)
        
        # États CLIM
        for clim in ['clim_a', 'clim_b', 'clim_c', 'clim_d']:
            if clim in cleaned_data:
                df = cleaned_data[clim].copy()
                value_col = find_value_column(df)
                if value_col and 'Timestamp' in df.columns:
                    df = df[['Timestamp', value_col]]
                    df.rename(columns={value_col: f"CLIM_{clim[-1].upper()}_Status"}, inplace=True)
                    dfs_to_merge.append(df)
        
        # État Porte
        if 'porte' in cleaned_data:
            df = cleaned_data['porte'].copy()
            value_col = find_value_column(df)
            if value_col and 'Timestamp' in df.columns:
                df = df[['Timestamp', value_col]]
                df.rename(columns={value_col: 'Porte_Status'}, inplace=True)
                dfs_to_merge.append(df)
        
        # Fusionner tous les DataFrames
        if dfs_to_merge:
            try:
                print("\n🔄 Fusion des données...")
                # Afficher un aperçu des DataFrames avant la fusion
                for i, df in enumerate(dfs_to_merge):
                    print(f"\nDataFrame {i+1}:")
                    print(f"Colonnes: {df.columns.tolist()}")
                    print(f"Période: {df['Timestamp'].min()} à {df['Timestamp'].max()}")
                    print(f"Nombre de lignes: {len(df)}")
                
                # Fusion progressive avec vérification
                merged = dfs_to_merge[0]
                for i, df in enumerate(dfs_to_merge[1:], 1):
                    before_merge = len(merged)
                    merged = pd.merge(merged, df, on='Timestamp', how='outer')
                    after_merge = len(merged)
                    
                    print(f"\nFusion {i}: {before_merge} → {after_merge} lignes")
                    if after_merge == 0:
                        print("⚠️ La fusion a résulté en 0 lignes!")
                        # Vérifier les plages de dates
                        print(f"Plage de dates du DataFrame principal: {merged['Timestamp'].min()} à {merged['Timestamp'].max()}")
                        print(f"Plage de dates du DataFrame à fusionner: {df['Timestamp'].min()} à {df['Timestamp'].max()}")
                
                # Trier par Timestamp
                merged = merged.sort_values('Timestamp').reset_index(drop=True)
                
                # Forward-fill pour les données continues
                continuous_cols = ['Temp_Ambiante', 'Temp_Exterieure', 
                                 'Puissance_CLIM', 'Puissance_Generale', 'Puissance_IT']
                for col in continuous_cols:
                    if col in merged.columns:
                        nulls_before = merged[col].isna().sum()
                        merged[col] = merged[col].ffill(limit=30)
                        nulls_after = merged[col].isna().sum()
                        if nulls_before - nulls_after > 0:
                            print(f"\n{col}: {nulls_before - nulls_after} valeurs comblées")
                
                # Vérification finale
                print("\n✅ Fusion terminée")
                print(f"Nombre total de lignes: {len(merged)}")
                print(f"Période couverte: {merged['Timestamp'].min()} à {merged['Timestamp'].max()}")
                print("Colonnes disponibles:")
                for col in merged.columns:
                    non_null = merged[col].notna().sum()
                    print(f"- {col}: {non_null} valeurs non-null ({non_null/len(merged)*100:.1f}%)")
                
                return merged
                
            except Exception as e:
                print(f"\n❌ Erreur lors de la fusion: {str(e)}")
                print("Détails de l'erreur:")
                import traceback
                print(traceback.format_exc())
                return pd.DataFrame()
        
        return pd.DataFrame()
    
    def load_multiple_pops(self, pop_list=None, regions=None):
        """
        Charge les données pour plusieurs POPs à la fois
        
        Args:
            pop_list: Liste de tuples (region, pop) à charger
            regions: Liste de régions - charge tous les POPs de ces régions
        
        Returns:
            Dict avec clé (region, pop) et valeur les données fusionnées
        """
        all_pops_data = {}
        
        # Si des régions sont spécifiées, obtenir tous les POPs de ces régions
        if regions:
            pop_list = []
            for region in regions:
                pops = self.get_pops(region)
                for pop in pops:
                    pop_list.append((region, pop))
        
        # Si aucune liste n'est fournie, charger TOUS les POPs
        if not pop_list:
            pop_list = []
            for region in self.get_regions():
                pops = self.get_pops(region)
                for pop in pops:
                    pop_list.append((region, pop))
        
        print(f"\n🔄 Chargement de {len(pop_list)} POPs...")
        
        for region, pop in pop_list:
            print(f"\n📍 Traitement de {region}/{pop}...")
            try:
                # Charger les données du POP
                cleaned_data = self.load_all_data(region=region, pop=pop)
                
                if cleaned_data:
                    # Fusionner les données
                    merged_data = self.merge_all_data(cleaned_data)
                    
                    if not merged_data.empty:
                        # Ajouter les métadonnées du POP
                        merged_data['Region'] = region
                        merged_data['POP'] = pop
                        merged_data['POP_ID'] = f"{region}_{pop}"
                        
                        all_pops_data[(region, pop)] = merged_data
                        print(f"✅ {region}/{pop}: {len(merged_data)} lignes chargées")
                    else:
                        print(f"⚠️ {region}/{pop}: Données vides après fusion")
                else:
                    print(f"⚠️ {region}/{pop}: Aucune donnée trouvée")
                    
            except Exception as e:
                print(f"❌ Erreur lors du chargement de {region}/{pop}: {str(e)}")
                continue
        
        print(f"\n✅ {len(all_pops_data)} POPs chargés avec succès sur {len(pop_list)}")
        return all_pops_data
    
    def calculate_pop_correlations(self, all_pops_data, metric='Temp_Ambiante', period=None):
        """
        Calcule les corrélations entre un métrique donné et d'autres métriques pour tous les POPs
        
        Args:
            all_pops_data: Dict avec les données de tous les POPs
            metric: Métrique principal pour la corrélation (défaut: Temp_Ambiante)
            period: Tuple (start_date, end_date) pour filtrer la période
        
        Returns:
            DataFrame avec les corrélations pour chaque POP
        """
        correlation_results = []
        
        # Liste des métriques à corréler avec la métrique principale
        correlation_metrics = ['Temp_Exterieure', 'Puissance_IT', 'Puissance_CLIM', 
                              'CLIM_A_Status', 'CLIM_B_Status', 'CLIM_C_Status', 
                              'CLIM_D_Status', 'Porte_Status']
        
        for (region, pop), data in all_pops_data.items():
            # Filtrer par période si spécifiée
            if period and 'Timestamp' in data.columns:
                start_date, end_date = period
                mask = (data['Timestamp'] >= start_date) & (data['Timestamp'] <= end_date)
                data = data[mask]
            
            if len(data) < 10:  # Besoin d'au moins 10 points
                continue
            
            # Vérifier que la métrique principale existe
            if metric not in data.columns:
                continue
            
            # Calculer les corrélations
            pop_correlations = {
                'Region': region,
                'POP': pop,
                'POP_ID': f"{region}_{pop}",
                'Data_Points': len(data),
                'Period_Start': data['Timestamp'].min() if 'Timestamp' in data.columns else None,
                'Period_End': data['Timestamp'].max() if 'Timestamp' in data.columns else None
            }
            
            # Calculer la corrélation avec chaque métrique
            for corr_metric in correlation_metrics:
                if corr_metric in data.columns:
                    # Préparer les données pour la corrélation
                    corr_data = data[[metric, corr_metric]].dropna()
                    
                    if len(corr_data) >= 10:
                        # Convertir les colonnes de statut en numérique si nécessaire
                        if corr_metric == 'Porte_Status' and corr_data[corr_metric].dtype == 'object':
                            corr_data[corr_metric] = corr_data[corr_metric].map({
                                'Open': 1, 'Ouvert': 1, 'open': 1, '1': 1, 1: 1,
                                'Close': 0, 'Fermé': 0, 'closed': 0, '0': 0, 0: 0
                            })
                        
                        if 'CLIM' in corr_metric and 'Status' in corr_metric:
                            if corr_data[corr_metric].dtype == 'object':
                                corr_data[corr_metric] = corr_data[corr_metric].map({
                                    'ON': 1, 'on': 1, 'On': 1, '1': 1, 1: 1,
                                    'OFF': 0, 'off': 0, 'Off': 0, '0': 0, 0: 0
                                })
                        
                        # Calculer les corrélations
                        try:
                            pearson_corr = corr_data[metric].corr(corr_data[corr_metric], method='pearson')
                            spearman_corr = corr_data[metric].corr(corr_data[corr_metric], method='spearman')
                            
                            pop_correlations[f'{corr_metric}_Pearson'] = pearson_corr
                            pop_correlations[f'{corr_metric}_Spearman'] = spearman_corr
                            pop_correlations[f'{corr_metric}_Count'] = len(corr_data)
                        except:
                            pop_correlations[f'{corr_metric}_Pearson'] = None
                            pop_correlations[f'{corr_metric}_Spearman'] = None
                            pop_correlations[f'{corr_metric}_Count'] = 0
                    else:
                        pop_correlations[f'{corr_metric}_Pearson'] = None
                        pop_correlations[f'{corr_metric}_Spearman'] = None
                        pop_correlations[f'{corr_metric}_Count'] = 0
                else:
                    pop_correlations[f'{corr_metric}_Pearson'] = None
                    pop_correlations[f'{corr_metric}_Spearman'] = None
                    pop_correlations[f'{corr_metric}_Count'] = 0
            
            # Calculer aussi les statistiques de base pour la métrique principale
            pop_correlations[f'{metric}_Mean'] = data[metric].mean()
            pop_correlations[f'{metric}_Std'] = data[metric].std()
            pop_correlations[f'{metric}_Min'] = data[metric].min()
            pop_correlations[f'{metric}_Max'] = data[metric].max()
            
            correlation_results.append(pop_correlations)
        
        # Créer un DataFrame avec tous les résultats
        if correlation_results:
            return pd.DataFrame(correlation_results)
        else:
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