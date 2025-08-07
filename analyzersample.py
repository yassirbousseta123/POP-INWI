import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

try:
    from .detector import Incident, IncidentType, IncidentSeverity
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from incident_lens.detector import Incident, IncidentType, IncidentSeverity

logger = logging.getLogger(__name__)

class RootCauseType(Enum):
    CLIM_TOTAL_FAILURE = "clim_total_failure"
    CLIM_PARTIAL_FAILURE = "clim_partial_failure"
    CLIM_INEFFICIENCY = "clim_inefficiency"
    DOOR_EXTENDED_OPEN = "door_extended_open"
    DOOR_FREQUENT_CYCLES = "door_frequent_cycles"
    EXTERNAL_HEAT_WAVE = "external_heat_wave"
    EXTERNAL_TEMP_INFLUENCE = "external_temp_influence"
    IT_POWER_SURGE = "it_power_surge"
    IT_POWER_HIGH_SUSTAINED = "it_power_high_sustained"
    COOLING_POWER_LOSS = "cooling_power_loss"
    PUE_DEGRADATION = "pue_degradation"
    COMPOUND_CAUSE = "compound_cause"
    UNKNOWN = "unknown"

@dataclass
class Evidence:
    type: str
    description: str
    value: Any
    confidence_contribution: float = 0.0

@dataclass
class RootCause:
    cause_type: RootCauseType
    confidence: float
    description: str
    evidence: List[Evidence] = field(default_factory=list)
    affected_metrics: List[str] = field(default_factory=list)
    time_detected: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    severity: str = "medium"
    recommendations: List[str] = field(default_factory=list)
    
    def add_evidence(self, evidence_type: str, description: str, value: Any, confidence_contrib: float = 0.0):
        self.evidence.append(Evidence(evidence_type, description, value, confidence_contrib))
    
    @property
    def calculated_confidence(self) -> float:
        return min(90.0, sum(e.confidence_contribution for e in self.evidence))

@dataclass
class DataQualityReport:
    completeness: float
    reliability: Dict[str, float]
    time_gaps: List[Tuple[datetime, datetime]] = field(default_factory=list)
    missing_sensors: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    
    def __post_init__(self):
        self.quality_score = self.completeness * np.mean(list(self.reliability.values())) if self.reliability else 0.0

