# EDA Reorganization - Onboarding Document

## Task Overview
The client has provided feedback that the "ANALYSES EDA" section requires too many button clicks to display different data visualizations. They want all graphs related to each data type displayed on a single page, similar to how the CLIM and Puissance IT sections are organized.

## Current Implementation Analysis

### EDA Section Structure (Current)
The EDA section currently has a dropdown menu with 7 subsections:
1. **Info datasets** - Dataset information and statistics
2. **Statistiques descriptives** - Descriptive statistics with distribution graphs
3. **Histogrammes** - Histogram visualizations
4. **Boîtes à moustaches** - Box plot visualizations
5. **Séries temporelles** - Time series graphs
6. **Moyennes journalières** - Daily averages
7. **Profils horaires** - Hourly profiles

**Problem**: Users must:
- Select a subsection from dropdown
- Select a metric
- Click buttons to see each visualization
- Repeat for each analysis type

### Reference Implementation: CLIM Section
The CLIM section (lines 1020-1226) shows a better approach:
- All relevant analyses on one page
- Multiple visualizations displayed simultaneously
- No excessive clicking required
- Includes:
  - CLIM status summary table
  - Temperature evolution after CLIM stops
  - Temperature comparison (CLIM ON vs OFF)
  - Correlation matrix
  - All displayed together

### Reference Implementation: Puissance IT Section
The Puissance IT section (lines 862-1017) also shows everything on one page:
- Distribution histogram with KDE
- Box plot
- Time series evolution
- Rolling averages
- Autocorrelation
- All metrics and stats displayed together

## Proposed Solution

### New Structure for EDA Section
Instead of dropdown navigation, display all analyses for selected metric(s) on one page:

```
EDA Section:
├── Metric Selection (multi-select possible)
└── For each selected metric:
    ├── Info & Statistics Panel
    │   ├── Basic info (count, type, missing values)
    │   └── Descriptive statistics table
    ├── Distribution Analysis
    │   ├── Histogram with KDE
    │   └── Box plot
    ├── Time Series Analysis
    │   ├── Raw time series
    │   ├── Daily averages
    │   └── Hourly profile
    └── Additional Analysis
        └── Metric-specific visualizations
```

### Implementation Plan

#### Phase 1: Restructure Navigation
1. Remove the dropdown for EDA subsections
2. Add multi-select for metrics at the top
3. Create a scrollable single-page layout

#### Phase 2: Create Unified Visualizations
For each selected metric, create sections with:

1. **Statistics Section**
   - Combine "Info datasets" and "Statistiques descriptives"
   - Show in expandable cards or tabs

2. **Distribution Section**
   - Side-by-side histogram and box plot
   - Use columns for layout

3. **Time Series Section**
   - Raw series, daily averages, and hourly profiles
   - Use tabs or expandable sections

#### Phase 3: Optimize Layout
1. Use Streamlit columns and expanders efficiently
2. Add "Expand All" / "Collapse All" buttons
3. Ensure responsive design

### Benefits
1. **Fewer Clicks**: All analyses visible immediately
2. **Better Overview**: Users can see all aspects of data at once
3. **Comparison**: Easy to compare multiple metrics
4. **Consistency**: Matches CLIM and Puissance IT sections

### Technical Considerations
1. **Performance**: May need to limit number of simultaneous metrics
2. **Layout**: Use st.columns(), st.expander(), and st.tabs()
3. **Caching**: Ensure calculations are cached for performance
4. **Scrolling**: Page will be longer but more comprehensive

## Questions for Validation
1. Should we limit the number of metrics that can be selected simultaneously?
2. Do you prefer tabs, expanders, or all visualizations visible by default?
3. Should we keep the current visualizations or add/remove any?
4. Any specific order preference for the visualizations?