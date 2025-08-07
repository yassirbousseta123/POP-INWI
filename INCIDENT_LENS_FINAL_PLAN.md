# Incident Lens - Final Implementation Plan (General & Reliable)

## Critical Design Principles

### 1. No Assumptions About Time Ranges
- User might analyze 1 hour, 1 day, 1 week, or 1 month
- System must handle sparse data (missing sensors)
- Must work with incomplete data periods
- No hardcoded time windows or durations

### 2. Adaptive Analysis Strategy
Instead of fixed rules, the system must:
- **Dynamically determine** what constitutes an anomaly based on the selected period
- **Adjust confidence** based on data availability
- **Scale correlations** to the time range context

## Revised Architecture: Context-Aware Analysis Engine

### Core Components

#### 1. Dynamic Anomaly Detection
```
User Input:
- Time Range: Any duration (5 minutes to 1 year)
- Temperature Bounds: Min/Max tolerable
- Analysis Depth: Quick/Standard/Deep

System Response:
- Identifies ALL temperature readings outside bounds
- Groups consecutive anomalies into "incidents"
- Calculates incident severity based on:
  - Duration relative to time range
  - Magnitude of deviation
  - Frequency of occurrence
```

#### 2. Adaptive Root Cause Analysis

**Key Insight**: Root causes have different "signatures" at different time scales

```
Short Range (Hours):
- Direct correlations matter most
- Immediate causes (door open, CLIM off)
- Minute-by-minute analysis

Medium Range (Days):
- Pattern recognition becomes important
- Recurring causes (daily CLIM maintenance)
- Hourly aggregations

Long Range (Weeks/Months):
- Statistical trends dominate
- Seasonal patterns (summer heat waves)
- Daily aggregations
```

### 3. General-Purpose Cause Detection Framework

#### 3.1 Cause Categories with Adaptive Detection

**CLIM-Related Causes**
```
Detection Strategy:
- Calculate CLIM availability % during incident
- Compare to baseline availability in time range
- Adjust for normal maintenance patterns

Confidence Factors:
- Temporal alignment (when CLIM failed vs temp rose)
- Impact magnitude (how many units failed)
- Recovery correlation (temp drops when CLIM returns)
```

**Environmental Causes**
```
Detection Strategy:
- Analyze external/internal temperature relationship
- Account for thermal lag (building insulation)
- Consider time-of-day effects

Confidence Factors:
- Correlation strength over time range
- External temperature extremity
- Historical pattern matching
```

**Door-Related Causes**
```
Detection Strategy:
- Identify door open events near anomalies
- Calculate exposure time vs impact
- Consider concurrent factors

Confidence Factors:
- Duration relative to incident
- Temperature differential (inside/outside)
- Frequency of door events in period
```

**Power/Load Causes**
```
Detection Strategy:
- Detect unusual power patterns
- Calculate heat generation estimates
- Check PUE degradation

Confidence Factors:
- Power spike magnitude
- Timing relative to temperature rise
- Cooling efficiency metrics
```

### 4. Reliability Mechanisms

#### 4.1 Data Quality Assessment
Before analysis, assess:
- Data completeness (% of expected readings)
- Sensor reliability (detect stuck/failed sensors)
- Temporal gaps (missing time periods)

#### 4.2 Confidence Adjustment
```
Base Confidence = Algorithm Score
Adjusted Confidence = Base × Data Quality Factor × Time Range Factor

Where:
- Data Quality Factor: 0.5-1.0 based on completeness
- Time Range Factor: Accounts for analysis granularity
```

#### 4.3 Multi-Evidence Correlation
Never rely on single indicator:
```
For each potential cause:
1. Primary Evidence (direct correlation)
2. Supporting Evidence (related metrics)
3. Negative Evidence (contradicting factors)
4. Historical Evidence (past patterns)

Final Score = Weighted combination of all evidence
```

### 5. Implementation Strategy

#### Phase 1: Core Analysis Engine
```
class IncidentLensAnalyzer:
    def analyze(self, data, time_start, time_end, temp_min, temp_max):
        # 1. Validate and prepare data
        validated_data = self.validate_data_quality(data, time_start, time_end)
        
        # 2. Detect anomalies
        anomalies = self.detect_anomalies(validated_data, temp_min, temp_max)
        
        # 3. Group into incidents
        incidents = self.group_anomalies_to_incidents(anomalies)
        
        # 4. Analyze each incident
        results = []
        for incident in incidents:
            causes = self.analyze_incident_causes(
                incident, 
                validated_data,
                context={'time_range': time_end - time_start}
            )
            results.append({
                'incident': incident,
                'causes': causes,
                'data_quality': validated_data.quality_score
            })
            
        return results
```