class RootCauseAnalyzer:
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.data = self.data.sort_index()
        self._prepare_data()
        self._init_detectors()
    
    def _prepare_data(self):
        clim_cols = ['CLIM_A_Status', 'CLIM_B_Status', 'CLIM_C_Status', 'CLIM_D_Status']
        available_clim = [col for col in clim_cols if col in self.data.columns]
        if available_clim:
            self.data['clim_active_count'] = self.data[available_clim].sum(axis=1)
            self.data['clim_availability_pct'] = self.data['clim_active_count'] / len(available_clim) * 100
        
        if 'T°C AMBIANTE' in self.data.columns and 'T°C EXTERIEURE' in self.data.columns:
            self.data['temp_differential'] = self.data['T°C AMBIANTE'] - self.data['T°C EXTERIEURE']
        
        if 'Puissance_IT' in self.data.columns:
            self.data['power_change_rate'] = self.data['Puissance_IT'].diff()
        
        if 'Etat de porte' in self.data.columns:
            self.data['door_open_rolling'] = self.data['Etat de porte'].rolling(window=4, min_periods=1).sum()
    
    def _init_detectors(self):
        self.detectors = {
            'clim': CLIMCauseDetector(),
            'environmental': EnvironmentalCauseDetector(),
            'door': DoorCauseDetector(),
            'power': PowerCauseDetector()
        }
    
    def assess_data_quality(self, start_time: datetime, end_time: datetime) -> DataQualityReport:
        mask = (self.data.index >= start_time) & (self.data.index <= end_time)
        period_data = self.data[mask]
        
        if period_data.empty:
            return DataQualityReport(completeness=0.0, reliability={})
        
        duration = end_time - start_time
        expected_points = int(duration.total_seconds() / 900)
        actual_points = len(period_data)
        completeness = min(1.0, actual_points / expected_points) if expected_points > 0 else 0.0
        
        time_gaps = []
        if len(period_data) > 1:
            time_diffs = period_data.index.to_series().diff()
            gap_threshold = pd.Timedelta(minutes=30)
            for i, diff in enumerate(time_diffs[1:], 1):
                if diff > gap_threshold:
                    time_gaps.append((period_data.index[i-1], period_data.index[i]))
        
        reliability = {}
        for col in period_data.columns:
            col_data = period_data[col].dropna()
            if len(col_data) > 0:
                std = col_data.std()
                reliability[col] = 1.0 if std > 0.1 else 0.5
        
        expected_sensors = ['T°C AMBIANTE', 'T°C EXTERIEURE', 'Etat de porte'] + clim_cols
        missing_sensors = [s for s in expected_sensors if s not in self.data.columns]
        
        return DataQualityReport(
            completeness=completeness,
            reliability=reliability,
            time_gaps=time_gaps,
            missing_sensors=missing_sensors
        )
    
    def analyze_incident(self, incident: Incident, time_window_before: int = 60, time_window_after: int = 30) -> List[RootCause]:
        start_time = incident.timestamp - timedelta(minutes=time_window_before)
        end_time = incident.timestamp + timedelta(minutes=time_window_after)
        mask = (self.data.index >= start_time) & (self.data.index <= end_time)
        window_data = self.data[mask]
        
        if window_data.empty:
            return [RootCause(
                cause_type=RootCauseType.UNKNOWN,
                confidence=0.0,
                description="Insufficient data for analysis",
                time_detected=incident.timestamp
            )]
        
        quality = self.assess_data_quality(start_time, end_time)
        context = {
            'incident': incident,
            'time_range': end_time - start_time,
            'data_quality': quality,
            'incident_duration': incident.duration_seconds / 60 if incident.duration_seconds else None
        }
        
        all_causes = []
        for detector_name, detector in self.detectors.items():
            try:
                causes = detector.detect(window_data, context)
                all_causes.extend(causes)
            except Exception as e:
                logger.error(f"Error in {detector_name} detector: {e}")
        
        ranked_causes = self._rank_causes(all_causes, quality)
        for cause in ranked_causes:
            cause.recommendations = self._generate_recommendations(cause)
            cause.time_detected = incident.timestamp
        
        return ranked_causes
    
    def _rank_causes(self, causes: List[RootCause], quality: DataQualityReport) -> List[RootCause]:
        if not causes:
            return causes
        
        for cause in causes:
            cause.confidence = cause.calculated_confidence
            for metric in cause.affected_metrics:
                if metric in quality.reliability:
                    cause.confidence *= quality.reliability[metric]
            cause.confidence = max(25.0, min(90.0, cause.confidence))
        
        ranked = sorted(causes, key=lambda x: x.confidence, reverse=True)
        return [c for c in ranked if c.confidence >= 25.0]
    
    def _generate_recommendations(self, cause: RootCause) -> List[str]:
        recommendations = []
        if cause.cause_type == RootCauseType.CLIM_TOTAL_FAILURE:
            recommendations.extend([
                "🔧 Immediate CLIM system intervention required",
                "📞 Contact maintenance team urgently",
                "🌡️ Activate thermal contingency plan"
            ])
        elif cause.cause_type == RootCauseType.DOOR_EXTENDED_OPEN:
            recommendations.extend([
                "🚪 Check automatic door closing system",
                "👤 Train staff on access procedures",
                "📱 Set up door open alerts (>5min)"
            ])
        return recommendations

class CLIMCauseDetector:
    def detect(self, data: pd.DataFrame, context: Dict[str, Any]) -> List[RootCause]:
        causes = []
        incident = context['incident']
        quality = context['data_quality']
        
        clim_cols = [col for col in ['CLIM_A_Status', 'CLIM_B_Status', 'CLIM_C_Status', 'CLIM_D_Status'] if col in data.columns]
        if not clim_cols:
            return causes
        
        window_data = data.loc[incident.timestamp - timedelta(minutes=30):incident.timestamp + timedelta(minutes=15)]
        if window_data.empty:
            return causes
        
        active_counts = window_data[clim_cols].sum(axis=1)
        total_failure = (active_counts == 0).mean() > 0.7
        partial_failure = (active_counts < len(clim_cols) * 0.5).mean() > 0.6
        
        if total_failure:
            cause = RootCause(
                cause_type=RootCauseType.CLIM_TOTAL_FAILURE,
                confidence=0.0,
                description=f"Total CLIM failure - all units off",
                affected_metrics=clim_cols,
                severity="critical"
            )
            cause.add_evidence("status_check", f"All CLIM units off for {total_failure*100:.0f}% of window", total_failure, 40.0)
            if 'P_Active CLIM' in window_data.columns:
                power_corr = window_data['P_Active CLIM'].corr(active_counts)
                cause.add_evidence("power_corr", f"Power correlation: {power_corr:.2f}", power_corr, 20.0 if power_corr > 0.5 else 10.0)
            causes.append(cause)
        
        elif partial_failure:
            failed_units = [col for col in clim_cols if window_data[col].mean() < 0.3]
            cause = RootCause(
                cause_type=RootCauseType.CLIM_PARTIAL_FAILURE,
                confidence=0.0,
                description=f"Partial CLIM failure - units affected: {', '.join(failed_units)}",
                affected_metrics=failed_units,
                severity="high"
            )
            cause.add_evidence("unit_status", f"Partial failure detected in {len(failed_units)} units", len(failed_units), 30.0)
            causes.append(cause)
        
        return causes

