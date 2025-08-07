#!/usr/bin/env python3
import pandas as pd
from datetime import datetime, timedelta

def detect_door_cycles(df, ts_col='Timestamp', status_col='Value', min_duration_sec=0, max_duration_hours=24, assume_close_at_end=True):
    """
    Détecte les cycles d'ouverture/fermeture de porte.
    Approche simple: chaque "Ouverte" est appariée avec le prochain "Fermé".
    """
    # Copie pour éviter de modifier l'original
    df_proc = df.copy()
    
    # 1. Sort by timestamp
    df_proc = df_proc.sort_values(ts_col).reset_index(drop=True)
    
    # 2. Convertir le statut en valeur numérique (1=ouvert, 0=fermé)
    if pd.api.types.is_string_dtype(df_proc[status_col]):
        # Gérer les statuts textuels en français
        clean_status = df_proc[status_col].str.strip().str.lower()
        status_map = {
            'ouverte': 1, 
            'ouvert': 1, 
            'fermé': 0, 
            'ferme': 0,
            'fermée': 0
        }
        df_proc['state'] = clean_status.map(status_map)
        df_proc['state'] = df_proc['state'].fillna(0)
    else:
        # Gérer les données numériques
        df_proc['state'] = pd.to_numeric(df_proc[status_col], errors='coerce').fillna(0)
    
    df_proc['state'] = df_proc['state'].astype(int)
    
    # 3. Algorithme simple: parcourir et apparier
    cycles_list = []
    i = 0
    
    print(f"Total records: {len(df_proc)}")
    print("\nScanning for cycles...")
    
    while i < len(df_proc):
        # Chercher une ouverture
        if df_proc.iloc[i]['state'] == 1:
            open_time = df_proc.iloc[i][ts_col]
            open_idx = i
            
            print(f"\nFound OPEN at index {i}: {open_time} - {df_proc.iloc[i][status_col]}")
            
            # Chercher la prochaine fermeture
            close_time = None
            close_idx = None
            
            for j in range(i + 1, len(df_proc)):
                if df_proc.iloc[j]['state'] == 0:
                    close_time = df_proc.iloc[j][ts_col]
                    close_idx = j
                    print(f"  Found CLOSE at index {j}: {close_time} - {df_proc.iloc[j][status_col]}")
                    break
            
            # Si pas de fermeture trouvée
            if close_time is None:
                print(f"  No CLOSE found for this OPEN")
                if assume_close_at_end:
                    # Utiliser le dernier timestamp + 30 min ou la durée max
                    last_time = df_proc.iloc[-1][ts_col]
                    duration_to_last = (last_time - open_time).total_seconds()
                    
                    if duration_to_last > max_duration_hours * 3600:
                        close_time = open_time + timedelta(hours=max_duration_hours)
                    else:
                        close_time = last_time + timedelta(minutes=30)
                    print(f"  Assumed CLOSE at: {close_time}")
                else:
                    # Ignorer ce cycle incomplet
                    i += 1
                    continue
            
            # Calculer la durée
            duration_sec = (close_time - open_time).total_seconds()
            
            # Ajouter le cycle si la durée est valide
            if duration_sec >= min_duration_sec:
                cycles_list.append({
                    'open_ts': open_time,
                    'close_ts': close_time,
                    'duration_sec': duration_sec
                })
                print(f"  ✓ Cycle added: duration = {duration_sec/60:.1f} min")
            else:
                print(f"  ✗ Cycle skipped: duration = {duration_sec:.1f} sec < {min_duration_sec} sec")
            
            # Continuer après la fermeture trouvée
            if close_idx is not None:
                i = close_idx + 1
            else:
                i += 1
        else:
            i += 1
    
    # 4. Créer le DataFrame des cycles
    cycles_df = pd.DataFrame(cycles_list)
    
    if len(cycles_df) == 0:
        cycles_df = pd.DataFrame(columns=['open_ts', 'close_ts', 'duration_sec'])
    
    print(f"\n[RESULT] Total cycles found: {len(cycles_df)}")
    
    return cycles_df

# Test avec les données réelles
print("Loading door data...")
df = pd.read_csv('/Users/boussetayassir/Desktop/benguerir-POP/data/Etat de porte BGU-ONE.csv', 
                 delimiter=';', 
                 encoding='utf-8-sig')

print(f"Loaded {len(df)} rows")
print(f"Columns: {df.columns.tolist()}")

# Convertir les timestamps - le format est DD-Mon-YY H:M:S AM/PM TZ
df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d-%b-%y %I:%M:%S %p %Z', errors='coerce')

# Pour les timestamps qui n'ont pas pu être convertis (différents timezone), essayer sans TZ
mask = df['Timestamp'].isna()
if mask.any():
    # Enlever le timezone et réessayer
    df.loc[mask, 'Timestamp'] = pd.to_datetime(
        df.loc[mask, 'Timestamp'].astype(str).str.replace(' WEST', '').str.replace(' WET', ''), 
        format='%d-%b-%y %I:%M:%S %p', 
        errors='coerce'
    )

# Afficher les premières lignes
print("\nFirst 10 rows of data:")
print(df[['Timestamp', 'Value']].head(10))

# Détecter les cycles
print("\n" + "="*80)
print("DETECTING CYCLES")
print("="*80)

cycles = detect_door_cycles(df, ts_col='Timestamp', status_col='Value', min_duration_sec=0)

# Afficher les résultats
print("\n" + "="*80)
print("FINAL RESULTS")
print("="*80)
print(f"Total cycles detected: {len(cycles)}")

if len(cycles) > 0:
    print("\nFirst 10 cycles:")
    for i, row in cycles.head(10).iterrows():
        print(f"Cycle {i+1}: {row['open_ts']} → {row['close_ts']} (duration: {row['duration_sec']/60:.1f} min)")
    
    print("\nCycle duration statistics:")
    print(f"- Mean: {cycles['duration_sec'].mean()/60:.1f} min")
    print(f"- Median: {cycles['duration_sec'].median()/60:.1f} min")
    print(f"- Min: {cycles['duration_sec'].min()/60:.1f} min")
    print(f"- Max: {cycles['duration_sec'].max()/60:.1f} min")