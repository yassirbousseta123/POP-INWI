# Incident Lens Root Cause Analysis - Implementation Plan

## Overview
This document outlines the implementation plan for the "Incident Lens" root cause exploration feature for the BGU-ONE data center temperature monitoring system. The feature will automatically analyze temperature anomalies and rank likely root causes with confidence scores.

## Feature Requirements
Based on user specifications:
- **Input**: Time range + min/max tolerable temperature thresholds
- **Output**: List of temperature anomalies with:
  - Root causes ranked by likelihood
  - Confidence percentage for each cause
  - Detailed description explaining why each cause is most likely

## Architecture Design

### 1. Core Components

#### 1.1 Enhanced Incident Detector (Existing)
- Already implemented in `src/incident_lens/detector.py`
- Detects temperature anomalies using thresholds:
  - Critical: >29°C (per inwi manual)
  - Warning: >26°C
  - Optimal: 20-23°C
- Provides context data for each incident

#### 1.2 Root Cause Analyzer (To Implement)
- New module: `src/incident_lens/analyzer.py`
- Uses PyRCA framework for causal analysis
- Implements causal graph for BGU-ONE system
- Ranks root causes with confidence scores

#### 1.3 Recommendation Engine (To Implement)
- New module: `src/incident_lens/recommender.py`
- Provides actionable recommendations based on root causes
- Includes historical pattern analysis

### 2. Causal Graph Model

Based on the BGU-ONE system architecture:

```
External Temperature ──┐
                       ├──► Ambient Temperature
Door Status ──────────┤
                       │
CLIM Status ──────────┤
(A, B, C, D)           │
                       │
IT Power Load ────────┤
                       │
General Power ────────┘
```

### 3. Root Cause Categories

#### 3.1 CLIM-Related Causes
- **CLIM Unit Failure**: One or more units offline
- **CLIM Degraded Performance**: Units running but inefficient
- **CLIM Power Issues**: Insufficient power to cooling units

#### 3.2 Environmental Causes
- **External Heat Wave**: Outside temperature >35°C
- **Door Left Open**: Door open >5 minutes during anomaly
- **Poor Insulation**: External temp strongly correlates with internal

#### 3.3 Power/Load Causes
- **IT Load Surge**: Sudden increase in IT equipment power
- **Power Distribution Issues**: Abnormal power patterns
- **PUE Degradation**: Efficiency loss leading to heat buildup

#### 3.4 Compound Causes
- **Multiple CLIM Failures + High External Temp**
- **Door Open + CLIM Failure**
- **Power Surge + Cooling Inefficiency**

## Implementation Steps

### Phase 1: Core RCA Module (Week 1)

1. **Install Dependencies**
   ```python
   # requirements.txt additions
   sfr-pyrca>=0.7.0
   pyod>=1.0.0
   networkx>=3.0
   scikit-learn>=1.3.0
   ```

2. **Implement analyzer.py**
   - Create `RootCauseAnalyzer` class
   - Define causal graph using networkx
   - Implement PyRCA integration
   - Add confidence scoring algorithm

3. **Enhance detector.py**
   - Add method to prepare data for RCA
   - Include more context in incident objects
   - Add correlation analysis helpers

### Phase 2: Causal Analysis Engine (Week 2)

1. **Build Causal Graph**
   ```python
   causal_graph = {
       'T°C EXTERIEURE': ['T°C AMBIANTE'],
       'Etat de porte': ['T°C AMBIANTE'],
       'CLIM_A_Status': ['T°C AMBIANTE', 'P_Active CLIM'],
       'CLIM_B_Status': ['T°C AMBIANTE', 'P_Active CLIM'],
       'CLIM_C_Status': ['T°C AMBIANTE', 'P_Active CLIM'],
       'CLIM_D_Status': ['T°C AMBIANTE', 'P_Active CLIM'],
       'Puissance_IT': ['T°C AMBIANTE', 'PUE'],
       'P_Active CLIM': ['PUE'],
       'P_Active Générale': ['PUE']
   }
   ```

2. **Implement Scoring Algorithms**
   - Temporal correlation scoring
   - Magnitude-based scoring
   - Historical pattern matching
   - Bayesian probability calculation

3. **Create Cause Templates**
   - Define explanation templates for each cause
   - Include severity indicators
   - Add remediation hints

### Phase 3: UI Integration (Week 3)

1. **Update Streamlit Interface**
   - Add new "Incident Lens" tab
   - Create input form:
     - Date/time range selector
     - Temperature threshold inputs
     - Analysis trigger button
   
2. **Results Display**
   - Timeline visualization of anomalies
   - Root cause ranking table
   - Confidence score gauges
   - Detailed explanation cards

3. **Export Functionality**
   - PDF report generation
   - CSV data export
   - API endpoint for integration

### Phase 4: Advanced Features (Week 4)

1. **Machine Learning Enhancement**
   - Train classification model on historical incidents
   - Implement online learning for improving accuracy
   - Add anomaly prediction capabilities

