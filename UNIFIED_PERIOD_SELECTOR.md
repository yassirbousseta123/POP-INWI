# Unified Period Selector - Implementation Guide

## Overview
A unified period selector has been implemented for the BGU-ONE POP Incident Management System. This allows users to select a time period once, and all 9 sections of the application will automatically use the same period for data filtering.

## Key Features

### 1. Global Period Selection
- Located in the sidebar for persistent visibility across all tabs
- Single selection applies to all 9 sections simultaneously
- Predefined periods: Last hour, 24 hours, 3 days, week, month, 3 months
- Custom date range selection available

### 2. Components Added

#### `/src/ui/period_selector.py`
- `UnifiedPeriodSelector` class manages global period state
- Uses Streamlit session state for persistence
- Methods:
  - `render_selector()`: Full UI component
  - `render_mini_selector()`: Compact sidebar version
  - `filter_dataframe()`: Filters any DataFrame by the selected period
  - `get_current_period()`: Returns current period settings
  - `set_period()`: Programmatically set the period

### 3. Integration Points

#### All 9 Tabs Updated:
1. **Vue d'ensemble**: Overview with key metrics
2. **Analyse temporelle**: Temporal analysis
3. **Analyses EDA**: Exploratory data analysis
4. **Analyse CLIM**: CLIM impact analysis
5. **Incident Lens**: Root cause analysis
6. **Analyse Porte**: Door opening impact
7. **Corrélations**: Correlation analysis
8. **Rapports**: Report generation
9. **Simulation Coûts**: Cost simulation

Each tab now:
- Displays the selected period at the top
- Uses `filtered_merged_data` instead of `merged_data`
- No longer has individual date selectors

## Usage

### Running the Application
```bash
streamlit run app.py
```

### Selecting a Period
1. Use the sidebar selector to choose a period
2. All sections automatically update with filtered data
3. Period info is displayed at the top of each section

### API Usage (for developers)
```python
from src.ui.period_selector import period_selector

# Get current period
current = period_selector.get_current_period()
start_date = current['start_date']
end_date = current['end_date']

# Filter a DataFrame
filtered_df = period_selector.filter_dataframe(df, timestamp_column='Timestamp')

# Set period programmatically
period_selector.set_period(start_date, end_date, "Custom")
```

## Benefits
1. **Consistency**: All sections use the same time period
2. **Efficiency**: Select once, apply everywhere
3. **User Experience**: No need to select dates multiple times
4. **Performance**: Data is filtered once and reused across tabs

## Technical Details
- Uses Streamlit session state for persistence
- Period selection persists during the session
- Automatic DataFrame filtering based on timestamp columns
- Compatible with existing data processing pipeline

## Testing
To verify the implementation:
1. Run the application
2. Select a period in the sidebar
3. Navigate through all tabs
4. Verify that each tab shows the same period and filtered data

## Future Enhancements
- Add period presets for specific analysis needs
- Export selected period with reports
- Add period comparison features
- Implement period-based caching for performance