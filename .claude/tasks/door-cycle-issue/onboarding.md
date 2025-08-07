# Door Cycle Issue Onboarding

## Problem Description
In the "Analyse Porte" section of the application, the number of cycles shows as 1 but this is clearly incorrect. The system should detect multiple door open/close cycles.

## Project Overview
This is a Streamlit application for analyzing temperature, power consumption, and door status data for a data center (BGU-ONE). The app has multiple sections including door analysis ("Analyse Porte").

## Key Files
- `app.py`: Main Streamlit application (line 1377-1730 contains the door analysis section)
- `data_loader.py`: Handles data loading and preprocessing
- `data/Etat de porte BGU-ONE.csv`: Contains door status data with timestamps

## Data Format
The door status CSV contains:
- Timestamp: Date/time in format "DD-MMM-YY H:MM:SS AM/PM WEST"
- Status: Usually "{ok}"
- Value: "Fermé" (closed) or "Ouverte" (open)

## Current Implementation

### Data Processing (data_loader.py)
1. Door status values are converted: "Fermé" → 0, "Ouverte" → 1
2. Forward-fill is applied to maintain state between events
3. NaN values are filled with 0 (closed)

### Cycle Detection (app.py:1415-1425)
1. Door open events: detected when status changes from 0 → 1
2. Door close events: detected when status changes from 1 → 0
3. For each open event, finds the next close event to form a cycle

## Investigation Findings

### Raw Data Analysis
From the door status file, I can see these events:
- 16-Jan-25 11:38:53 AM: Ouverte (Open)
- 16-Jan-25 11:40:44 AM: Fermé (Closed) → Cycle 1
- 16-Jan-25 11:50:07 AM: Ouverte (Open)
- 16-Jan-25 2:36:42 PM: Fermé (Closed) → Cycle 2
- 20-Jan-25 1:00:09 PM: Ouverte (Open)
- 20-Jan-25 1:01:36 PM: Fermé (Closed) → Cycle 3

So there should be at least 3 cycles in the data.

## Suspected Issues

1. **Event Detection Logic**: The current logic uses `.shift(1)` to detect transitions:
   ```python
   porte_data['Door_Open'] = (porte_data['Porte_Status'].shift(1) == 0) & (porte_data['Porte_Status'] == 1)
   ```
   This might miss events if there are gaps in the data.

2. **Data Sparsity**: The door status data is very sparse - only recording when state changes occur, not continuous monitoring. The forward-fill might be creating issues.

3. **Filtering Issues**: After detecting events, the code might be filtering out valid cycles due to temperature data availability or other conditions.

## Next Steps
1. Add debugging output to see how many open/close events are detected
2. Check if the forward-fill is working correctly
3. Verify that temperature data is available during door events
4. Review the cycle validation logic that might be discarding valid cycles