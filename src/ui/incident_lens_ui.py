"""
Incident Lens UI Components for Streamlit
User interface for temperature anomaly root cause analysis
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    from ..incident_lens.preprocessor import DataPreprocessor
    from ..incident_lens.analyzer import RootCauseAnalyzer
    from ..incident_lens.recommender import RecommendationEngine
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from src.incident_lens.preprocessor import DataPreprocessor
    from src.incident_lens.analyzer import RootCauseAnalyzer
    from src.incident_lens.recommender import RecommendationEngine


def render_incident_lens_interface():
    """Main interface for Incident Lens root cause analysis"""
    st.header("🔍 Incident Lens - Analyse des Causes Racines")
    st.markdown("""
    **Objectif**: Identifier automatiquement les causes des anomalies de température avec des scores de confiance.
    """)
    
    # Initialize session state
    if 'preprocessor' not in st.session_state:
        st.session_state.preprocessor = DataPreprocessor('data')
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    # Create input form
    with st.expander("⚙️ Configuration de l'analyse", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📅 Période d'analyse")
            
            # Quick time range buttons
            quick_ranges = {
                "Dernière heure": timedelta(hours=1),
                "Dernières 4 heures": timedelta(hours=4),
                "Dernières 24 heures": timedelta(days=1),
                "Derniers 3 jours": timedelta(days=3),
                "Dernière semaine": timedelta(weeks=1),
                "Dernier mois": timedelta(days=30)
            }
            
            selected_range = st.selectbox(
                "Sélection rapide",
                list(quick_ranges.keys()),
                index=2  # Default to 24 hours
            )
            
            # Calculate dates
            end_time = datetime.now()
            start_time = end_time - quick_ranges[selected_range]
            
            # Allow manual override
            use_custom = st.checkbox("Définir une période personnalisée")
            if use_custom:
                start_date = st.date_input("Date de début", value=start_time.date())
                start_time_input = st.time_input("Heure de début", value=start_time.time())
                end_date = st.date_input("Date de fin", value=end_time.date())
                end_time_input = st.time_input("Heure de fin", value=end_time.time())
                
                start_time = datetime.combine(start_date, start_time_input)
                end_time = datetime.combine(end_date, end_time_input)
            
        with col2:
            st.subheader("🌡️ Seuils de température")
            
            temp_min = st.number_input(
                "Température minimale acceptable (°C)",
                min_value=15.0,
                max_value=25.0,
                value=20.0,
                step=0.5,
                help="Températures en dessous de cette valeur seront considérées comme anomalies"
            )
            
            temp_max = st.number_input(
                "Température maximale acceptable (°C)",
                min_value=22.0,
                max_value=35.0,
                value=26.0,
                step=0.5,
                help="Températures au dessus de cette valeur seront considérées comme anomalies"
            )
            
            if temp_min >= temp_max:
                st.error("❌ La température minimale doit être inférieure à la maximale")
                return
                
        with col3:
            st.subheader("🎯 Options d'analyse")
            
            show_recommendations = st.checkbox(
                "Générer des recommandations",
                value=True,
                help="Créer des actions correctives spécifiques"
            )
    
    # Analysis button
    analyze_button = st.button(
        "🔍 Lancer l'analyse",
        type="primary",
        help="Analyser les anomalies de température dans la période sélectionnée"
    )
    
    if analyze_button:
        run_incident_analysis(
            start_time, end_time, temp_min, temp_max, show_recommendations
        )
    
    # Display results if available
    if st.session_state.analysis_results:
        display_analysis_results(
            st.session_state.analysis_results,
            show_recommendations
        )


def run_incident_analysis(start_time: datetime, end_time: datetime, 
                         temp_min: float, temp_max: float, show_recommendations: bool):
    """Execute the incident analysis"""
    
    with st.spinner("🔄 Chargement et analyse des données..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Load data
            status_text.text("📂 Chargement des données...")
            progress_bar.progress(20)
            
            preprocessor = st.session_state.preprocessor
            data = preprocessor.load_data(start_time, end_time, force_reload=True)
            
            if data.empty:
                st.error(f"❌ Aucune donnée trouvée pour la période {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%Y-%m-%d %H:%M')}")
                
                # Try to get available data range for user guidance
                try:
                    all_data = preprocessor.load_data()
                    if not all_data.empty:
                        data_start = all_data.index.min()
                        data_end = all_data.index.max()
                        st.info(f"💡 Données disponibles de {data_start.strftime('%Y-%m-%d %H:%M')} à {data_end.strftime('%Y-%m-%d %H:%M')}")
                        st.info("Veuillez ajuster la période d'analyse ou utiliser la sélection rapide.")
                    else:
                        st.warning("⚠️ Aucune donnée disponible dans les fichiers. Vérifiez les fichiers de données dans le dossier 'data'.")
                except Exception as e:
                    st.warning(f"⚠️ Problème de chargement des données: {str(e)}")
                    
                progress_bar.empty()
                status_text.empty()
                return
            
            # Step 2: Data validation
            status_text.text("✅ Validation des données...")
            progress_bar.progress(40)
            
            validation = preprocessor.validate_data_for_analysis(data)
            if not validation['is_valid']:
                st.error("❌ Données insuffisantes pour une analyse fiable")
                for error in validation['errors']:
                    st.error(f"• {error}")
                progress_bar.empty()
                status_text.empty()
                return
            
            if validation['warnings']:
                for warning in validation['warnings']:
                    st.warning(f"⚠️ {warning}")
            
            # Step 3: Run analysis
            status_text.text("🔍 Analyse des incidents...")
            progress_bar.progress(60)
            
            analyzer = RootCauseAnalyzer(data)
            analysis_results = analyzer.analyze_time_range(
                start_time, end_time, temp_min, temp_max
            )
            
            # Step 4: Generate recommendations if requested
            if show_recommendations and analysis_results['incidents']:
                status_text.text("💡 Génération des recommandations...")
                progress_bar.progress(80)
                
                recommender = RecommendationEngine()
                # Skip recommendation generation for now
                # Context-based recommendations can be added later if needed
                pass
            
            # Step 5: Store results
            progress_bar.progress(100)
            status_text.text("✅ Analyse terminée!")
            
            # Add metadata
            analysis_results['metadata'] = {
                'analysis_time': datetime.now(),
                'time_range': f"{start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%Y-%m-%d %H:%M')}",
                'temperature_thresholds': f"{temp_min}°C - {temp_max}°C",
                'data_points': len(data),
                'data_quality': validation['data_quality_score'] if 'data_quality_score' in validation else 0.8
            }
            
            st.session_state.analysis_results = analysis_results
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Show success message
            incident_count = len(analysis_results['incidents'])
            if incident_count > 0:
                st.success(f"✅ Analyse terminée: {incident_count} incident(s) détecté(s)")
            else:
                st.info("ℹ️ Aucune anomalie détectée dans la période analysée")
                
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
            st.exception(e)


def display_analysis_results(results: Dict[str, Any], show_recommendations: bool):
    """Display the analysis results"""
    
    if not results or not results.get('incidents'):
        st.info("ℹ️ Aucun incident détecté - système fonctionnel")
        return
    
    # Summary section
    st.subheader("📊 Résumé de l'analyse")
    
    metadata = results.get('metadata', {})
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Incidents détectés",
            len(results['incidents']),
            help="Nombre total d'anomalies de température"
        )
    
    with col2:
        data_quality = metadata.get('data_quality', 0) * 100
        st.metric(
            "Qualité des données",
            f"{data_quality:.0f}%",
            help="Pourcentage de données valides utilisées"
        )
    
    with col3:
        pass
    
    with col4:
        critical_count = sum(1 for inc in results['incidents'] 
                           if inc['incident'].severity.value == 'critical')
        st.metric(
            "Incidents critiques",
            critical_count,
            delta=f"{critical_count}/{len(results['incidents'])}",
            help="Incidents nécessitant une action immédiate"
        )
    
    # Timeline visualization
    st.subheader("📈 Chronologie des incidents")
    display_incident_timeline(results['incidents'])
    
    # Detailed incident analysis
    st.subheader("🔬 Analyse détaillée des incidents")
    
    for i, incident_result in enumerate(results['incidents'], 1):
        incident = incident_result['incident']
        context = incident_result['context']
        
        with st.expander(
            f"🚨 Incident #{i}: {incident.metric_value:.1f}°C à {incident.timestamp.strftime('%d/%m %H:%M')}", 
            expanded=i <= 3  # Auto-expand first 3 incidents
        ):
            display_incident_details(incident, context, show_recommendations, 
                                   incident_result.get('recommendations', []))


def display_incident_timeline(incidents: List[Dict[str, Any]]):
    """Create timeline visualization of incidents"""
    
    if not incidents:
        return
    
    # Prepare data for timeline
    timeline_data = []
    for i, inc_result in enumerate(incidents):
        incident = inc_result['incident']
        # Get context summary for timeline
        context = inc_result.get('context')
        context_summary = "Contexte indisponible"
        if context:
            # Create a brief summary from context
            door = context.door_status.get('severity', 'unknown')
            temp_ext = context.external_temp.get('severity', 'unknown')
            power = context.it_power.get('severity', 'unknown')
            clim = context.clim_status.get('severity', 'unknown')
            
            # Count critical factors
            critical_count = sum(1 for s in [door, temp_ext, power, clim] if s == 'critical')
            if critical_count > 0:
                context_summary = f"{critical_count} facteur(s) critique(s)"
            elif any(s == 'warning' for s in [door, temp_ext, power, clim]):
                context_summary = "Facteurs d'attention"
            else:
                context_summary = "Contexte normal"
        
        timeline_data.append({
            'timestamp': incident.timestamp,
            'temperature': incident.metric_value,
            'severity': incident.severity.value,
            'duration': incident.duration_seconds / 60 if incident.duration_seconds else 0,
            'context_summary': context_summary,
            'incident_id': f"Incident #{i+1}"
        })
    
    df = pd.DataFrame(timeline_data)
    
    # Create timeline plot
    fig = go.Figure()
    
    # Color mapping for severity
    color_map = {
        'critical': 'red',
        'warning': 'orange',
        'info': 'blue'
    }
    
    for severity in df['severity'].unique():
        severity_data = df[df['severity'] == severity]
        
        fig.add_trace(go.Scatter(
            x=severity_data['timestamp'],
            y=severity_data['temperature'],
            mode='markers+lines',
            name=f'Incidents {severity}',
            marker=dict(
                color=color_map.get(severity, 'gray'),
                size=severity_data['duration'].clip(5, 20),  # Size based on duration
                opacity=0.8,
                line=dict(width=1, color='white')
            ),
            text=severity_data['incident_id'],
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Température: %{y:.1f}°C<br>"
                "Heure: %{x}<br>"
                "Contexte: %{customdata[1]}"
                "<extra></extra>"
            ),
            customdata=severity_data[['duration', 'context_summary']].values
        ))
    
    fig.update_layout(
        title="Chronologie des incidents de température",
        xaxis_title="Temps",
        yaxis_title="Température (°C)",
        height=400,
        hovermode='closest',
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_incident_details(incident, context, show_recommendations: bool, recommendations: List):
    """Display detailed information about a specific incident"""
    
    # Incident info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**Température**: {incident.metric_value:.1f}°C")
    
    with col2:
        st.markdown(f"**Seuil dépassé**: {incident.threshold_violated:.1f}°C")
    
    with col3:
        st.markdown(f"**Heure**: {incident.timestamp.strftime('%d/%m/%Y %H:%M')}")
        st.markdown(f"**Description**: {incident.description}")
    
    # Context Analysis
    st.markdown("### 📊 Contexte pendant l'incident")
    
    # Helper function for severity colors
    def get_severity_color(severity):
        if severity == "good":
            return "🟢"
        elif severity == "warning":
            return "🟡"
        elif severity == "critical":
            return "🔴"
        else:
            return "⚪"
    
    # Display context as a simple table-like structure
    context_data = [
        ("🚪 Porte", context.door_status["status"], get_severity_color(context.door_status["severity"])),
        ("🌡️ Temp. ext", context.external_temp["status"], get_severity_color(context.external_temp["severity"])),
        ("⚡ Puissance IT", context.it_power["status"], get_severity_color(context.it_power["severity"])),
        ("❄️ CLIMs", context.clim_status["status"], get_severity_color(context.clim_status["severity"])),
        ("📈 Tendance", context.temp_trend["status"], get_severity_color(context.temp_trend["severity"]))
    ]
    
    # Create a clean display
    for icon_label, status, color in context_data:
        st.markdown(f"{icon_label}: {status} {color}")
    
    # Recommendations
    if show_recommendations and recommendations:
        st.markdown("### 💡 Recommandations")
        
        # Group by priority
        priority_order = ['immediate', 'urgent', 'high', 'medium', 'low']
        priority_labels = {
            'immediate': '🚨 IMMÉDIAT',
            'urgent': '⚡ URGENT',
            'high': '🔴 HAUTE PRIORITÉ',
            'medium': '🟡 PRIORITÉ MOYENNE',
            'low': '🟢 PRÉVENTIF'
        }
        
        recommendations_by_priority = {}
        for rec in recommendations:
            priority = rec.priority.value
            if priority not in recommendations_by_priority:
                recommendations_by_priority[priority] = []
            recommendations_by_priority[priority].append(rec)
        
        for priority in priority_order:
            if priority in recommendations_by_priority:
                st.markdown(f"#### {priority_labels[priority]}")
                
                for rec in recommendations_by_priority[priority]:
                    st.markdown(f"**{rec.title}** - {rec.estimated_time}")
                    st.markdown(f"**Description**: {rec.description}")
                    st.markdown(f"**Équipe responsable**: {rec.responsible_team}")
                    
                    if rec.steps:
                        st.markdown("**Étapes**:")
                        for step in rec.steps:
                            st.markdown(f"• {step}")
                    
                    if rec.resources_needed:
                        st.markdown(f"**Ressources nécessaires**: {', '.join(rec.resources_needed)}")
                    
                    if rec.expected_outcome:
                        st.markdown(f"**Résultat attendu**: {rec.expected_outcome}")
                    
                    st.markdown("---")  # Separator between recommendations


def render_incident_lens_summary():
    """Render summary view for main dashboard"""
    st.subheader("🔍 Incident Lens - Aperçu")
    
    if 'analysis_results' in st.session_state and st.session_state.analysis_results:
        results = st.session_state.analysis_results
        incidents = results.get('incidents', [])
        
        if incidents:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Incidents récents", len(incidents))
            
            with col2:
                critical_count = sum(1 for inc in incidents 
                                   if inc['incident'].severity.value == 'critical')
                st.metric("Critiques", critical_count)
            
            with col3:
                if incidents:
                    last_incident = max(incidents, key=lambda x: x['incident'].timestamp)
                    time_since = datetime.now() - last_incident['incident'].timestamp
                    st.metric("Dernier incident", f"Il y a {time_since.seconds // 3600}h")
            
            # Quick actions
            if st.button("🔍 Analyser maintenant", key="quick_analysis"):
                st.switch_page("Incident Lens")
        
        else:
            st.success("✅ Aucun incident récent détecté")
    
    else:
        st.info("ℹ️ Aucune analyse récente. Cliquez ci-dessous pour commencer.")
        if st.button("🚀 Lancer première analyse", key="first_analysis"):
            st.switch_page("Incident Lens")