#### Phase 2: Cause Detection Modules
Each cause type has its own module:
```
class CLIMCauseDetector:
    def detect(self, incident, data, context):
        # Adaptive detection based on time range
        if context['time_range'] < timedelta(hours=24):
            return self._detect_immediate_failure(incident, data)
        elif context['time_range'] < timedelta(days=7):
            return self._detect_pattern_failure(incident, data)
        else:
            return self._detect_statistical_failure(incident, data)
```

#### Phase 3: Result Aggregation
```
class CauseAggregator:
    def combine_evidence(self, detections, data_quality):
        # Sort by raw confidence
        sorted_causes = sorted(detections, key=lambda x: x.confidence, reverse=True)
        
        # Apply quality adjustments
        for cause in sorted_causes:
            cause.adjusted_confidence = self._adjust_confidence(
                cause.confidence,
                data_quality,
                cause.evidence_strength
            )
            
        # Filter out low-confidence causes
        significant_causes = [c for c in sorted_causes if c.adjusted_confidence > 30]
        
        return significant_causes
```

### 6. Key Design Decisions

#### 6.1 No Hardcoded Thresholds
- All thresholds are relative to the data context
- Use percentiles instead of absolute values
- Adapt to seasonal variations automatically

#### 6.2 Evidence-Based Scoring
- Every cause must have measurable evidence
- Confidence reflects evidence strength, not assumptions
- Missing data reduces confidence, doesn't break analysis

#### 6.3 Scalable Architecture
- Works equally well for 1 hour or 1 year
- Performance scales with data size, not time range
- Can add new cause detectors without changing core

### 7. Output Format

```json
{
  "analysis_period": {
    "start": "2024-01-15T00:00:00",
    "end": "2024-01-15T23:59:59",
    "duration_hours": 24,
    "data_completeness": 0.95
  },
  "incidents": [
    {
      "id": "INC_001",
      "start_time": "2024-01-15T14:00:00",
      "end_time": "2024-01-15T15:30:00",
      "severity": "high",
      "max_temperature": 28.5,
      "threshold_exceeded": 26.0,
      "root_causes": [
        {
          "cause": "CLIM_FAILURE",
          "confidence": 85,
          "evidence": {
            "primary": "CLIM_B and CLIM_C offline during incident",
            "supporting": "Cooling capacity reduced by 50%",
            "temporal": "CLIM failure preceded temperature rise by 15 minutes",
            "impact": "Temperature rose 2.5°C above normal"
          },
          "description": "Défaillance partielle du système CLIM - 2 unités sur 4 hors service"
        },
        {
          "cause": "EXTERNAL_HEAT",
          "confidence": 45,
          "evidence": {
            "primary": "External temperature 35°C during incident",
            "supporting": "Correlation coefficient 0.72",
            "temporal": "External heat present throughout incident",
            "impact": "Contributing factor, not primary cause"
          },
          "description": "Température extérieure élevée contribuant à la charge thermique"
        }
      ]
    }
  ],
  "summary": {
    "total_incidents": 1,
    "primary_cause_distribution": {
      "CLIM_FAILURE": 1,
      "EXTERNAL_HEAT": 0,
      "DOOR_EVENTS": 0,
      "POWER_ANOMALY": 0
    },
    "recommendation": "Maintenance préventive recommandée pour CLIM_B et CLIM_C"
  }
}
```

### 8. Performance Guarantees

- **Analysis Speed**: O(n) where n = number of data points
- **Memory Usage**: Streaming processing for large datasets
- **Response Time**: 
  - < 1 second for 1 day
  - < 5 seconds for 1 month
  - < 30 seconds for 1 year

### 9. Reliability Guarantees

1. **Graceful Degradation**: Works with partial data
2. **No Silent Failures**: Reports data quality issues
3. **Deterministic Results**: Same input = same output
4. **Auditable**: Every decision is logged with evidence

### 10. Testing Strategy

- Unit tests for each cause detector
- Integration tests with various time ranges
- Edge cases: missing data, sensor failures, extreme ranges
- Performance benchmarks for different data sizes
- Validation against known historical incidents

## Conclusion

This plan ensures the system is:
- **General**: Works for any time range without assumptions
- **Reliable**: Evidence-based, not guesswork
- **Transparent**: Clear reasoning for each conclusion
- **Performant**: Scales efficiently with data size
- **Maintainable**: Modular design for easy updates

The key is treating root cause analysis as an evidence collection problem, not a pattern matching problem. This makes the system robust to any time range or data scenario the user provides.