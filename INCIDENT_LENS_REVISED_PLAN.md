# Incident Lens - REVISED Implementation Plan (Fast & Reliable)

## Critical Issues with Original Plan
1. **PyRCA Overhead**: Complex causal inference library adds 2-3s latency
2. **Over-engineering**: ML models unnecessary when causes are deterministic
3. **Performance Risk**: <5s target unrealistic with proposed architecture
4. **Debugging Nightmare**: Black-box ML makes troubleshooting difficult

## Revised Architecture: Rule-Based Correlation Engine

### Core Principle: "Known Causes, Fast Detection"
Since we KNOW the exact causes from the inwi manual and system design:
- CLIM failures → Temperature rise
- Door open → Temperature rise  
- External heat → Internal heat
- Power surge → Heat generation

We can use **deterministic rules + correlation scoring** instead of complex ML.

## Fast & Reliable Implementation

### 1. Lightweight Root Cause Analyzer

```python
class FastRootCauseAnalyzer:
    """
    Rule-based analyzer with pre-computed correlations
    Target: <500ms analysis time
    """
    
    def __init__(self, data: pd.DataFrame):
        # Pre-compute all correlations at initialization
        self.data = data
        self.correlations = self._precompute_correlations()
        self.rules = self._load_detection_rules()
        
    def analyze_anomaly(self, timestamp, temp_value):
        """Instant analysis using pre-computed data"""
        # 1. Get 30-min window around anomaly
        window = self._get_time_window(timestamp, minutes=30)
        
        # 2. Apply detection rules (vectorized operations)
        causes = self._apply_rules(window)
        
        # 3. Score and rank (simple weighted scoring)
        ranked_causes = self._score_causes(causes, temp_value)
        
        return ranked_causes  # <100ms execution
```

### 2. Detection Rules (Domain Knowledge)

```python
DETECTION_RULES = {
    'CLIM_TOTAL_FAILURE': {
        'condition': lambda df: (df[['CLIM_A_Status', 'CLIM_B_Status', 
                                    'CLIM_C_Status', 'CLIM_D_Status']].sum(axis=1) == 0),
        'confidence_base': 95,
        'description': "Panne totale CLIM - Toutes unités hors service"
    },
    
    'CLIM_PARTIAL_FAILURE': {
        'condition': lambda df: (df[['CLIM_A_Status', 'CLIM_B_Status',
                                    'CLIM_C_Status', 'CLIM_D_Status']].sum(axis=1) < 2),
        'confidence_base': 80,
        'description': "Capacité CLIM réduite - {failed_units} unités en panne"
    },
    
    'DOOR_EXTENDED_OPEN': {
        'condition': lambda df: (df['Etat de porte'] == 1).rolling(2).sum() == 2,
        'confidence_base': 70,
        'description': "Porte restée ouverte >30 minutes"
    },
    
    'EXTERNAL_HEAT_WAVE': {
        'condition': lambda df: df['T°C EXTERIEURE'] > 35,
        'confidence_base': 60,
        'description': "Température extérieure élevée: {ext_temp}°C"
    },
    
    'POWER_SURGE': {
        'condition': lambda df: df['Puissance_IT'].diff().abs() > 3,
        'confidence_base': 50,
        'description': "Pic de charge IT: +{power_delta}kW"
    }
}
```

### 3. Confidence Scoring (Simple & Fast)

```python
def calculate_confidence(base_confidence, factors):
    """
    Simple weighted scoring - no ML needed
    Factors: temporal_proximity, magnitude, duration
    """
    score = base_confidence
    
    # Temporal boost: How close to anomaly time
    if factors['time_delta_minutes'] < 5:
        score += 10
    elif factors['time_delta_minutes'] < 15:
        score += 5
        
    # Magnitude boost: How severe the cause
    if factors['severity'] == 'critical':
        score += 10
    elif factors['severity'] == 'warning':
        score += 5
        
    # Duration boost: How long it lasted
    if factors['duration_minutes'] > 30:
        score += 5
        
    return min(100, score)
```

### 4. Optimized Data Processing

```python
class DataPreprocessor:
    """Pre-process data for instant analysis"""
    
    @staticmethod
    def prepare_data(df):
        # Add derived columns for faster analysis
        df['clim_active_count'] = df[['CLIM_A_Status', 'CLIM_B_Status',
                                      'CLIM_C_Status', 'CLIM_D_Status']].sum(axis=1)
        df['door_open_duration'] = df['Etat de porte'].rolling(4).sum() * 15  # minutes
        df['temp_delta_ext'] = df['T°C AMBIANTE'] - df['T°C EXTERIEURE']
        df['power_delta'] = df['Puissance_IT'].diff()
        
        # Pre-calculate rolling statistics
        df['temp_rolling_mean'] = df['T°C AMBIANTE'].rolling(4).mean()
        df['temp_rolling_std'] = df['T°C AMBIANTE'].rolling(4).std()
        
        return df
```