class EnvironmentalCauseDetector:
    def detect(self, data: pd.DataFrame, context: Dict[str, Any]) -> List[RootCause]:
        causes = []
        incident = context['incident']
        quality = context['data_quality']
        
        if 'T°C EXTERIEURE' not in data.columns:
            return causes
        
        window_data = data.loc[incident.timestamp - timedelta(hours=2):incident.timestamp + timedelta(minutes=30)]
        if window_data.empty:
            return causes
        
        ext_temp = window_data['T°C EXTERIEURE']
        max_temp = ext_temp.max()
        if max_temp > 38:
            cause = RootCause(
                cause_type=RootCauseType.EXTERNAL_HEAT_WAVE,
                confidence=0.0,
                description=f"Heat wave detected - max temp: {max_temp:.1f}°C",
                affected_metrics=['T°C EXTERIEURE', 'T°C AMBIANTE'],
                severity="high"
            )
            cause.add_evidence("temp_peak", f"Max external temp: {max_temp:.1f}°C", max_temp, 30.0)
            if 'T°C AMBIANTE' in window_data.columns:
                corr = window_data['T°C AMBIANTE'].corr(ext_temp)
                cause.add_evidence("temp_corr", f"Internal temp correlation: {corr:.2f}", corr, 25.0 if corr > 0.4 else 15.0)
            causes.append(cause)
        
        return causes

class DoorCauseDetector:
    def detect(self, data: pd.DataFrame, context: Dict[str, Any]) -> List[RootCause]:
        causes = []
        incident = context['incident']
        quality = context['data_quality']
        
        if 'Etat de porte' not in data.columns:
            return causes
        
        window_data = data.loc[incident.timestamp - timedelta(hours=1):incident.timestamp + timedelta(minutes=15)]
        if window_data.empty:
            return causes
        
        door_open = window_data['Etat de porte']
        max_open = door_open.rolling(window=4).sum().max() * 15  # Minutes
        if max_open > 45:
            cause = RootCause(
                cause_type=RootCauseType.DOOR_EXTENDED_OPEN,
                confidence=0.0,
                description=f"Extended door open - max duration: {max_open:.0f} minutes",
                affected_metrics=['Etat de porte', 'T°C AMBIANTE'],
                severity="high",
                duration_minutes=int(max_open)
            )
            cause.add_evidence("duration", f"Door open for {max_open:.0f} minutes", max_open, 35.0)
            if 'T°C AMBIANTE' in window_data.columns:
                temp_impact = window_data['T°C AMBIANTE'].diff().sum()
                cause.add_evidence("temp_impact", f"Temperature rise: {temp_impact:.1f}°C", temp_impact, 20.0 if temp_impact > 0.5 else 10.0)
            causes.append(cause)
        
        return causes

class PowerCauseDetector:
    def detect(self, data: pd.DataFrame, context: Dict[str, Any]) -> List[RootCause]:
        causes = []
        incident = context['incident']
        quality = context['data_quality']
        
        if 'Puissance_IT' not in data.columns:
            return causes
        
        window_data = data.loc[incident.timestamp - timedelta(hours=2):incident.timestamp + timedelta(minutes=30)]
        if window_data.empty:
            return causes
        
        power = window_data['Puissance_IT']
        max_change = power.diff().abs().max()
        if max_change > 4:
            cause = RootCause(
                cause_type=RootCauseType.IT_POWER_SURGE,
                confidence=0.0,
                description=f"Power surge detected - max change: {max_change:.1f}kW",
                affected_metrics=['Puissance_IT', 'T°C AMBIANTE'],
                severity="medium"
            )
            cause.add_evidence("power_spike", f"Max power change: {max_change:.1f}kW", max_change, 30.0)
            if 'T°C AMBIANTE' in window_data.columns:
                corr = power.corr(window_data['T°C AMBIANTE'])
                cause.add_evidence("temp_corr", f"Temperature correlation: {corr:.2f}", corr, 20.0 if corr > 0.3 else 10.0)
            causes.append(cause)
        
        return causes