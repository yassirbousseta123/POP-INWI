# BGU-ONE Centre de Données - Tableau de Bord

Application de surveillance et d'analyse pour le centre de données BGU-ONE.

## 🚀 Installation

1. Installer les dépendances:
```bash
pip install -r requirements.txt
```

2. Lancer l'application:
```bash
streamlit run app.py
```

## 📊 Fonctionnalités

### 1. Vue d'ensemble
- Métriques en temps réel
- État des équipements (CLIMs et porte)
- Indicateurs de performance

### 2. Analyse temporelle interactive
- Sélection multiple de métriques
- Filtrage par date
- Visualisation superposée ou séparée
- Export PNG/CSV

### 3. Analyses EDA
- Histogrammes avec courbe de densité
- Boîtes à moustaches
- Séries temporelles
- Moyennes journalières
- Profils horaires

### 4. Analyse CLIM
- Impact de l'arrêt des CLIMs sur la température
- Statistiques de changement de température
- Visualisation par événement

### 5. Analyse Porte
- Cycles d'ouverture/fermeture
- Impact sur la température ambiante
- Corrélation durée/température

### 6. Corrélations
- Matrice de corrélation
- Interprétation automatique
- Facteurs influençant la température

### 7. Rapports
- Rapport d'efficacité énergétique
- Calcul du PUE
- Recommandations d'optimisation

## 📁 Structure des données

Les fichiers CSV doivent être placés dans le dossier `/data` avec les noms suivants:
- `T°C AMBIANTE BGU-ONE.csv`
- `T°C EXTERIEURE BGU-ONE.csv`
- `P_Active CLIM BGU-ONE.csv`
- `P_Active Général BGU-ONE.csv`
- `Etat CLIM A/B/C/D BGU-ONE.csv`
- `Etat de porte BGU-ONE.csv`
- `Etat GE BGU-ONE.csv`

## 🛠️ Nettoyage automatique des données

L'application effectue automatiquement:
1. Suppression des colonnes 'Trend Flags'
2. Filtrage des lignes où Status ≠ '{ok}'
3. Validation et standardisation des dates
4. Conversion des statuts (ON/OFF → 1/0)

## 📈 Métriques calculées

- **Puissance IT** = Puissance Générale - Puissance CLIM
- **PUE** = Puissance Générale / Puissance IT
- **Efficacité CLIM** = Puissance CLIM / Puissance IT