2. **Pattern Recognition**
   - Recurring incident detection
   - Seasonal pattern analysis
   - Predictive maintenance alerts

3. **Performance Optimization**
   - Implement caching for faster analysis
   - Add parallel processing for large datasets
   - Optimize causal graph traversal

## Technical Implementation Details

### 1. RootCauseAnalyzer Class Structure

```python
class RootCauseAnalyzer:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.causal_graph = self._build_causal_graph()
        self.pyrca_model = self._initialize_pyrca()
        
    def analyze_incident(self, 
                        incident: Incident,
                        time_window: int = 60) -> List[RootCause]:
        """
        Analyze a temperature incident and return ranked root causes
        
        Args:
            incident: The temperature anomaly incident
            time_window: Minutes before/after to analyze
            
        Returns:
            List of RootCause objects with confidence scores
        """
        # Implementation details...
        
    def _calculate_confidence(self, 
                            cause: str,
                            evidence: Dict) -> float:
        """Calculate confidence score (0-100%) for a cause"""
        # Implementation details...
```

### 2. Confidence Scoring Algorithm

```python
def calculate_confidence_score(cause_data):
    """
    Multi-factor confidence scoring:
    - Temporal correlation: 40% weight
    - Magnitude correlation: 30% weight
    - Historical frequency: 20% weight
    - Domain rules: 10% weight
    """
    scores = {
        'temporal': calculate_temporal_correlation(),
        'magnitude': calculate_magnitude_impact(),
        'historical': check_historical_patterns(),
        'rules': apply_domain_rules()
    }
    
    weighted_score = (
        scores['temporal'] * 0.4 +
        scores['magnitude'] * 0.3 +
        scores['historical'] * 0.2 +
        scores['rules'] * 0.1
    )
    
    return min(100, max(0, weighted_score))
```

### 3. Integration with Existing System

```python
# In app.py
def analyze_temperature_anomalies():
    # Get user inputs
    time_range = st.date_input("Select time range")
    temp_min = st.number_input("Min temperature (°C)", value=20.0)
    temp_max = st.number_input("Max temperature (°C)", value=26.0)
    
    if st.button("Analyze"):
        # Run incident detection
        detector = IncidentDetector(data)
        incidents = detector.detect_temperature_incidents(
            time_range, temp_min, temp_max
        )
        
        # Run root cause analysis
        analyzer = RootCauseAnalyzer(data)
        
        for incident in incidents:
            root_causes = analyzer.analyze_incident(incident)
            display_root_causes(incident, root_causes)
```

## Expected Outputs

### 1. Root Cause Report Example

```
Temperature Anomaly Detected: 28.5°C at 2025-01-15 14:30

Root Causes (Ranked by Confidence):

1. CLIM Unit Failures (85% confidence)
   - CLIM_B and CLIM_C offline for 45 minutes
   - Cooling capacity reduced by 50%
   - Strong temporal correlation with temperature rise
   
2. External Heat Wave (72% confidence)
   - External temperature: 38°C (3°C above normal)
   - Started 2 hours before internal temp spike
   - Historical pattern matches summer heat events

3. Door Left Open (45% confidence)
   - Door open for 15 minutes at 14:15
   - Moderate impact given CLIM failures
   - Contributed to but not primary cause
```

### 2. Visualization Components

- **Timeline Chart**: Shows temperature, causes, and correlations
- **Confidence Gauge**: Visual representation of certainty
- **Cause Tree**: Interactive causal path visualization
- **Recommendation Panel**: Actionable steps to resolve

## Testing Strategy

1. **Unit Tests**
   - Test each root cause detection algorithm
   - Validate confidence scoring logic
   - Test causal graph construction

2. **Integration Tests**
   - End-to-end incident analysis
   - UI interaction testing
   - Performance benchmarking

3. **Validation**
   - Compare with known historical incidents
   - Expert review of cause rankings
   - A/B testing with operators

## Performance Considerations

- **Analysis Speed**: <5 seconds for 1-week data range
- **Memory Usage**: Efficient handling of large datasets
- **Caching**: Store computed causal graphs and patterns
- **Scalability**: Support for multiple POPs analysis

## Security & Reliability

- Input validation for user-provided thresholds
- Graceful handling of missing sensor data
- Audit logging for all analyses performed
- Role-based access control for sensitive data

## Deployment Plan

1. **Development Environment**: Local testing with sample data
2. **Staging**: Deploy to test POP with real-time data
3. **Production**: Gradual rollout to all POPs
4. **Monitoring**: Track accuracy and performance metrics

## Success Metrics

- **Accuracy**: >80% correct root cause identification
- **Speed**: <5 second analysis time
- **Adoption**: >90% operator usage rate
- **MTTR**: 30% reduction in incident resolution time

## Next Steps

1. Review and approve implementation plan
2. Set up development environment
3. Begin Phase 1 implementation
4. Schedule weekly progress reviews

---

*This implementation plan provides a comprehensive roadmap for building the Incident Lens feature with reliable root cause analysis capabilities for the BGU-ONE data center temperature monitoring system.*