### 5. UI Integration (Instant Response)

```python
def analyze_temperature_incidents():
    # User inputs
    col1, col2, col3 = st.columns(3)
    with col1:
        start_date = st.date_input("Date début")
        start_time = st.time_input("Heure début")
    with col2:
        end_date = st.date_input("Date fin")  
        end_time = st.time_input("Heure fin")
    with col3:
        temp_min = st.number_input("T°C Min", value=20.0)
        temp_max = st.number_input("T°C Max", value=26.0)
    
    if st.button("🔍 Analyser", type="primary"):
        with st.spinner("Analyse en cours..."):
            # Pre-filtered data (already in memory)
            mask = (df.index >= start_datetime) & (df.index <= end_datetime)
            subset = df[mask]
            
            # Find anomalies (vectorized)
            anomalies = subset[(subset['T°C AMBIANTE'] < temp_min) | 
                              (subset['T°C AMBIANTE'] > temp_max)]
            
            # Analyze each anomaly
            analyzer = FastRootCauseAnalyzer(subset)
            
            for idx, anomaly in anomalies.iterrows():
                causes = analyzer.analyze_anomaly(idx, anomaly['T°C AMBIANTE'])
                display_results_instant(idx, causes)
```

## Performance Optimizations

### 1. Data Loading Strategy
```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_and_prepare_data():
    # Load all CSVs once
    data = load_all_data()
    # Pre-process immediately
    return DataPreprocessor.prepare_data(data)
```

### 2. Correlation Matrix Caching
```python
@st.cache_data
def compute_correlation_matrix(data):
    # Compute once, use many times
    relevant_cols = ['T°C AMBIANTE', 'T°C EXTERIEURE', 'clim_active_count',
                     'Etat de porte', 'Puissance_IT', 'P_Active CLIM']
    return data[relevant_cols].corr()
```

### 3. Incident Detection Vectorization
```python
def detect_all_incidents_fast(data, temp_min, temp_max):
    # Single pass detection
    mask = (data['T°C AMBIANTE'] < temp_min) | (data['T°C AMBIANTE'] > temp_max)
    incidents = data[mask].copy()
    
    # Batch process all incidents
    incidents['severity'] = pd.cut(incidents['T°C AMBIANTE'], 
                                  bins=[0, temp_min-2, temp_min, temp_max, temp_max+3, 50],
                                  labels=['critical_low', 'warning_low', 'normal', 'warning_high', 'critical_high'])
    
    return incidents
```

## Expected Performance

### Analysis Speed
- **Data Load**: <100ms (cached)
- **Anomaly Detection**: <50ms (vectorized)
- **Root Cause Analysis**: <200ms per incident
- **Total Time**: <1 second for typical analysis

### Reliability
- **Deterministic**: Same input = same output
- **Explainable**: Every score has clear reasoning
- **Debuggable**: Simple rules, no black boxes
- **Tested**: Each rule individually verifiable

## Implementation Timeline

### Day 1-2: Core Engine
1. Implement `FastRootCauseAnalyzer`
2. Create rule definitions
3. Build correlation scoring

### Day 3-4: UI Integration  
1. Update Streamlit interface
2. Add caching layers
3. Create result visualizations

### Day 5: Testing & Optimization
1. Performance profiling
2. Rule tuning based on test data
3. Final optimizations

## Key Advantages

1. **Speed**: Sub-second analysis guaranteed
2. **Reliability**: Deterministic rule-based approach
3. **Maintainability**: Simple to update rules
4. **Transparency**: Clear explanation for each cause
5. **No Dependencies**: No heavy ML libraries needed

## Example Output (Instant Display)

```
🔴 Anomalie Détectée: 28.5°C à 14:30

Causes Probables:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ Défaillance CLIM (92% confiance)
   ├─ CLIM_B et CLIM_C hors service
   ├─ Durée: 45 minutes
   └─ Impact: Capacité réduite de 50%

2️⃣ Vague de Chaleur (78% confiance)
   ├─ T°C Extérieure: 38°C
   ├─ Début: 2h avant l'anomalie
   └─ Corrélation: 0.85

3️⃣ Porte Ouverte (45% confiance)
   ├─ Durée d'ouverture: 15 min
   ├─ Heure: 14:15
   └─ Impact modéré (CLIM déjà défaillante)

⏱️ Temps d'analyse: 0.3s
```

This revised approach prioritizes **speed and reliability** over complexity, delivering instant results with clear explanations.