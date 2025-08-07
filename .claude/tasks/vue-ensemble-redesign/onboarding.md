# Vue Ensemble Redesign - Onboarding Document

## Project Overview
BGU-ONE Centre de Données is a data center monitoring dashboard built with Streamlit. It provides real-time monitoring and analysis of various metrics including temperature, power consumption, and equipment status.

### Tech Stack
- **Frontend**: Streamlit (Python web framework)
- **Data Visualization**: Plotly (interactive charts)
- **Data Processing**: Pandas, NumPy
- **File Format**: CSV data files with specific timestamp and status formats

## Current Architecture

### File Structure
```
benguerir-POP/
├── app.py              # Main Streamlit application (27k+ tokens)
├── data_loader.py      # Data cleaning and loading utilities
├── data/               # CSV data files
│   ├── T°C AMBIANTE BGU-ONE.csv
│   ├── T°C EXTERIEURE BGU-ONE.csv
│   ├── P_Active CLIM BGU-ONE.csv
│   ├── P_Active Général BGU-ONE.csv
│   ├── Etat CLIM [A-D] BGU-ONE.csv (4 files)
│   ├── Etat de porte BGU-ONE.csv
│   └── Etat GE BGU-ONE.csv
└── requirements.txt
```

### Data Flow
1. **Data Loading**: `DataCleaner` class in `data_loader.py` handles:
   - CSV file parsing with different delimiters (`;` or `|`)
   - Special header handling for temperature/power files
   - Status filtering (only keeps rows with Status='{ok}')
   - Timestamp standardization and timezone handling
   - Value standardization (ON/OFF → 1/0 for status files)

2. **Data Merging**: All data sources are merged on Timestamp:
   - Temperature data (Ambient & External)
   - Power data (IT, CLIM, General)
   - Status data (CLIM A-D, Door)
   - IT Power is calculated as: General Power - CLIM Power

3. **Data Structure**: The merged DataFrame contains:
   - `Timestamp`: datetime column
   - `Temp_Ambiante`: Ambient temperature in °C
   - `Temp_Exterieure`: External temperature in °C
   - `Puissance_IT`: IT Power in kW (calculated)
   - `Puissance_CLIM`: CLIM Power in kW
   - `Puissance_Generale`: General Power in kW
   - `CLIM_[A-D]_Status`: 1/0 for ON/OFF
   - `Porte_Status`: 1/0 for Open/Closed

## Current Vue d'ensemble Implementation
The current implementation (lines 84-143 in app.py) shows:
1. **4 Main Metrics**: Latest values with delta from mean
   - Température Ambiante
   - Température Extérieure
   - Puissance IT
   - Puissance CLIM

2. **Equipment Status**: Two columns showing:
   - CLIM A-D status (ON/OFF)
   - Door status (Open/Closed)

## Task Requirements
Replace the Vue d'ensemble section with:

### 1. Time Range Selection
- User selects time range for analysis
- This affects all metrics displayed below

### 2. Important Metrics Display (for selected time range)
For each of these three categories, show: min, max, mean, moyenne
- **Temp Ambiante**: min, max, mean, moyenne
- **Temp Extérieur**: min, max, mean, moyenne  
- **Puissance IT**: min, max, mean, moyenne

### 3. Time Series Graph
- Multi-select for data to display
- ALL selected data displayed in ONE unified graph
- Smart color scheme for distinguishing different metrics
- Handle different scales (temperature vs power)
- Interactive (Plotly) for zooming/panning

## Implementation Plan
1. Remove current Vue d'ensemble content
2. Add time range selector (date picker or predefined ranges)
3. Calculate and display metrics for selected range
4. Create unified time series visualization
5. Implement smart scaling/coloring for mixed metric types

## Key Considerations
- **Performance**: Data can be large, use Streamlit caching
- **UX**: Clear visual hierarchy, intuitive controls
- **Scales**: Temperature (°C) and Power (kW) have different ranges
- **Colors**: Need distinct colors for up to 10+ metrics on one graph