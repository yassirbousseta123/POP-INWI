# Door Cycle Detection Fix - Onboarding Document

## Task Overview
**Issue**: The "Analyse porte" section doesn't detect cycles correctly. The user reports there should be more than 50 cycles, but the system isn't detecting them all.

## Current Understanding

### 1. Project Structure
- **Main Application**: `app.py` - Streamlit application with multiple analysis sections
- **Data Loader**: `data_loader.py` - Handles CSV data loading and cleaning
- **Data Directory**: Contains various CSV files with CLIM, temperature, and door status data

### 2. Door Data Structure
The door status data (`Etat de porte BGU-ONE.csv`) contains:
- Discrete events (not continuous monitoring)
- States: "Ouverte" (open) or "Fermé" (closed)
- Format: `Timestamp;Trend Flags;Status;Value`
- **Confirmed**: 53 "Ouverte" events in the data (matching user's claim of 50+ cycles)
- Total 127 lines in the file

### 3. Current Implementation Analysis

#### Data Processing Pipeline:
1. **Data Loading** (`data_loader.py`):
   - Lines 99-106: Converts door status text to numeric (Ouverte→1, Fermé→0)
   - Lines 264-275: Forward-fills door status to maintain state between events
   - This creates continuous data from discrete events

2. **Cycle Detection** (`app.py`, starting line 1376):
   - Lines 1434-1435: Filters for non-NaN door status values
   - Lines 1438-1439: Separates open (1) and close (0) events
   - Lines 1477-1553: Main cycle creation loop
   
#### Identified Issues:
1. **Data Filtering**: The code filters for non-NaN values after forward-filling, which might miss some transitions
2. **Cycle Matching Logic**: For each open event, it looks for the next close event. If not found, it uses a 30-minute default window
3. **Data Loss Points**:
   - Cycles without temperature data are discarded (line 1553)
   - Cycles with invalid temperatures are discarded (line 1551)
   - Cycles without matching close events use artificial 30-min window

### 4. Root Cause Analysis
The cycle detection appears to be working correctly at the event detection level (finding 53 open events), but cycles are being filtered out during the temperature analysis phase. This suggests:
- Temperature data might not be available for all time periods
- The 15-minute "before" window for temperature reference might not have data
- Some cycles might be too short or have missing temperature readings

### 5. Next Steps
1. Add detailed debugging to understand why cycles are being filtered
2. Check temperature data availability around door events
3. Consider adjusting the temperature window requirements
4. Implement a more robust cycle detection that doesn't require perfect temperature data

## Key Code Locations
- Door cycle analysis: `app.py:1376-1700`
- Door data loading: `data_loader.py:99-106, 237-244`
- Door status forward-filling: `data_loader.py:264-275`
- Cycle creation loop: `app.py:1477-1553`

## Questions to Investigate
1. How many cycles are lost due to missing temperature data?
2. Are door events clustered in time periods without temperature monitoring?
3. Should we relax the temperature data requirements for cycle detection?