"""
Demo script to show how the Anomaly Analyzer works with the existing app
This can be integrated into the main Streamlit app
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

# Import the existing data loader and new anomaly analyzer
from data_loader import DataCleaner
from src.analysis.anomaly_analyzer import AnomalyAnalyzer
from src.ui.anomaly_explorer import render_anomaly_explorer_section

# Page config
st.set_page_config(
    page_title="BGU-ONE - Explorateur d'Anomalies",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 BGU-ONE - Explorateur d'Anomalies avec Analyse des Causes Racines")

# Load data using existing data loader
@st.cache_data
def load_data():
    """Load data using the existing DataCleaner"""
    try:
        cleaner = DataCleaner()
        cleaned_data = cleaner.load_all_data()
        merged_data = cleaner.merge_all_data(cleaned_data)
        return merged_data
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return pd.DataFrame()

# Load the data
data = load_data()

if not data.empty:
    # Render the anomaly explorer section
    render_anomaly_explorer_section(data)
else:
    st.error("Impossible de charger les données. Vérifiez que les fichiers CSV sont présents dans le dossier 'data/'")

# Add documentation
with st.expander("📚 Comment utiliser l'Explorateur d'Anomalies"):
    st.markdown("""
    ### Guide d'utilisation
    
    1. **Configurer la période d'analyse**
       - Sélectionnez les dates de début et fin pour analyser
       
    2. **Définir les seuils de température normale**
       - Température minimale: En dessous = anomalie froide
       - Température maximale: Au dessus = anomalie chaude
       - Les valeurs suggérées sont basées sur vos données historiques
       
    3. **Lancer l'analyse**
       - Le système détecte automatiquement toutes les anomalies
       - Pour chaque anomalie, il analyse ce qui s'est passé avant
       
    4. **Interpréter les résultats**
       - **Confiance %**: Plus c'est élevé, plus la cause est probable
       - **Preuves**: Données factuelles qui supportent chaque cause
       - Les causes sont classées par ordre de probabilité
       
    ### Types de causes détectées
    
    - **CLIM_FAILURE**: Arrêt d'une unité de climatisation
    - **DOOR_OPEN**: Porte restée ouverte  
    - **EXTERNAL_TEMPERATURE**: Influence de la température extérieure
    - **IT_LOAD_INCREASE**: Augmentation de la charge informatique
    - **MULTIPLE_FACTORS**: Combinaison de plusieurs problèmes
    
    ### Exemple de lecture des résultats
    
    ```
    Anomalie détectée: 26.5°C à 14:35
    
    Causes identifiées:
    🟢 CLIM-C s'est arrêté (90% de confiance)
       - CLIM-C était actif puis s'est arrêté
       - Arrêt détecté 10 minutes avant l'anomalie
       - Température a augmenté de 2.5°C
    
    🟡 Porte ouverte pendant 15 minutes (75% de confiance)
       - Porte ouverte 5 min avant l'anomalie
       - Température extérieure: 38°C
    ```
    """)

# Add examples of how to integrate into existing app
with st.expander("💻 Intégration dans l'application existante"):
    st.code("""
# Dans app.py, ajouter après les autres sections:

elif choix_section == "Explorateur d'Anomalies":
    # Import the anomaly explorer
    from src.ui.anomaly_explorer import render_anomaly_explorer_section
    
    # Render the section
    render_anomaly_explorer_section(merged_data)
    """, language="python")
    
    st.markdown("""
    ### Pour intégrer dans votre app.py existant:
    
    1. Copiez les fichiers:
       - `src/analysis/anomaly_analyzer.py`
       - `src/ui/anomaly_explorer.py`
       
    2. Ajoutez l'option au menu dans la sidebar:
       ```python
       "Explorateur d'Anomalies"
       ```
       
    3. Ajoutez la condition pour afficher la section
    
    4. C'est tout! L'explorateur utilisera automatiquement vos données
    """)

# Footer
st.markdown("---")
st.caption("Explorateur d'Anomalies v1.0 - Analyse intelligente des causes racines")