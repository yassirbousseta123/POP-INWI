import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from data_loader import DataCleaner
import warnings
warnings.filterwarnings('ignore')

# Import Unified Period Selector
from src.ui.period_selector import period_selector

# Import Incident Lens UI
try:
    from src.ui.incident_lens_ui import render_incident_lens_interface, render_incident_lens_summary
except ImportError as e:
    st.error(f"Erreur d'import Incident Lens: {e}")
    render_incident_lens_interface = None
    render_incident_lens_summary = None

# Configuration de la page
st.set_page_config(
    page_title="BGU-ONE Centre de Données - Tableau de Bord",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stTitle {
        color: #1E3A8A;
        font-size: 2.5rem !important;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stPlotlyChart {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Titre principal avec logo INWI
col_title, col_spacer, col_logo = st.columns([5, 0.5, 1])
with col_title:
    st.markdown("<h1 style='margin-top: 0; padding-top: 20px;'>🏢 BGU-ONE Centre de Données - Tableau de Bord de Surveillance</h1>", unsafe_allow_html=True)
with col_spacer:
    st.empty()
with col_logo:
    st.markdown("<div style='text-align: right; padding-top: 10px; padding-right: 20px;'>", unsafe_allow_html=True)
    st.image("logo_inwi.png", width=200)
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")

# Initialisation du cache
@st.cache_data
def load_data():
    """Charge et nettoie toutes les données"""
    cleaner = DataCleaner()
    cleaned_data = cleaner.load_all_data()
    merged_data = cleaner.merge_all_data(cleaned_data)
    return cleaned_data, merged_data

# Initialize session state for period selector before anything else
if 'unified_period' not in st.session_state:
    end_date_default = datetime.now()
    start_date_default = end_date_default - timedelta(days=7)
    st.session_state.unified_period = {
        'start_date': start_date_default,
        'end_date': end_date_default,
        'selection_type': 'Dernière semaine',
        'custom_range': None
    }

# Chargement des données
with st.spinner("Chargement des données..."):
    cleaned_data, merged_data = load_data()

# Unified Period Selector in Sidebar
start_date, end_date = period_selector.render_mini_selector()

# Filter all data based on unified period
filtered_merged_data = period_selector.filter_dataframe(merged_data) if not merged_data.empty else merged_data

# Navigation horizontale
st.markdown("## 🎯 Navigation")

# Créer les onglets pour la navigation
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📊 Vue d'ensemble",
    "📈 Analyse temporelle",
    "🔬 Analyses EDA",
    "❄️ Analyse CLIM",
    "🚪 Analyse Porte",
    "🔍 Incident Lens",
    "🔗 Corrélations",
    "📋 Rapports",
    "💰 Simulation Coûts"
])


# 1. VUE D'ENSEMBLE
with tab1:
    st.header("📊 Vue d'ensemble du système")
    
    if not filtered_merged_data.empty and 'Timestamp' in filtered_merged_data.columns:
        # Display current unified period
        st.info(f"📅 Période sélectionnée: {start_date.strftime('%Y-%m-%d %H:%M')} - {end_date.strftime('%Y-%m-%d %H:%M')}")
        
        # Use the already filtered data from unified selector
        filtered_data = filtered_merged_data
        
        if not filtered_data.empty:
            # Métriques importantes
            st.subheader("📊 Métriques clés pour la période sélectionnée")
            
            # Fonction pour calculer les statistiques
            def calculate_stats(data, column):
                if column in data.columns:
                    # Filtrer les valeurs non-NaN
                    valid_data = data[column].dropna()
                    if len(valid_data) > 0:
                        return {
                            'min': valid_data.min(),
                            'max': valid_data.max(),
                            'mean': valid_data.mean(),
                            'median': valid_data.median()
                        }
                return {'min': 0, 'max': 0, 'mean': 0, 'median': 0}
            
            # Température Ambiante
            st.markdown("### 🌡️ Température Ambiante")
            temp_amb_stats = calculate_stats(filtered_data, 'Temp_Ambiante')
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Min", f"{temp_amb_stats['min']:.1f}°C")
            with col2:
                st.metric("Max", f"{temp_amb_stats['max']:.1f}°C")
            with col3:
                st.metric("Moyenne", f"{temp_amb_stats['mean']:.1f}°C")
            with col4:
                st.metric("Médiane", f"{temp_amb_stats['median']:.1f}°C")
            
            # Température Extérieure
            st.markdown("### 🌤️ Température Extérieure")
            temp_ext_stats = calculate_stats(filtered_data, 'Temp_Exterieure')
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Min", f"{temp_ext_stats['min']:.1f}°C")
            with col2:
                st.metric("Max", f"{temp_ext_stats['max']:.1f}°C")
            with col3:
                st.metric("Moyenne", f"{temp_ext_stats['mean']:.1f}°C")
            with col4:
                st.metric("Médiane", f"{temp_ext_stats['median']:.1f}°C")
            
            # Puissance IT
            st.markdown("### 💻 Puissance IT")
            puiss_it_stats = calculate_stats(filtered_data, 'Puissance_IT')
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Min", f"{puiss_it_stats['min']:.1f} kW")
            with col2:
                st.metric("Max", f"{puiss_it_stats['max']:.1f} kW")
            with col3:
                st.metric("Moyenne", f"{puiss_it_stats['mean']:.1f} kW")
            with col4:
                st.metric("Médiane", f"{puiss_it_stats['median']:.1f} kW")
            
            # Graphique temporel unifié
            st.subheader("📈 Évolution temporelle")
            
            # Sélection des données à afficher
            available_metrics = {
                'Temp_Ambiante': '🌡️ Température Ambiante (°C)',
                'Temp_Exterieure': '🌤️ Température Extérieure (°C)',
                'Puissance_IT': '💻 Puissance IT (kW)',
                'Puissance_Generale': '⚡ Puissance Générale (kW)',
                'Puissance_CLIM': '❄️ Puissance CLIM (kW)',
                'CLIM_A_Status': '❄️ État CLIM A',
                'CLIM_B_Status': '❄️ État CLIM B',
                'CLIM_C_Status': '❄️ État CLIM C',
                'CLIM_D_Status': '❄️ État CLIM D',
                'Porte_Status': '🚪 État Porte'
            }
            
            # Filtrer les métriques disponibles
            available_cols = [col for col in available_metrics.keys() if col in filtered_data.columns]
            
            # Afficher des informations sur la disponibilité des données
            with st.expander("ℹ️ Informations sur les données disponibles"):
                for col in available_cols:
                    valid_count = filtered_data[col].notna().sum()
                    total_count = len(filtered_data)
                    percentage = (valid_count / total_count * 100) if total_count > 0 else 0
                    st.text(f"{available_metrics[col]}: {valid_count}/{total_count} points ({percentage:.1f}%)")
            
            # Boutons de sélection rapide
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("🌡️ Toutes Températures"):
                    temp_metrics = [col for col in available_cols if 'Temp' in col]
                    st.session_state['selected_metrics'] = temp_metrics
            with col2:
                if st.button("⚡ Toutes Puissances"):
                    power_metrics = [col for col in available_cols if 'Puissance' in col]
                    st.session_state['selected_metrics'] = power_metrics
            with col3:
                if st.button("❄️ Tous CLIMs"):
                    clim_metrics = [col for col in available_cols if 'CLIM' in col and 'Status' in col]
                    st.session_state['selected_metrics'] = clim_metrics
            with col4:
                if st.button("📊 Tout Sélectionner"):
                    st.session_state['selected_metrics'] = available_cols
            
            selected_metrics = st.multiselect(
                "Sélectionner les données à afficher dans le graphique:",
                available_cols,
                default=st.session_state.get('selected_metrics', ['Temp_Ambiante', 'Temp_Exterieure', 'Puissance_IT'] if all(col in available_cols for col in ['Temp_Ambiante', 'Temp_Exterieure', 'Puissance_IT']) else available_cols[:3]),
                format_func=lambda x: available_metrics[x]
            )
            
            if selected_metrics:
                # Créer un graphique unifié avec axes secondaires si nécessaire
                fig = go.Figure()
                
                # Nouvelles couleurs optimisées pour la superposition avec transparence
                # Couleurs sémantiques et contrastées pour une meilleure visibilité en superposition
                color_scheme = {
                    # Températures - tons bleus/cyan
                    'Temp_Ambiante': {'color': '#2E86AB', 'fill': 'rgba(46, 134, 171, 0.4)'},
                    'Temp_Exterieure': {'color': '#A23B72', 'fill': 'rgba(162, 59, 114, 0.3)'},
                    
                    # Puissances - tons orange/rouge
                    'Puissance_IT': {'color': '#F18F01', 'fill': 'rgba(241, 143, 1, 0.5)'},
                    'Puissance_Generale': {'color': '#C73E1D', 'fill': 'rgba(199, 62, 29, 0.4)'},
                    'Puissance_CLIM': {'color': '#FF6B6B', 'fill': 'rgba(255, 107, 107, 0.3)'},
                    
                    # États CLIM - tons verts avec transparence élevée
                    'CLIM_A_Status': {'color': '#4ECDC4', 'fill': 'rgba(78, 205, 196, 0.6)'},
                    'CLIM_B_Status': {'color': '#45B7D1', 'fill': 'rgba(69, 183, 209, 0.6)'},
                    'CLIM_C_Status': {'color': '#96CEB4', 'fill': 'rgba(150, 206, 180, 0.6)'},
                    'CLIM_D_Status': {'color': '#FECA57', 'fill': 'rgba(254, 202, 87, 0.6)'},
                    
                    # Porte - ton violet
                    'Porte_Status': {'color': '#6C5CE7', 'fill': 'rgba(108, 92, 231, 0.7)'}
                }
                
                # Couleurs de fallback pour métriques non définies
                fallback_colors = [
                    {'color': '#FF9F43', 'fill': 'rgba(255, 159, 67, 0.4)'},
                    {'color': '#10AC84', 'fill': 'rgba(16, 172, 132, 0.4)'},
                    {'color': '#EE5A24', 'fill': 'rgba(238, 90, 36, 0.4)'},
                    {'color': '#0984e3', 'fill': 'rgba(9, 132, 227, 0.4)'},
                    {'color': '#a29bfe', 'fill': 'rgba(162, 155, 254, 0.4)'},
                    {'color': '#fd79a8', 'fill': 'rgba(253, 121, 168, 0.4)'},
                    {'color': '#fdcb6e', 'fill': 'rgba(253, 203, 110, 0.4)'},
                    {'color': '#6c5ce7', 'fill': 'rgba(108, 92, 231, 0.4)'}
                ]
                
                # Déterminer si on a besoin d'axes secondaires
                has_temp = any('Temp' in m for m in selected_metrics)
                has_power = any('Puissance' in m for m in selected_metrics)
                has_status = any('Status' in m for m in selected_metrics)
                
                # Séparer les données continues des données binaires
                continuous_metrics = [m for m in selected_metrics if 'Status' not in m]
                binary_metrics = [m for m in selected_metrics if 'Status' in m]
                
                # Option d'affichage pour les données binaires
                col1, col2 = st.columns([3, 1])
                with col2:
                    binary_display = st.selectbox(
                        "Affichage binaires:",
                        ["Superposées transparentes", "Séparées classiques"],
                        help="Superposées: données binaires empilées avec transparence par-dessus les continues. Séparées: affichage classique."
                    )
                
                # 1. COUCHE DE FOND : Tracer d'abord toutes les données continues normalement
                for idx, metric in enumerate(continuous_metrics):
                    # Obtenir les couleurs pour cette métrique
                    if metric in color_scheme:
                        colors_data = color_scheme[metric]
                    else:
                        colors_data = fallback_colors[idx % len(fallback_colors)]
                    
                    # Déterminer l'axe Y approprié
                    if 'Temp' in metric:
                        yaxis = 'y'
                    elif 'Puissance' in metric:
                        yaxis = 'y2' if has_temp else 'y'
                    
                    # Préparer les données
                    mask_valid = filtered_data[metric].notna()
                    x_data = filtered_data.loc[mask_valid, 'Timestamp']
                    y_data = filtered_data.loc[mask_valid, metric]
                    
                    if len(x_data) > 0:
                        # Tracer les données continues normalement (pas de transparence)
                        fig.add_trace(go.Scatter(
                            x=x_data,
                            y=y_data,
                            name=available_metrics[metric],
                            mode='lines',
                            line=dict(color=colors_data['color'], width=2.5),
                            yaxis=yaxis,
                            connectgaps=True,
                            hovertemplate='<b>%{fullData.name}</b><br>Valeur: %{y:.2f}<br>Temps: %{x}<extra></extra>'
                        ))
                
                # 2. COUCHE SUPERPOSÉE : Tracer les données binaires par-dessus
                if binary_metrics and binary_display == "Superposées transparentes":
                    # Calculer la plage des données continues pour normaliser les binaires
                    if continuous_metrics:
                        # Trouver min/max global des données continues pour la normalisation
                        all_continuous_values = []
                        for metric in continuous_metrics:
                            mask_valid = filtered_data[metric].notna()
                            if mask_valid.any():
                                all_continuous_values.extend(filtered_data.loc[mask_valid, metric].values)
                        
                        if all_continuous_values:
                            y_min, y_max = min(all_continuous_values), max(all_continuous_values)
                            y_range = y_max - y_min if y_max != y_min else 1
                            band_height = y_range * 0.15  # Chaque bande binaire = 15% de la plage
                        else:
                            y_min, y_max, y_range, band_height = 0, 1, 1, 0.2
                    else:
                        y_min, y_max, y_range, band_height = 0, 1, 1, 0.2
                    
                    # Tracer chaque donnée binaire comme une bande transparente empilée
                    for idx, metric in enumerate(binary_metrics):
                        # Couleurs pour les binaires avec forte transparence
                        binary_colors = [
                            {'color': '#4ECDC4', 'fill': 'rgba(78, 205, 196, 0.4)'},
                            {'color': '#45B7D1', 'fill': 'rgba(69, 183, 209, 0.4)'},
                            {'color': '#96CEB4', 'fill': 'rgba(150, 206, 180, 0.4)'},
                            {'color': '#FECA57', 'fill': 'rgba(254, 202, 87, 0.4)'},
                            {'color': '#6C5CE7', 'fill': 'rgba(108, 92, 231, 0.4)'}
                        ]
                        colors_data = binary_colors[idx % len(binary_colors)]
                        
                        # Préparer les données binaires
                        mask_valid = filtered_data[metric].notna()
                        x_data = filtered_data.loc[mask_valid, 'Timestamp']
                        binary_values = filtered_data.loc[mask_valid, metric]
                        
                        if len(x_data) > 0:
                            # Créer des bandes empilées pour les binaires
                            # Base de la bande actuelle
                            band_bottom = y_max + (idx * band_height * 0.6)  # Espacement entre bandes
                            
                            # Convertir les 0/1 en zones remplies
                            y_bottom = [band_bottom] * len(x_data)
                            y_top = [band_bottom + (band_height * 0.5 * val) for val in binary_values]
                            
                            # Trace pour le bas de la bande (invisible)
                            fig.add_trace(go.Scatter(
                                x=x_data,
                                y=y_bottom,
                                name=f"{available_metrics[metric]} (base)",
                                mode='lines',
                                line=dict(color='rgba(0,0,0,0)', width=0),
                                showlegend=False,
                                yaxis='y' if (continuous_metrics and 'Temp' in continuous_metrics[0]) else 'y',
                                hoverinfo='skip'
                            ))
                            
                            # Trace pour le haut de la bande (visible avec remplissage)
                            fig.add_trace(go.Scatter(
                                x=x_data,
                                y=y_top,
                                name=available_metrics[metric],
                                mode='lines',
                                line=dict(color=colors_data['color'], width=1),
                                fill='tonexty',  # Remplir entre cette trace et la précédente
                                fillcolor=colors_data['fill'],
                                yaxis='y' if (continuous_metrics and 'Temp' in continuous_metrics[0]) else 'y',
                                connectgaps=False,
                                hovertemplate='<b>%{fullData.name}</b><br>Valeur: %{customdata}<br>Temps: %{x}<extra></extra>',
                                customdata=binary_values
                            ))
                
                elif binary_metrics and binary_display == "Séparées classiques":
                    # Mode classique pour les binaires
                    for idx, metric in enumerate(binary_metrics):
                        if metric in color_scheme:
                            colors_data = color_scheme[metric]
                        else:
                            colors_data = fallback_colors[(len(continuous_metrics) + idx) % len(fallback_colors)]
                        
                        yaxis = 'y3' if (has_temp and has_power) else ('y2' if (has_temp or has_power) else 'y')
                        
                        mask_valid = filtered_data[metric].notna()
                        x_data = filtered_data.loc[mask_valid, 'Timestamp']
                        y_data = filtered_data.loc[mask_valid, metric]
                        
                        if len(x_data) > 0:
                            fig.add_trace(go.Scatter(
                                x=x_data,
                                y=y_data,
                                name=available_metrics[metric],
                                mode='lines',
                                line=dict(shape='hv', color=colors_data['color'], width=2),
                                yaxis=yaxis,
                                connectgaps=False
                            ))
                
                # Vérifier s'il y a des traces ajoutées
                if len(fig.data) == 0:
                    st.warning("Aucune donnée valide trouvée pour les métriques sélectionnées dans la période choisie.")
                else:
                    # Configuration améliorée du layout pour la superposition
                    layout_config = {
                        'title': dict(
                            text=f'📈 Évolution temporelle - {binary_display}',
                            font=dict(size=18, color='#2C3E50')
                        ),
                        'xaxis': dict(
                            title='Temps',
                            showgrid=True,
                            gridcolor='rgba(128,128,128,0.2)',
                            zeroline=False
                        ),
                        'hovermode': 'x unified',
                        'height': 700,
                        'plot_bgcolor': 'rgba(0,0,0,0)',
                        'paper_bgcolor': 'rgba(0,0,0,0)',
                        'legend': dict(
                            orientation="v",
                            yanchor="top",
                            y=1,
                            xanchor="left",
                            x=1.02,
                            bgcolor="rgba(255,255,255,0.8)",
                            bordercolor="rgba(128,128,128,0.3)",
                            borderwidth=1
                        ),
                        'margin': dict(r=200)  # Plus d'espace pour la légende
                    }
                
                    # Configuration des axes Y pour le nouveau système de couches
                    # L'axe Y principal est toujours pour les données continues
                    if has_temp:
                        layout_config['yaxis'] = dict(
                            title='Température (°C)',
                            side='left',
                            showgrid=True,
                            gridcolor='rgba(128,128,128,0.2)',
                            zeroline=True,
                            zerolinecolor='rgba(128,128,128,0.4)',
                            titlefont=dict(color='#2E86AB')
                        )
                    
                    # Axe Y secondaire pour les puissances
                    if has_power and has_temp:
                        layout_config['yaxis2'] = dict(
                            title='Puissance (kW)',
                            overlaying='y',
                            side='right',
                            showgrid=False,
                            zeroline=False,
                            titlefont=dict(color='#F18F01')
                        )
                    elif has_power:
                        layout_config['yaxis'] = dict(
                            title='Puissance (kW)',
                            side='left',
                            showgrid=True,
                            gridcolor='rgba(128,128,128,0.2)',
                            zeroline=True,
                            zerolinecolor='rgba(128,128,128,0.4)',
                            titlefont=dict(color='#F18F01')
                        )
                    
                    # Ajouter troisième axe pour binaires séparées si nécessaire
                    if binary_display == "Séparées classiques" and binary_metrics:
                        if has_status and (has_temp or has_power):
                            if has_temp and has_power:
                                layout_config['yaxis3'] = dict(
                                    title='État (0=OFF, 1=ON)',
                                    overlaying='y',
                                    side='right',
                                    position=0.85,
                                    anchor='free',
                                    tickvals=[0, 1],
                                    ticktext=['OFF', 'ON']
                                )
                                layout_config['xaxis']['domain'] = [0, 0.85]
                            else:
                                layout_config['yaxis2'] = dict(
                                    title='État (0=OFF, 1=ON)',
                                    overlaying='y',
                                    side='right',
                                    tickvals=[0, 1],
                                    ticktext=['OFF', 'ON']
                                )
                    
                    fig.update_layout(**layout_config)
                    
                    # Ajouter des fonctionnalités interactives supplémentaires
                    fig.update_layout(
                        # Configuration pour interactions de type TradingView
                        dragmode='zoom',
                        selectdirection='h',  # 'h' pour horizontal
                        showlegend=True,
                    )
                    
                    # Configurer les interactions
                    fig.update_xaxes(
                        rangeslider_visible=False,  # Pas de rangeslider pour éviter l'encombrement
                        showspikes=True,
                        spikecolor="gray",
                        spikesnap="cursor",
                        spikemode="across",
                        spikethickness=1
                    )
                    
                    fig.update_yaxes(
                        showspikes=True,
                        spikecolor="gray",
                        spikethickness=1
                    )
                    
                    # Afficher le graphique avec configuration étendue
                    config = {
                        'displayModeBar': True,
                        'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape'],
                        'toImageButtonOptions': {
                            'format': 'png',
                            'filename': f'evolution_temporelle_{binary_display.lower().replace(" ", "_")}',
                            'height': 700,
                            'width': 1200,
                            'scale': 2
                        }
                    }
                    st.plotly_chart(fig, use_container_width=True, config=config)
                    
                    # Ajouter une légende des couleurs pour référence
                    if binary_display == "Superposées transparentes" and binary_metrics:
                        with st.expander("🎨 Guide du système de couches"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**📊 Couche de fond (Données continues):**")
                                st.markdown("- <span style='color:#2E86AB'>**Température Ambiante**</span> - Ligne pleine", unsafe_allow_html=True)
                                st.markdown("- <span style='color:#A23B72'>**Température Extérieure**</span> - Ligne pleine", unsafe_allow_html=True)
                                st.markdown("- <span style='color:#F18F01'>**Puissance IT**</span> - Ligne pleine", unsafe_allow_html=True)
                                st.markdown("- <span style='color:#C73E1D'>**Puissance Générale**</span> - Ligne pleine", unsafe_allow_html=True)
                                st.markdown("- <span style='color:#FF6B6B'>**Puissance CLIM**</span> - Ligne pleine", unsafe_allow_html=True)
                            with col2:
                                st.markdown("**🔧 Couche superposée (États binaires):**")
                                st.markdown("- <span style='color:#4ECDC4'>**CLIM A**</span> - Zones transparentes empilées", unsafe_allow_html=True)
                                st.markdown("- <span style='color:#45B7D1'>**CLIM B**</span> - Zones transparentes empilées", unsafe_allow_html=True)
                                st.markdown("- <span style='color:#96CEB4'>**CLIM C**</span> - Zones transparentes empilées", unsafe_allow_html=True)
                                st.markdown("- <span style='color:#FECA57'>**CLIM D**</span> - Zones transparentes empilées", unsafe_allow_html=True)
                                st.markdown("- <span style='color:#6C5CE7'>**Porte**</span> - Zones transparentes empilées", unsafe_allow_html=True)
                                st.markdown("\n**💡 Les zones colorées = ON, transparent = OFF**")
            else:
                st.info("Veuillez sélectionner au moins une métrique à afficher.")
        else:
            st.warning("Aucune donnée disponible pour la période sélectionnée.")
    else:
        st.error("Aucune donnée disponible.")

# 2. ANALYSE TEMPORELLE INTERACTIVE
with tab2:
    st.header("📈 Analyse temporelle interactive")
    
    # Display current unified period
    st.info(f"📅 Période sélectionnée: {start_date.strftime('%Y-%m-%d %H:%M')} - {end_date.strftime('%Y-%m-%d %H:%M')}")
    
    # Sélection des données
    # Multi-sélection des données à afficher
    available_metrics = {
        'Temp_Ambiante': '🌡️ Température Ambiante (°C)',
        'Temp_Exterieure': '🌤️ Température Extérieure (°C)',
        'Puissance_IT': '💻 Puissance IT (kW)',
        'Puissance_Generale': '⚡ Puissance Générale (kW)',
        'Puissance_CLIM': '❄️ Puissance CLIM (kW)',
        'CLIM_A_Status': '❄️ État CLIM A',
        'CLIM_B_Status': '❄️ État CLIM B',
        'CLIM_C_Status': '❄️ État CLIM C',
        'CLIM_D_Status': '❄️ État CLIM D',
        'Porte_Status': '🚪 État Porte'
    }
    
    # Filtrer les métriques disponibles
    available_cols = [col for col in available_metrics.keys() if col in filtered_merged_data.columns]
    
    selected_metrics = st.multiselect(
        "Sélectionner les données à afficher:",
        available_cols,
        default=available_cols[:3] if len(available_cols) >= 3 else available_cols,
        format_func=lambda x: available_metrics[x]
    )
    
    # Use unified filtered data
    if selected_metrics and not filtered_merged_data.empty:
        filtered_data = filtered_merged_data
        
        # Création du graphique interactif
        fig = make_subplots(
            rows=len(selected_metrics),
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=[available_metrics[m] for m in selected_metrics]
        )
        
        colors = px.colors.qualitative.Set3
        fill_colors = [
            'rgba(141, 211, 199, 0.3)',
            'rgba(255, 255, 179, 0.3)',
            'rgba(190, 186, 218, 0.3)',
            'rgba(251, 128, 114, 0.3)',
            'rgba(128, 177, 211, 0.3)',
            'rgba(253, 180, 98, 0.3)',
            'rgba(179, 222, 105, 0.3)',
            'rgba(252, 205, 229, 0.3)',
            'rgba(217, 217, 217, 0.3)',
            'rgba(188, 128, 189, 0.3)'
        ]
        
        for idx, metric in enumerate(selected_metrics):
            # Déterminer le type de graphique selon la métrique
            if 'Status' in metric:
                # Pour les statuts, utiliser un graphique en escalier
                fig.add_trace(
                    go.Scatter(
                        x=filtered_data['Timestamp'],
                        y=filtered_data[metric],
                        name=available_metrics[metric],
                        mode='lines',
                        line=dict(shape='hv', color=colors[idx % len(colors)]),
                        fill='tozeroy',
                        fillcolor=fill_colors[idx % len(fill_colors)]
                    ),
                    row=idx+1, col=1
                )
            else:
                # Pour les métriques continues
                fig.add_trace(
                    go.Scatter(
                        x=filtered_data['Timestamp'],
                        y=filtered_data[metric],
                        name=available_metrics[metric],
                        mode='lines',
                        line=dict(color=colors[idx % len(colors)], width=2),
                        hovertemplate='%{y:.2f}<br>%{x}<extra></extra>'
                    ),
                    row=idx+1, col=1
                )
            
            # Mise à jour des axes Y
            fig.update_yaxes(title_text=metric.split('_')[0], row=idx+1, col=1)
        
        # Mise à jour de la mise en page
        fig.update_layout(
            height=200 * len(selected_metrics),
            showlegend=False,
            hovermode='x unified',
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        fig.update_xaxes(title_text="Date et heure", row=len(selected_metrics), col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Options d'export
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("📊 Exporter en PNG"):
                fig.write_image("export_analyse_temporelle.png")
                st.success("Graphique exporté!")
        
        with col2:
            if st.button("📄 Exporter en CSV"):
                export_data = filtered_data[['Timestamp'] + selected_metrics]
                export_data.to_csv("export_donnees.csv", index=False)
                st.success("Données exportées!")
    
    # Profile Horaire Moyen Unifié
    st.subheader("📊 Profil Horaire Moyen Unifié")
    st.write("Visualisation comparative des profils horaires moyens pour Température Ambiante, Puissance IT et Température Extérieure")
    
    if not filtered_merged_data.empty:
        # Prepare hourly data for the three metrics
        hourly_data = filtered_merged_data.copy()
        hourly_data['Heure'] = hourly_data['Timestamp'].dt.hour
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Temperature Ambiante
        if 'Temp_Ambiante' in hourly_data.columns:
            hourly_avg_ambiante = hourly_data.groupby('Heure')['Temp_Ambiante'].agg(['mean', 'std']).reset_index()
            
            # Add mean line
            fig.add_trace(
                go.Scatter(
                    x=hourly_avg_ambiante['Heure'],
                    y=hourly_avg_ambiante['mean'],
                    mode='lines+markers',
                    name='Température Ambiante (°C)',
                    line=dict(color='#FF6B6B', width=3),
                    marker=dict(size=8),
                    yaxis='y'
                ),
                secondary_y=False
            )
            
            # Add std band
            fig.add_trace(
                go.Scatter(
                    x=list(hourly_avg_ambiante['Heure']) + list(hourly_avg_ambiante['Heure'][::-1]),
                    y=list(hourly_avg_ambiante['mean'] + hourly_avg_ambiante['std']) + list((hourly_avg_ambiante['mean'] - hourly_avg_ambiante['std'])[::-1]),
                    fill='toself',
                    fillcolor='rgba(255,107,107,0.15)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='± Écart-type Temp Ambiante',
                    showlegend=False,
                    yaxis='y'
                ),
                secondary_y=False
            )
        
        # Temperature Extérieure
        if 'Temp_Exterieure' in hourly_data.columns:
            hourly_avg_ext = hourly_data.groupby('Heure')['Temp_Exterieure'].agg(['mean', 'std']).reset_index()
            
            # Add mean line
            fig.add_trace(
                go.Scatter(
                    x=hourly_avg_ext['Heure'],
                    y=hourly_avg_ext['mean'],
                    mode='lines+markers',
                    name='Température Extérieure (°C)',
                    line=dict(color='#4ECDC4', width=3),
                    marker=dict(size=8),
                    yaxis='y'
                ),
                secondary_y=False
            )
            
            # Add std band
            fig.add_trace(
                go.Scatter(
                    x=list(hourly_avg_ext['Heure']) + list(hourly_avg_ext['Heure'][::-1]),
                    y=list(hourly_avg_ext['mean'] + hourly_avg_ext['std']) + list((hourly_avg_ext['mean'] - hourly_avg_ext['std'])[::-1]),
                    fill='toself',
                    fillcolor='rgba(78,205,196,0.15)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='± Écart-type Temp Extérieure',
                    showlegend=False,
                    yaxis='y'
                ),
                secondary_y=False
            )
        
        # Puissance IT (on secondary y-axis)
        if 'Puissance_IT' in hourly_data.columns:
            hourly_avg_it = hourly_data.groupby('Heure')['Puissance_IT'].agg(['mean', 'std']).reset_index()
            
            # Add mean line
            fig.add_trace(
                go.Scatter(
                    x=hourly_avg_it['Heure'],
                    y=hourly_avg_it['mean'],
                    mode='lines+markers',
                    name='Puissance IT (kW)',
                    line=dict(color='#6C5CE7', width=3, dash='dot'),
                    marker=dict(size=8, symbol='square'),
                    yaxis='y2'
                ),
                secondary_y=True
            )
            
            # Add std band
            fig.add_trace(
                go.Scatter(
                    x=list(hourly_avg_it['Heure']) + list(hourly_avg_it['Heure'][::-1]),
                    y=list(hourly_avg_it['mean'] + hourly_avg_it['std']) + list((hourly_avg_it['mean'] - hourly_avg_it['std'])[::-1]),
                    fill='toself',
                    fillcolor='rgba(108,92,231,0.15)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='± Écart-type Puissance IT',
                    showlegend=False,
                    yaxis='y2'
                ),
                secondary_y=True
            )
        
        # Update layout
        fig.update_xaxes(
            title_text="Heure de la journée",
            tickmode='linear',
            tick0=0,
            dtick=2,
            range=[-0.5, 23.5]
        )
        
        fig.update_yaxes(
            title_text="Température (°C)",
            secondary_y=False,
            gridcolor='rgba(128,128,128,0.2)'
        )
        
        fig.update_yaxes(
            title_text="Puissance IT (kW)",
            secondary_y=True,
            gridcolor='rgba(128,128,128,0.1)'
        )
        
        fig.update_layout(
            title="Profil Horaire Moyen - Vue Comparative",
            height=500,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            template='plotly_white',
            margin=dict(l=50, r=50, t=50, b=100)
        )
        
        # Add grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insights
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'Temp_Ambiante' in hourly_data.columns:
                peak_hour_amb = hourly_avg_ambiante.loc[hourly_avg_ambiante['mean'].idxmax(), 'Heure']
                peak_temp_amb = hourly_avg_ambiante['mean'].max()
                st.metric(
                    "🌡️ Pic Temp Ambiante",
                    f"{peak_temp_amb:.1f}°C",
                    f"à {int(peak_hour_amb)}h"
                )
        
        with col2:
            if 'Puissance_IT' in hourly_data.columns:
                peak_hour_it = hourly_avg_it.loc[hourly_avg_it['mean'].idxmax(), 'Heure']
                peak_power_it = hourly_avg_it['mean'].max()
                st.metric(
                    "💻 Pic Puissance IT",
                    f"{peak_power_it:.1f} kW",
                    f"à {int(peak_hour_it)}h"
                )
        
        with col3:
            if 'Temp_Exterieure' in hourly_data.columns:
                peak_hour_ext = hourly_avg_ext.loc[hourly_avg_ext['mean'].idxmax(), 'Heure']
                peak_temp_ext = hourly_avg_ext['mean'].max()
                st.metric(
                    "🌤️ Pic Temp Extérieure",
                    f"{peak_temp_ext:.1f}°C",
                    f"à {int(peak_hour_ext)}h"
                )

# 3. ANALYSES EDA
with tab3:
    st.header("🔬 Analyses exploratoires (EDA)")
    
    # Display current unified period
    st.info(f"📅 Période sélectionnée: {start_date.strftime('%Y-%m-%d %H:%M')} - {end_date.strftime('%Y-%m-%d %H:%M')}")
    
    if not filtered_merged_data.empty and 'Timestamp' in filtered_merged_data.columns:
        # Sélection des métriques (multi-sélection)
        numeric_cols = ['Temp_Ambiante', 'Temp_Exterieure', 'Puissance_IT', 
                       'Puissance_Generale', 'Puissance_CLIM']
        available_numeric = [col for col in numeric_cols if col in filtered_merged_data.columns]
        
        metric_labels = {
            'Temp_Ambiante': '🌡️ Température Ambiante',
            'Temp_Exterieure': '🌤️ Température Extérieure',
            'Puissance_IT': '💻 Puissance IT',
            'Puissance_Generale': '⚡ Puissance Générale',
            'Puissance_CLIM': '❄️ Puissance CLIM'
        }
        
        selected_metrics = st.multiselect(
            "Sélectionner les métriques à analyser:",
            available_numeric,
            default=[available_numeric[0]] if available_numeric else [],
            format_func=lambda x: metric_labels.get(x, x)
        )
        
        # Use unified filtered data
        filtered_data = filtered_merged_data
    
        
        # Afficher les analyses pour chaque métrique sélectionnée
        if selected_metrics and not filtered_data.empty:
            for metric in selected_metrics:
                st.markdown("---")
                st.subheader(f"📊 Analyse complète: {metric_labels.get(metric, metric)}")
                
                # Vérifier la disponibilité des données
                metric_data = filtered_data[metric].dropna()
                if len(metric_data) == 0:
                    st.warning(f"Aucune donnée disponible pour {metric_labels.get(metric, metric)} dans la période sélectionnée.")
                    continue
                
                # 1. STATISTIQUES GÉNÉRALES
                with st.expander(f"📈 Statistiques et informations - {metric_labels.get(metric, metric)}", expanded=True):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown("**Informations générales**")
                        total_points = len(filtered_data)
                        valid_points = len(metric_data)
                        missing_points = total_points - valid_points
                        
                        st.metric("Points totaux", f"{total_points:,}")
                        st.metric("Points valides", f"{valid_points:,}")
                        st.metric("Données manquantes", f"{missing_points:,} ({missing_points/total_points*100:.1f}%)")
                    
                    with col2:
                        st.markdown("**Statistiques descriptives**")
                        stats_data = {
                            'Statistique': ['Minimum', 'Maximum', 'Moyenne', 'Médiane', 'Écart-type', 'Asymétrie', 'Aplatissement'],
                            'Valeur': [
                                f"{metric_data.min():.2f}",
                                f"{metric_data.max():.2f}",
                                f"{metric_data.mean():.2f}",
                                f"{metric_data.median():.2f}",
                                f"{metric_data.std():.2f}",
                                f"{stats.skew(metric_data):.2f}",
                                f"{stats.kurtosis(metric_data):.2f}"
                            ]
                        }
                        st.dataframe(pd.DataFrame(stats_data), hide_index=True, use_container_width=True)
                
                # 2. VISUALISATIONS DE DISTRIBUTION
                st.markdown(f"#### 📊 Distribution - {metric_labels.get(metric, metric)}")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Histogramme avec KDE
                    fig_hist = go.Figure()
                    
                    # Histogramme
                    fig_hist.add_trace(go.Histogram(
                        x=metric_data,
                        name='Fréquence',
                        nbinsx=30,
                        marker_color='lightblue',
                        opacity=0.7
                    ))
                    
                    # KDE
                    kde_x = np.linspace(metric_data.min(), metric_data.max(), 100)
                    kde = stats.gaussian_kde(metric_data)
                    kde_y = kde(kde_x) * len(metric_data) * (metric_data.max() - metric_data.min()) / 30
                    
                    fig_hist.add_trace(go.Scatter(
                        x=kde_x,
                        y=kde_y,
                        mode='lines',
                        name='Densité (KDE)',
                        line=dict(color='red', width=2),
                        yaxis='y2'
                    ))
                    
                    fig_hist.update_layout(
                        title=f"Histogramme - {metric}",
                        xaxis_title=metric,
                        yaxis_title="Fréquence",
                        yaxis2=dict(overlaying='y', side='right', title='Densité'),
                        height=400,
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                with col2:
                    # Boîte à moustaches
                    fig_box = go.Figure()
                    fig_box.add_trace(go.Box(
                        y=metric_data,
                        name=metric,
                        boxpoints='outliers',
                        marker_color='lightcoral',
                        line_color='darkred'
                    ))
                    
                    fig_box.update_layout(
                        title=f"Boîte à moustaches - {metric}",
                        yaxis_title=metric,
                        height=400
                    )
                    
                    st.plotly_chart(fig_box, use_container_width=True)
                    
                    # Statistiques des quartiles
                    q1 = metric_data.quantile(0.25)
                    q3 = metric_data.quantile(0.75)
                    iqr = q3 - q1
                    
                    st.caption("**Quartiles:**")
                    st.caption(f"Q1 (25%): {q1:.2f} | Q3 (75%): {q3:.2f} | IQR: {iqr:.2f}")
                
                # 3. ANALYSES TEMPORELLES
                st.markdown(f"#### 📈 Analyses temporelles - {metric_labels.get(metric, metric)}")
                
                # Série temporelle brute
                with st.expander("Série temporelle complète", expanded=True):
                    fig_ts = go.Figure()
                    fig_ts.add_trace(go.Scatter(
                        x=filtered_data['Timestamp'],
                        y=filtered_data[metric],
                        mode='lines',
                        name=metric,
                        line=dict(color='green', width=1)
                    ))
                    
                    fig_ts.update_layout(
                        title=f"Évolution temporelle - {metric}",
                        xaxis_title="Date et heure",
                        yaxis_title=metric,
                        height=400,
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig_ts, use_container_width=True)
                
                # Moyennes journalières et profil horaire côte à côte
                col1, col2 = st.columns(2)
                
                with col1:
                    # Moyennes journalières
                    daily_data = filtered_data.copy()
                    daily_data['Date'] = daily_data['Timestamp'].dt.date
                    daily_avg = daily_data.groupby('Date')[metric].mean().reset_index()
                    
                    if len(daily_avg) > 0:
                        fig_daily = go.Figure()
                        fig_daily.add_trace(go.Scatter(
                            x=daily_avg['Date'],
                            y=daily_avg[metric],
                            mode='lines+markers',
                            name='Moyenne journalière',
                            line=dict(color='blue', width=2),
                            marker=dict(size=6)
                        ))
                        
                        fig_daily.update_layout(
                            title=f"Moyennes journalières - {metric}",
                            xaxis_title="Date",
                            yaxis_title=f"Moyenne {metric}",
                            height=350
                        )
                        
                        st.plotly_chart(fig_daily, use_container_width=True)
                
                with col2:
                    # Profil horaire
                    hourly_data = filtered_data.copy()
                    hourly_data['Heure'] = hourly_data['Timestamp'].dt.hour
                    hourly_avg = hourly_data.groupby('Heure')[metric].agg(['mean', 'std']).reset_index()
                    
                    if len(hourly_avg) > 0:
                        fig_hourly = go.Figure()
                        
                        # Moyenne
                        fig_hourly.add_trace(go.Scatter(
                            x=hourly_avg['Heure'],
                            y=hourly_avg['mean'],
                            mode='lines+markers',
                            name='Moyenne',
                            line=dict(color='darkblue', width=3),
                            marker=dict(size=8)
                        ))
                        
                        # Bande d'écart-type
                        fig_hourly.add_trace(go.Scatter(
                            x=list(hourly_avg['Heure']) + list(hourly_avg['Heure'][::-1]),
                            y=list(hourly_avg['mean'] + hourly_avg['std']) + list((hourly_avg['mean'] - hourly_avg['std'])[::-1]),
                            fill='toself',
                            fillcolor='rgba(0,100,250,0.2)',
                            line=dict(color='rgba(255,255,255,0)'),
                            name='± Écart-type',
                            showlegend=True
                        ))
                        
                        fig_hourly.update_layout(
                            title=f"Profil horaire moyen - {metric}",
                            xaxis_title="Heure",
                            yaxis_title=metric,
                            height=350,
                            xaxis=dict(tickmode='linear', tick0=0, dtick=2)
                        )
                        
                        st.plotly_chart(fig_hourly, use_container_width=True)
        
        elif not selected_metrics:
            st.info("👆 Veuillez sélectionner au moins une métrique à analyser.")
        else:
            st.warning("Aucune donnée disponible pour la période sélectionnée.")
    
    else:
        st.error("Aucune donnée disponible.")

# 4. ANALYSE CLIM
with tab4:
    st.header("❄️ Analyse de l'impact des CLIMs sur la température")
    st.info(f"📅 Période sélectionnée: {start_date.strftime('%Y-%m-%d %H:%M')} - {end_date.strftime('%Y-%m-%d %H:%M')}")
    
    # Préparer les données CLIM
    clim_columns = [col for col in filtered_merged_data.columns if 'CLIM' in col and 'Status' in col]
    
    if clim_columns and 'Temp_Ambiante' in filtered_merged_data.columns:
        # Info sur les données disponibles
        st.info(f"**CLIMs détectées:** {', '.join(clim_columns)}")
        
        # Vérifier l'état des CLIMs
        clim_status_summary = []
        for clim in clim_columns:
            if clim in filtered_merged_data.columns:
                total_points = len(filtered_merged_data)
                on_points = (filtered_merged_data[clim] == 1).sum()
                off_points = (filtered_merged_data[clim] == 0).sum()
                clim_status_summary.append({
                    'CLIM': clim,
                    'Total Points': total_points,
                    'ON': on_points,
                    'OFF': off_points,
                    '% ON': (on_points / total_points * 100) if total_points > 0 else 0
                })
        
        if clim_status_summary:
            df_clim_summary = pd.DataFrame(clim_status_summary)
            st.dataframe(df_clim_summary.style.format({
                '% ON': '{:.1f}%'
            }), use_container_width=True)
        
        # Analyse de la température après arrêt CLIM
        st.subheader("📉 Évolution de la température après arrêt des CLIMs")
        
        # Paramètres
        col1, col2 = st.columns(2)
        with col1:
            minutes_after = st.slider("Minutes après l'arrêt", 5, 60, 30, 5)
        with col2:
            selected_clim = st.selectbox("Sélectionner un CLIM", clim_columns)
        
        # Détecter les arrêts de CLIM (passage de 1 à 0)
        filtered_merged_data['CLIM_Stop'] = (filtered_merged_data[selected_clim].shift(1) == 1) & (filtered_merged_data[selected_clim] == 0)
        
        # Points d'arrêt
        stop_points = filtered_merged_data[filtered_merged_data['CLIM_Stop']]['Timestamp'].tolist()
        
        # Debug info
        with st.expander("🔍 Informations de débogage"):
            st.write(f"Total de points de données: {len(filtered_merged_data)}")
            st.write(f"Points avec température valide: {filtered_merged_data['Temp_Ambiante'].notna().sum()}")
            st.write(f"Valeurs uniques de {selected_clim}: {filtered_merged_data[selected_clim].value_counts().to_dict()}")
            st.write(f"Transitions détectées (1→0): {len(stop_points)}")
            if stop_points:
                st.write(f"Premiers arrêts: {[t.strftime('%Y-%m-%d %H:%M') for t in stop_points[:5]]}")
        
        if stop_points:
            # Analyser chaque arrêt
            temp_changes = []
            
            st.write(f"**{len(stop_points)} arrêts détectés pour {selected_clim}**")
            st.write(f"**Analyse de tous les {len(stop_points)} arrêts...**")
            
            # Progress bar for large datasets
            progress_bar = st.progress(0)
            
            for i, stop_time in enumerate(stop_points):  # Analyser tous les événements
                # Température au moment de l'arrêt
                temp_at_stop_idx = filtered_merged_data[filtered_merged_data['Timestamp'] <= stop_time]['Temp_Ambiante'].last_valid_index()
                
                if temp_at_stop_idx is not None:
                    temp_at_stop = filtered_merged_data.loc[temp_at_stop_idx, 'Temp_Ambiante']
                    
                    # Température après X minutes
                    time_after = stop_time + timedelta(minutes=minutes_after)
                    after_mask = (filtered_merged_data['Timestamp'] > stop_time) & \
                                (filtered_merged_data['Timestamp'] <= time_after)
                    temps_after = filtered_merged_data[after_mask]['Temp_Ambiante'].dropna()
                    
                    if len(temps_after) > 0:
                        # Prendre la dernière température dans la fenêtre
                        temp_final = temps_after.iloc[-1]
                        temp_change = temp_final - temp_at_stop
                        
                        temp_changes.append({
                            'Timestamp': stop_time,
                            'Temp_Initial': temp_at_stop,
                            'Temp_Final': temp_final,
                            'Delta_Temp': temp_change,
                            'CLIM': selected_clim,
                            'Duration_min': minutes_after,
                            'Num_Points': len(temps_after)
                        })
                    else:
                        # Même si pas de données après, enregistrer ce qu'on a
                        temp_changes.append({
                            'Timestamp': stop_time,
                            'Temp_Initial': temp_at_stop,
                            'Temp_Final': temp_at_stop,  # Pas de changement
                            'Delta_Temp': 0.0,
                            'CLIM': selected_clim,
                            'Duration_min': minutes_after,
                            'Num_Points': 0
                        })
                
                # Update progress bar
                progress_bar.progress((i + 1) / len(stop_points))
            
            # Clear progress bar
            progress_bar.empty()
            
            st.write(f"**Cycles valides trouvés:** {len(temp_changes)}")
            
            if temp_changes:
                # Graphique des changements de température
                df_changes = pd.DataFrame(temp_changes)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_changes.index,
                    y=df_changes['Delta_Temp'],
                    mode='markers',
                    marker=dict(
                        size=10,
                        color=df_changes['Delta_Temp'],
                        colorscale='RdYlBu_r',
                        showscale=True,
                        colorbar=dict(title="ΔT (°C)")
                    ),
                    text=[f"Arrêt: {t.strftime('%Y-%m-%d %H:%M')}<br>ΔT: {d:.2f}°C" 
                          for t, d in zip(df_changes['Timestamp'], df_changes['Delta_Temp'])],
                    hovertemplate='%{text}<extra></extra>'
                ))
                
                # Ligne de référence à zéro
                fig.add_hline(y=0, line_dash="dash", line_color="gray")
                
                # Ligne de tendance moyenne
                avg_change = df_changes['Delta_Temp'].mean()
                fig.add_hline(y=avg_change, line_dash="solid", line_color="red",
                            annotation_text=f"Moyenne: {avg_change:.2f}°C")
                
                fig.update_layout(
                    title=f"Changement de température {minutes_after} min après arrêt - {selected_clim}",
                    xaxis_title="Événement d'arrêt",
                    yaxis_title="Changement de température (°C)",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Tableau récapitulatif détaillé
                st.subheader("📊 Résumé statistique complet")
                
                # Première ligne de métriques
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("ΔT Moyen", f"{df_changes['Delta_Temp'].mean():.2f}°C")
                with col2:
                    st.metric("ΔT Médian", f"{df_changes['Delta_Temp'].median():.2f}°C")
                with col3:
                    st.metric("ΔT Min", f"{df_changes['Delta_Temp'].min():.2f}°C")
                with col4:
                    st.metric("ΔT Max", f"{df_changes['Delta_Temp'].max():.2f}°C")
                with col5:
                    st.metric("Écart-type", f"{df_changes['Delta_Temp'].std():.2f}°C")
                
                # Deuxième ligne de métriques
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Amplitude", f"{df_changes['Delta_Temp'].max() - df_changes['Delta_Temp'].min():.2f}°C")
                with col2:
                    positive_changes = df_changes[df_changes['Delta_Temp'] > 0]
                    st.metric("Augmentations", f"{len(positive_changes)} ({len(positive_changes)/len(df_changes)*100:.1f}%)")
                with col3:
                    negative_changes = df_changes[df_changes['Delta_Temp'] < 0]
                    st.metric("Diminutions", f"{len(negative_changes)} ({len(negative_changes)/len(df_changes)*100:.1f}%)")
                with col4:
                    zero_changes = df_changes[df_changes['Delta_Temp'] == 0]
                    st.metric("Sans changement", f"{len(zero_changes)} ({len(zero_changes)/len(df_changes)*100:.1f}%)")
                
                # Tableau détaillé de tous les événements
                st.subheader("📋 Détail de tous les arrêts CLIM")
                
                # Préparer les données pour l'affichage
                display_df = df_changes.copy()
                display_df['Timestamp'] = display_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
                display_df['Temp_Initial'] = display_df['Temp_Initial'].round(2)
                display_df['Temp_Final'] = display_df['Temp_Final'].round(2)
                display_df['Delta_Temp'] = display_df['Delta_Temp'].round(2)
                
                # Ajouter une colonne pour l'index
                display_df.insert(0, 'N°', range(1, len(display_df) + 1))
                
                # Renommer les colonnes pour l'affichage
                display_df = display_df.rename(columns={
                    'Timestamp': 'Date/Heure arrêt',
                    'Temp_Initial': 'T° initiale (°C)',
                    'Temp_Final': f'T° après {minutes_after}min (°C)',
                    'Delta_Temp': 'ΔT (°C)',
                    'Num_Points': 'Points de données'
                })
                
                # Sélectionner les colonnes à afficher
                columns_to_display = ['N°', 'Date/Heure arrêt', 'T° initiale (°C)', 
                                     f'T° après {minutes_after}min (°C)', 'ΔT (°C)', 'Points de données']
                
                # Utiliser un expander si il y a beaucoup d'événements
                if len(display_df) > 20:
                    with st.expander(f"Voir tous les {len(display_df)} événements"):
                        st.dataframe(
                            display_df[columns_to_display],
                            use_container_width=True,
                            hide_index=True
                        )
                else:
                    st.dataframe(
                        display_df[columns_to_display],
                        use_container_width=True,
                        hide_index=True
                    )
                
                # Bouton pour télécharger les données
                csv = display_df[columns_to_display].to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Télécharger les données en CSV",
                    data=csv,
                    file_name=f"analyse_arrets_{selected_clim}_{minutes_after}min.csv",
                    mime="text/csv"
                )
                
                # Visualisations supplémentaires des distributions
                st.subheader("📊 Distribution des changements de température")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Histogramme des changements de température
                    fig_hist = go.Figure()
                    fig_hist.add_trace(go.Histogram(
                        x=df_changes['Delta_Temp'],
                        nbinsx=20,
                        name='Distribution',
                        marker_color='lightblue',
                        opacity=0.7
                    ))
                    
                    # Ajouter une ligne verticale pour la moyenne
                    mean_delta = df_changes['Delta_Temp'].mean()
                    fig_hist.add_vline(x=mean_delta, line_dash="dash", line_color="red",
                                      annotation_text=f"Moyenne: {mean_delta:.2f}°C")
                    
                    # Ajouter une ligne verticale pour la médiane
                    median_delta = df_changes['Delta_Temp'].median()
                    fig_hist.add_vline(x=median_delta, line_dash="dot", line_color="green",
                                      annotation_text=f"Médiane: {median_delta:.2f}°C")
                    
                    fig_hist.update_layout(
                        title="Histogramme des ΔT",
                        xaxis_title="Changement de température (°C)",
                        yaxis_title="Fréquence",
                        showlegend=False,
                        height=400
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                with col2:
                    # Box plot des changements de température
                    fig_box = go.Figure()
                    fig_box.add_trace(go.Box(
                        y=df_changes['Delta_Temp'],
                        name='ΔT',
                        boxpoints='outliers',
                        marker_color='lightgreen',
                        line_color='darkgreen'
                    ))
                    
                    fig_box.update_layout(
                        title="Box Plot des ΔT",
                        yaxis_title="Changement de température (°C)",
                        showlegend=False,
                        height=400
                    )
                    
                    # Ajouter des annotations pour les quartiles
                    q1 = df_changes['Delta_Temp'].quantile(0.25)
                    q3 = df_changes['Delta_Temp'].quantile(0.75)
                    iqr = q3 - q1
                    
                    fig_box.add_annotation(
                        x=0.5, y=q1,
                        text=f"Q1: {q1:.2f}°C",
                        showarrow=True,
                        arrowhead=2,
                        xref="paper"
                    )
                    
                    fig_box.add_annotation(
                        x=0.5, y=q3,
                        text=f"Q3: {q3:.2f}°C",
                        showarrow=True,
                        arrowhead=2,
                        xref="paper"
                    )
                    
                    st.plotly_chart(fig_box, use_container_width=True)
                
                # Graphique temporel
                st.subheader("📈 Évolution temporelle de la température")
                
                # Sélectionner un événement à visualiser
                event_idx = st.selectbox(
                    "Sélectionner un arrêt à visualiser",
                    range(len(df_changes)),
                    format_func=lambda x: f"Arrêt {x+1} - {df_changes.iloc[x]['Timestamp'].strftime('%Y-%m-%d %H:%M')} (ΔT: {df_changes.iloc[x]['Delta_Temp']:.2f}°C)"
                )
                
                if event_idx is not None:
                    selected_event = df_changes.iloc[event_idx]
                    stop_time = selected_event['Timestamp']
                    
                    # Récupérer les données pour visualiser
                    viz_start = stop_time - timedelta(minutes=15)
                    viz_end = stop_time + timedelta(minutes=minutes_after + 10)
                    
                    viz_mask = (filtered_merged_data['Timestamp'] >= viz_start) & \
                              (filtered_merged_data['Timestamp'] <= viz_end)
                    viz_data = filtered_merged_data[viz_mask].copy()
                    
                    if len(viz_data) > 0:
                        fig_timeline = go.Figure()
                        
                        # Température
                        fig_timeline.add_trace(go.Scatter(
                            x=viz_data['Timestamp'],
                            y=viz_data['Temp_Ambiante'],
                            mode='lines',
                            name='Température',
                            line=dict(color='red', width=2)
                        ))
                        
                        # État du CLIM
                        fig_timeline.add_trace(go.Scatter(
                            x=viz_data['Timestamp'],
                            y=viz_data[selected_clim] * viz_data['Temp_Ambiante'].max() * 0.95,
                            mode='lines',
                            name=f'{selected_clim} (ON/OFF)',
                            line=dict(color='blue', width=2, dash='dash'),
                            yaxis='y2'
                        ))
                        
                        # Marquer l'arrêt avec add_shape au lieu de add_vline
                        fig_timeline.add_shape(
                            type="line",
                            x0=stop_time, x1=stop_time,
                            y0=0, y1=1,
                            yref="paper",
                            line=dict(color="green", width=2, dash="dash")
                        )
                        fig_timeline.add_annotation(
                            x=stop_time,
                            y=1.05,
                            yref="paper",
                            text="Arrêt CLIM",
                            showarrow=False
                        )
                        
                        # Marquer la fin de la fenêtre d'analyse
                        end_time = stop_time + timedelta(minutes=minutes_after)
                        fig_timeline.add_shape(
                            type="line",
                            x0=end_time, x1=end_time,
                            y0=0, y1=1,
                            yref="paper",
                            line=dict(color="orange", width=1, dash="dot")
                        )
                        fig_timeline.add_annotation(
                            x=end_time,
                            y=1.05,
                            yref="paper",
                            text=f"+{minutes_after} min",
                            showarrow=False
                        )
                        
                        fig_timeline.update_layout(
                            title=f"Évolution autour de l'arrêt du {stop_time.strftime('%Y-%m-%d %H:%M')}",
                            xaxis_title="Temps",
                            yaxis_title="Température (°C)",
                            yaxis2=dict(
                                title="État CLIM",
                                overlaying='y',
                                side='right',
                                showticklabels=False
                            ),
                            height=400
                        )
                        
                        st.plotly_chart(fig_timeline, use_container_width=True)
                
                # Tableau détaillé
                with st.expander("📋 Voir le détail des événements"):
                    st.dataframe(
                        df_changes.style.format({
                            'Temp_Initial': '{:.1f}°C',
                            'Temp_Final': '{:.1f}°C',
                            'Delta_Temp': '{:.2f}°C'
                        })
                    )
            else:
                st.info(f"Aucun changement de température mesuré après les arrêts de {selected_clim}.")
        else:
            st.warning(f"Aucun arrêt détecté pour {selected_clim} dans la période sélectionnée.")

# 5. INCIDENT LENS
with tab5:
    st.header("🚪 Analyse de l'impact de l'ouverture de porte")
    
    # Explication d'un cycle
    st.info("💡 **Qu'est-ce qu'un cycle ?** Un cycle correspond à une séquence complète d'ouverture et de fermeture de la porte. Il commence quand la porte passe de l'état fermé à ouvert, et se termine quand elle revient à l'état fermé. L'analyse suit l'évolution de la température pendant chaque cycle.")
    
    if 'Porte_Status' in filtered_merged_data.columns and 'Temp_Ambiante' in merged_data.columns:
        # Informations sur les données de porte
        st.subheader("📊 État actuel des données de porte")
        
        porte_data_raw = filtered_merged_data[['Timestamp', 'Porte_Status', 'Temp_Ambiante']].copy()
        
        # Statistiques des données de porte
        open_records = porte_data_raw['Porte_Status'].notna().sum()
        st.metric("Événements d'ouverture", open_records)
        
        # Afficher un échantillon des données de porte
        st.subheader("🔍 Échantillon des événements d'ouverture")
        door_events = porte_data_raw[porte_data_raw['Porte_Status'].notna()].copy()
        if not door_events.empty:
            st.dataframe(door_events.head(20), use_container_width=True)
            
            # Debug: Afficher les données brutes de porte avant traitement
            with st.expander("🔍 Debug - Données de porte brutes (non-NaN uniquement)"):
                st.write(f"Nombre d'entrées non-NaN: {len(door_events)}")
                st.write(f"Valeurs uniques dans Porte_Status: {door_events['Porte_Status'].unique()}")
                st.write(f"Nombre de 1 (ouvert): {(door_events['Porte_Status'] == 1).sum()}")
                st.write(f"Nombre de 0 (fermé): {(door_events['Porte_Status'] == 0).sum()}")
                
                # Afficher les transitions dans les données brutes
                door_events_sorted = door_events.sort_values('Timestamp')
                door_events_sorted['Status_Change'] = door_events_sorted['Porte_Status'] != door_events_sorted['Porte_Status'].shift(1)
                transitions = door_events_sorted[door_events_sorted['Status_Change']]
                st.write(f"\nTransitions dans les données brutes: {len(transitions)}")
                if len(transitions) > 0:
                    st.dataframe(transitions[['Timestamp', 'Porte_Status']].head(20))
            
            # Fonction robuste de détection des cycles de porte
            def detect_door_cycles(
                    df,
                    ts_col='Timestamp',
                    status_col='Porte_Status',
                    min_duration_sec=5,
                    max_duration_hours=24,
                    assume_close_at_end=True
                ):
                """
                Détecte les cycles d'ouverture/fermeture de porte.
                Approche simple: chaque "Ouverte" est appariée avec le prochain "Fermé".
                """
                # Copie pour éviter de modifier l'original
                df_proc = df.copy()
                
                # 1. Sort by timestamp
                df_proc = df_proc.sort_values(ts_col).reset_index(drop=True)
                
                # 2. Convertir le statut en valeur numérique (1=ouvert, 0=fermé)
                if pd.api.types.is_string_dtype(df_proc[status_col]):
                    # Gérer les statuts textuels en français
                    clean_status = df_proc[status_col].str.strip().str.lower()
                    status_map = {
                        'ouverte': 1, 
                        'ouvert': 1, 
                        'fermé': 0, 
                        'ferme': 0,
                        'fermée': 0
                    }
                    df_proc['state'] = clean_status.map(status_map)
                    df_proc['state'] = df_proc['state'].fillna(0)
                else:
                    # Gérer les données numériques
                    df_proc['state'] = pd.to_numeric(df_proc[status_col], errors='coerce').fillna(0)
                
                df_proc['state'] = df_proc['state'].astype(int)
                
                # 3. Algorithme corrigé: parcourir et apparier en sautant les ouvertures consécutives
                cycles_list = []
                i = 0
                
                while i < len(df_proc):
                    # Chercher une ouverture
                    if df_proc.iloc[i]['state'] == 1 and pd.notna(df_proc.iloc[i][ts_col]):
                        open_time = df_proc.iloc[i][ts_col]
                        open_idx = i
                        
                        # Sauter toutes les ouvertures consécutives
                        j = i + 1
                        while j < len(df_proc) and df_proc.iloc[j]['state'] == 1:
                            j += 1
                        
                        # Maintenant j pointe soit sur un 'Fermé' soit sur la fin des données
                        close_time = None
                        close_idx = None
                        
                        if j < len(df_proc) and df_proc.iloc[j]['state'] == 0:
                            close_time = df_proc.iloc[j][ts_col]
                            close_idx = j
                        
                        # Si pas de fermeture trouvée
                        if close_time is None or pd.isna(close_time):
                            if assume_close_at_end and pd.notna(open_time):
                                # Utiliser le dernier timestamp + 30 min ou la durée max
                                last_time = df_proc.iloc[-1][ts_col]
                                if pd.notna(last_time):
                                    duration_to_last = (last_time - open_time).total_seconds()
                                    
                                    if duration_to_last > max_duration_hours * 3600:
                                        close_time = open_time + pd.Timedelta(hours=max_duration_hours)
                                    else:
                                        close_time = last_time + pd.Timedelta(minutes=30)
                                else:
                                    close_time = open_time + pd.Timedelta(minutes=30)
                                
                                # Créer le cycle avec fermeture assumée
                                duration_sec = (close_time - open_time).total_seconds()
                                if duration_sec >= min_duration_sec:
                                    cycles_list.append({
                                        'open_ts': open_time,
                                        'close_ts': close_time,
                                        'duration_sec': duration_sec
                                    })
                            
                            # Passer au-delà de toutes les ouvertures
                            i = j
                        else:
                            # Calculer la durée
                            if pd.notna(open_time) and pd.notna(close_time):
                                duration_sec = (close_time - open_time).total_seconds()
                                
                                # Ajouter le cycle si la durée est valide
                                if duration_sec >= min_duration_sec:
                                    cycles_list.append({
                                        'open_ts': open_time,
                                        'close_ts': close_time,
                                        'duration_sec': duration_sec
                                    })
                            
                            # Continuer après l'événement de fermeture
                            i = close_idx + 1 if close_idx is not None else j
                    else:
                        i += 1
                
                # 4. Créer le DataFrame des cycles
                cycles_df = pd.DataFrame(cycles_list)
                
                if len(cycles_df) == 0:
                    cycles_df = pd.DataFrame(columns=['open_ts', 'close_ts', 'duration_sec'])
                
                # 5. Debug info (optional)
                # print(f"[DEBUG] Total records: {len(df_proc)}, Open events: {(df_proc['state'] == 1).sum()}, Cycles found: {len(cycles_df)}")
                
                # Store debug info for display
                cycles_df.attrs['debug_df'] = df_proc[[ts_col, status_col, 'state']].head(100)
                
                return cycles_df
            
            # Paramètres de détection ajustables
            st.subheader("⚙️ Paramètres de détection des cycles")
            col1, col2, col3 = st.columns(3)
            with col1:
                min_duration = st.number_input(
                    "Durée min (secondes)", 
                    min_value=0, 
                    max_value=3600, 
                    value=0,
                    help="Durée minimale pour qu'un cycle soit considéré valide (0 = pas de filtre)"
                )
            with col2:
                max_duration = st.number_input(
                    "Durée max (heures)", 
                    min_value=1, 
                    max_value=48, 
                    value=24,
                    help="Durée maximale d'un cycle"
                )
            with col3:
                detection_mode = st.selectbox(
                    "Mode de détection",
                    ["Automatique", "Événements individuels", "Groupes stricts"],
                    help="Automatique: s'adapte aux données. Événements: chaque entrée 'Ouverte' est un cycle. Groupes: transitions uniquement."
                )
            
            # Vérifier les données avant d'appeler la fonction
            with st.expander("🔍 Debug - Analyse détaillée des données de porte", expanded=False):
                st.write("### Données brutes")
                st.write(f"- Shape: {porte_data_raw.shape}")
                st.write(f"- Colonnes: {porte_data_raw.columns.tolist()}")
                
                # Analyser les valeurs de Porte_Status
                st.write("\n### Analyse de Porte_Status")
                st.write(f"- Type de données: {porte_data_raw['Porte_Status'].dtype}")
                st.write(f"- Nombre total de valeurs: {len(porte_data_raw)}")
                st.write(f"- Valeurs non-NaN: {porte_data_raw['Porte_Status'].notna().sum()}")
                st.write(f"- Valeurs NaN: {porte_data_raw['Porte_Status'].isna().sum()}")
                
                # Filtrer les NaN
                porte_data_clean = porte_data_raw[porte_data_raw['Porte_Status'].notna()].copy()
                
                if len(porte_data_clean) > 0:
                    st.write(f"\n### Après filtrage des NaN: {len(porte_data_clean)} lignes")
                    unique_vals = porte_data_clean['Porte_Status'].unique()
                    st.write(f"- Valeurs uniques: {sorted(unique_vals)}")
                    
                    # Si les valeurs sont du texte, afficher le mapping
                    if pd.api.types.is_string_dtype(porte_data_clean['Porte_Status']):
                        st.write("\n### Mapping des valeurs textuelles:")
                        st.write("- 'Ouverte' → 1 (porte ouverte)")
                        st.write("- 'Fermé' → 0 (porte fermée)")
                    
                    # Distribution des valeurs
                    value_counts = porte_data_clean['Porte_Status'].value_counts().sort_index()
                    st.write("\n### Distribution des valeurs:")
                    for val, count in value_counts.items():
                        st.write(f"  - {val}: {count} ({count/len(porte_data_clean)*100:.1f}%)")
                    
                    # Vérifier les transitions
                    porte_sorted = porte_data_clean.sort_values('Timestamp').copy()
                    porte_sorted['prev_status'] = porte_sorted['Porte_Status'].shift(1)
                    transitions = porte_sorted[porte_sorted['Porte_Status'] != porte_sorted['prev_status']]
                    
                    st.write(f"\n### Transitions détectées: {len(transitions)}")
                    if len(transitions) > 0:
                        st.write("Premières transitions:")
                        st.dataframe(transitions[['Timestamp', 'prev_status', 'Porte_Status']].head(10))
                        
                        # Calculer les durées entre transitions
                        transitions['time_diff'] = transitions['Timestamp'].diff().dt.total_seconds()
                        st.write(f"\n### Durées entre transitions (secondes):")
                        st.write(f"- Moyenne: {transitions['time_diff'].mean():.1f}s")
                        st.write(f"- Médiane: {transitions['time_diff'].median():.1f}s")
                        st.write(f"- Min: {transitions['time_diff'].min():.1f}s")
                        st.write(f"- Max: {transitions['time_diff'].max():.1f}s")
                
                # Utiliser la nouvelle fonction de détection
                if len(porte_data_clean) > 0:
                    # Mode événements individuels - traiter chaque "Ouverte" comme un cycle
                    if detection_mode == "Événements individuels":
                        # Filtrer seulement les événements d'ouverture
                        if pd.api.types.is_string_dtype(porte_data_clean['Porte_Status']):
                            open_events_df = porte_data_clean[
                                porte_data_clean['Porte_Status'].str.lower().isin(['ouverte', 'ouvert'])
                            ].copy()
                        else:
                            # Données numériques (1 = ouvert, 0 = fermé)
                            open_events_df = porte_data_clean[
                                porte_data_clean['Porte_Status'] == 1
                            ].copy()
                        
                        cycles_list = []
                        for i, row in open_events_df.iterrows():
                            # Assumer une durée fixe ou jusqu'au prochain événement
                            open_time = row['Timestamp']
                            # Chercher le prochain événement pour déterminer la durée
                            next_events = porte_data_clean[porte_data_clean['Timestamp'] > open_time].head(5)
                            
                            if len(next_events) > 0:
                                # Utiliser le prochain timestamp comme fermeture approximative
                                close_time = next_events.iloc[0]['Timestamp']
                                duration = (close_time - open_time).total_seconds()
                                
                                # Si la durée est trop longue, limiter à 1 heure
                                if duration > 3600:
                                    close_time = open_time + pd.Timedelta(hours=1)
                                    duration = 3600
                            else:
                                # Pas d'événement suivant, assumer 30 minutes
                                close_time = open_time + pd.Timedelta(minutes=30)
                                duration = 1800
                            
                            if duration >= min_duration:
                                cycles_list.append({
                                    'open_ts': open_time,
                                    'close_ts': close_time,
                                    'duration_sec': duration
                                })
                        
                        cycles_df = pd.DataFrame(cycles_list)
                        if len(cycles_df) > 0:
                            cycles_df = cycles_df.sort_values('open_ts').reset_index(drop=True)
                        else:
                            cycles_df = pd.DataFrame(columns=['open_ts', 'close_ts', 'duration_sec'])
                            
                        st.info(f"Mode événements individuels: {len(open_events_df)} événements 'Ouverte' détectés → {len(cycles_df)} cycles créés")
                    else:
                        # Mode normal ou automatique
                        cycles_df = detect_door_cycles(
                            porte_data_clean,
                            ts_col='Timestamp', 
                            status_col='Porte_Status',
                            min_duration_sec=min_duration,
                            max_duration_hours=max_duration
                        )
                    
                    st.write(f"\n### Résultat de la détection: {len(cycles_df)} cycles")
                    if len(cycles_df) > 0:
                        st.write("Cycles détectés:")
                        cycles_display = cycles_df.copy()
                        cycles_display['duration_min'] = cycles_display['duration_sec'] / 60
                        st.dataframe(cycles_display)
                else:
                    st.warning("Aucune donnée de porte valide trouvée")
                    cycles_df = pd.DataFrame()
            
            # Debug: Afficher les cycles détectés
            with st.expander("🔍 Debug - Cycles détectés"):
                st.write(f"Nombre de cycles trouvés: {len(cycles_df)}")
                
                # Afficher les données brutes pour debug
                if hasattr(cycles_df, 'attrs') and 'debug_df' in cycles_df.attrs:
                    st.write("\n### Échantillon des données brutes:")
                    debug_df = cycles_df.attrs['debug_df']
                    # Ajouter une colonne pour mieux voir les états
                    debug_df_display = debug_df.copy()
                    debug_df_display['État'] = debug_df_display['state'].map({0: '🔴 Fermé', 1: '🟢 Ouvert'})
                    st.dataframe(debug_df_display[['Timestamp', 'Porte_Status', 'État']].head(50))
                
                if len(cycles_df) > 0:
                    st.write("\n### Cycles détectés:")
                    display_df = cycles_df.copy()
                    display_df['duration_min'] = display_df['duration_sec'] / 60
                    display_df['open_time'] = display_df['open_ts'].dt.strftime('%Y-%m-%d %H:%M:%S')
                    display_df['close_time'] = display_df['close_ts'].dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Afficher tous les cycles si moins de 50, sinon les 50 premiers
                    n_display = len(display_df) if len(display_df) < 50 else 50
                    st.dataframe(display_df[['open_time', 'close_time', 'duration_min']].head(n_display))
                    
                    # Statistiques
                    st.write("\n### Statistiques des cycles:")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Durée moyenne", f"{display_df['duration_min'].mean():.1f} min")
                    with col2:
                        st.metric("Durée médiane", f"{display_df['duration_min'].median():.1f} min")
                    with col3:
                        st.metric("Total cycles", len(display_df))
                    
                    # Distribution des durées
                    st.write("\n### Distribution des durées:")
                    st.write(f"- < 1 min: {len(display_df[display_df['duration_min'] < 1])} cycles")
                    st.write(f"- 1-10 min: {len(display_df[(display_df['duration_min'] >= 1) & (display_df['duration_min'] < 10)])} cycles")
                    st.write(f"- 10-60 min: {len(display_df[(display_df['duration_min'] >= 10) & (display_df['duration_min'] < 60)])} cycles")
                    st.write(f"- > 60 min: {len(display_df[display_df['duration_min'] >= 60])} cycles")
            
            # Visualisation de l'état de la porte dans le temps
            if len(porte_data_clean) > 0:
                st.subheader("📊 État de la porte dans le temps")
                
                # Créer une figure pour l'état de la porte
                fig_status = go.Figure()
                
                # Préparer les données pour la visualisation
                plot_data = porte_data_clean.copy()
                plot_data = plot_data.sort_values('Timestamp')
                
                # Convertir le statut en numérique si nécessaire
                if pd.api.types.is_string_dtype(plot_data['Porte_Status']):
                    status_map = {'ouverte': 1, 'ouvert': 1, 'fermé': 0, 'ferme': 0, 'fermée': 0}
                    plot_data['Status_Numeric'] = plot_data['Porte_Status'].str.lower().map(status_map).fillna(0)
                else:
                    plot_data['Status_Numeric'] = pd.to_numeric(plot_data['Porte_Status'], errors='coerce').fillna(0)
                
                # Ajouter la ligne d'état
                fig_status.add_trace(go.Scatter(
                    x=plot_data['Timestamp'],
                    y=plot_data['Status_Numeric'],
                    mode='lines',
                    line=dict(shape='hv', color='blue', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(0, 100, 255, 0.3)',
                    name='État porte',
                    hovertemplate='%{x}<br>État: %{y}<extra></extra>'
                ))
                
                # Ajouter des zones colorées pour les cycles détectés
                for i, row in cycles_df.iterrows():
                    fig_status.add_vrect(
                        x0=row['open_ts'], x1=row['close_ts'],
                        fillcolor="red", opacity=0.2,
                        layer="below", line_width=0,
                        annotation_text=f"C{i+1}",
                        annotation_position="top left"
                    )
                
                fig_status.update_layout(
                    title="État de la porte et cycles détectés",
                    xaxis_title="Temps",
                    yaxis_title="État (0=Fermé, 1=Ouvert)",
                    height=400,
                    yaxis=dict(
                        tickmode='array',
                        tickvals=[0, 1],
                        ticktext=['Fermé', 'Ouvert'],
                        range=[-0.1, 1.1]
                    ),
                    showlegend=False
                )
                
                st.plotly_chart(fig_status, use_container_width=True)
            
            # Visualisation Timeline des cycles de porte
            if len(cycles_df) > 0:
                st.subheader("📅 Timeline des cycles de porte")
                
                # Créer une figure pour la timeline
                fig_timeline = go.Figure()
                
                # Ajouter chaque cycle comme une barre horizontale
                for i, row in cycles_df.iterrows():
                    fig_timeline.add_trace(go.Scatter(
                        x=[row['open_ts'], row['close_ts']],
                        y=[i, i],
                        mode='lines',
                        line=dict(color='red', width=10),
                        name=f"Cycle {i+1}",
                        hovertemplate=(
                            f"Cycle {i+1}<br>" +
                            "Ouverture: %{x|%Y-%m-%d %H:%M:%S}<br>" +
                            f"Durée: {row['duration_sec']/60:.1f} min<extra></extra>"
                        ),
                        showlegend=False
                    ))
                    
                    # Ajouter des marqueurs pour début et fin
                    fig_timeline.add_trace(go.Scatter(
                        x=[row['open_ts'], row['close_ts']],
                        y=[i, i],
                        mode='markers',
                        marker=dict(size=12, color=['green', 'red']),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                
                # Mise en forme de la timeline
                fig_timeline.update_layout(
                    title="Chronologie des ouvertures de porte",
                    xaxis_title="Temps",
                    yaxis_title="Cycles",
                    height=max(300, min(600, 50 + len(cycles_df) * 30)),
                    yaxis=dict(
                        tickmode='linear',
                        tick0=0,
                        dtick=1,
                        ticktext=[f"Cycle {i+1}" for i in range(len(cycles_df))],
                        tickvals=list(range(len(cycles_df)))
                    ),
                    showlegend=False,
                    hovermode='closest'
                )
                
                # Ajouter une annotation pour la légende
                fig_timeline.add_annotation(
                    text="🟢 Ouverture | 🔴 Fermeture",
                    xref="paper", yref="paper",
                    x=0.5, y=1.05,
                    showarrow=False,
                    font=dict(size=12)
                )
                
                st.plotly_chart(fig_timeline, use_container_width=True)
                
                # Statistiques rapides
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total cycles", len(cycles_df))
                with col2:
                    st.metric("Durée moyenne", f"{cycles_df['duration_sec'].mean()/60:.1f} min")
                with col3:
                    st.metric("Durée totale", f"{cycles_df['duration_sec'].sum()/60:.1f} min")
                with col4:
                    if len(filtered_merged_data) > 0:
                        time_range = (filtered_merged_data['Timestamp'].max() - filtered_merged_data['Timestamp'].min()).total_seconds() / 3600
                        if time_range > 0:
                            freq = len(cycles_df) / time_range
                            st.metric("Fréquence", f"{freq:.2f} cycles/h")
            
            # Convertir en format attendu par le reste du code
            open_events = cycles_df['open_ts'].tolist()
            close_events = cycles_df['close_ts'].tolist()
            
            st.write(f"**Cycles valides détectés:** {len(cycles_df)} cycles")
            
            # Analyse des cycles ouverture-fermeture
            st.subheader("📈 Analyse de l'évolution de température pendant l'ouverture de porte")
            
            # Utiliser les événements d'ouverture détectés pour créer des cycles
            door_cycles = []
            all_door_cycles = []  # Nouveau: garder tous les cycles même sans température
            
            if len(cycles_df) > 0:
                st.write(f"**Traitement de {len(cycles_df)} cycles détectés...**")
                
                # NOUVELLE APPROCHE: Prétraiter les données de température
                # 1. Créer une copie pour le traitement
                temp_processed = filtered_merged_data[['Timestamp', 'Temp_Ambiante']].copy()
                temp_processed = temp_processed.sort_values('Timestamp')
                
                # 2. Statistiques avant traitement
                nan_before = temp_processed['Temp_Ambiante'].isna().sum()
                total_rows = len(temp_processed)
                st.write(f"**Données température - Avant traitement:** {total_rows - nan_before}/{total_rows} valeurs valides ({nan_before} NaN)")
                
                # 3. Remplir les NaN intelligemment
                # D'abord, interpolation linéaire pour les petits gaps
                temp_processed['Temp_Ambiante_Interpolated'] = temp_processed['Temp_Ambiante'].interpolate(
                    method='linear', 
                    limit=10  # Max 10 points consécutifs
                )
                
                # Ensuite, forward fill puis backward fill pour les gaps restants
                temp_processed['Temp_Ambiante_Filled'] = temp_processed['Temp_Ambiante_Interpolated'].ffill().bfill()
                
                # Si encore des NaN (début/fin), utiliser la moyenne globale
                global_mean = temp_processed['Temp_Ambiante'].mean()
                if pd.notna(global_mean):
                    temp_processed['Temp_Ambiante_Final'] = temp_processed['Temp_Ambiante_Filled'].fillna(global_mean)
                else:
                    temp_processed['Temp_Ambiante_Final'] = temp_processed['Temp_Ambiante_Filled']
                
                # 4. Statistiques après traitement
                nan_after = temp_processed['Temp_Ambiante_Final'].isna().sum()
                st.write(f"**Données température - Après traitement:** {total_rows - nan_after}/{total_rows} valeurs valides")
                
                # 5. Remplacer dans filtered_merged_data
                filtered_merged_data['Temp_Ambiante_Original'] = filtered_merged_data['Temp_Ambiante'].copy()
                filtered_merged_data = filtered_merged_data.merge(
                    temp_processed[['Timestamp', 'Temp_Ambiante_Final']], 
                    on='Timestamp', 
                    how='left'
                )
                filtered_merged_data['Temp_Ambiante'] = filtered_merged_data['Temp_Ambiante_Final']
                
                # Debug: Variables pour suivre le traitement
                cycles_with_no_temp_data = 0
                cycles_with_invalid_temps = 0
                
                # Pour chaque cycle, analyser l'impact sur la température
                for i, cycle in cycles_df.iterrows():
                    open_time = cycle['open_ts']
                    close_time = cycle['close_ts']
                    cycle_duration = cycle['duration_sec'] / 60  # Convertir en minutes
                    
                    # Limiter les cycles très longs (plus de 2 heures)
                    if cycle_duration > 120:
                        close_time = open_time + timedelta(minutes=120)
                        cycle_duration = 120
                    
                    # Enregistrer tous les cycles (avec ou sans température)
                    all_door_cycles.append({
                        'Open_Time': open_time,
                        'Close_Time': close_time,
                        'Duration_min': cycle_duration,
                        'Is_Complete_Cycle': True,  # Tous les cycles détectés sont complets
                        'Has_Temp_Data': False  # Sera mis à jour plus tard
                    })
                    
                    # NOUVELLE LOGIQUE: Plus flexible pour trouver les températures
                    
                    # 1. Température AVANT l'ouverture (baseline)
                    # Chercher dans les 30 minutes avant, mais prendre les 5 dernières minutes de préférence
                    before_window_start = open_time - timedelta(minutes=30)
                    before_window_end = open_time
                    
                    before_data = filtered_merged_data[
                        (filtered_merged_data['Timestamp'] >= before_window_start) & 
                        (filtered_merged_data['Timestamp'] < before_window_end)
                    ].copy()
                    
                    # Prendre la moyenne des 5 dernières minutes si possible
                    before_5min = before_data[before_data['Timestamp'] >= (open_time - timedelta(minutes=5))]
                    if len(before_5min) > 0:
                        temp_before = before_5min['Temp_Ambiante'].mean()
                    elif len(before_data) > 0:
                        # Sinon, prendre la dernière valeur disponible
                        temp_before = before_data.iloc[-1]['Temp_Ambiante']
                    else:
                        temp_before = np.nan
                    
                    # 2. Température PENDANT/APRÈS le cycle
                    # Chercher pendant tout le cycle + 10 minutes après
                    after_window_start = open_time
                    after_window_end = close_time + timedelta(minutes=10)
                    
                    after_data = filtered_merged_data[
                        (filtered_merged_data['Timestamp'] >= after_window_start) & 
                        (filtered_merged_data['Timestamp'] <= after_window_end)
                    ].copy()
                    
                    # Prendre le maximum pendant le cycle (pire cas)
                    if len(after_data) > 0:
                        temp_after = after_data['Temp_Ambiante'].max()
                    else:
                        temp_after = np.nan
                    
                    # 3. Données complètes pour visualisation
                    full_window_start = before_window_start
                    full_window_end = after_window_end
                    
                    full_cycle_data = filtered_merged_data[
                        (filtered_merged_data['Timestamp'] >= full_window_start) & 
                        (filtered_merged_data['Timestamp'] <= full_window_end)
                    ].copy()
                    
                    # Debug: Afficher les infos de matching température pour les premiers cycles
                    if i < 3:  # Debug pour les 3 premiers cycles
                        with st.expander(f"🔍 Debug température cycle {i+1}"):
                            st.write(f"Ouverture: {open_time}, Fermeture: {close_time}")
                            st.write(f"Fenêtre avant: {before_window_start} à {before_window_end}")
                            st.write(f"Points de données avant: {len(before_data)}")
                            st.write(f"Temp avant: {temp_before:.2f}°C" if pd.notna(temp_before) else "Temp avant: NaN")
                            st.write(f"Fenêtre après: {after_window_start} à {after_window_end}")
                            st.write(f"Points de données après: {len(after_data)}")
                            st.write(f"Temp après (max): {temp_after:.2f}°C" if pd.notna(temp_after) else "Temp après: NaN")
                        
                    # Vérifier que les températures sont valides
                    if pd.notna(temp_before) and pd.notna(temp_after):
                        # Marquer ce cycle comme ayant des données de température
                        all_door_cycles[-1]['Has_Temp_Data'] = True
                        
                        door_cycles.append({
                            'Open_Time': open_time,
                            'Close_Time': close_time,
                            'Duration_min': cycle_duration,
                            'Temp_Before': temp_before,
                            'Temp_After': temp_after,
                            'Delta_Temp': temp_after - temp_before,
                            'Cycle_Data': full_cycle_data,
                            'Before_Data': before_data,
                            'After_Data': after_data,
                            'Is_Complete_Cycle': True
                        })
                    else:
                        if pd.isna(temp_before) or pd.isna(temp_after):
                            cycles_with_invalid_temps += 1
                        else:
                            cycles_with_no_temp_data += 1
                            
                st.write(f"**Total de cycles détectés:** {len(all_door_cycles)}")
                st.write(f"**Cycles avec données de température:** {len(door_cycles)}")
                
                # Debug: Afficher pourquoi des cycles ont été filtrés
                with st.expander("🔍 Debug - Résumé du traitement des cycles"):
                    st.write("**Nouvelle approche de traitement:**")
                    st.write("1. ✅ Interpolation des NaN dans les données de température")
                    st.write("2. ✅ Fenêtres de temps flexibles (30 min avant, cycle + 10 min après)")
                    st.write("3. ✅ Température avant = moyenne des 5 dernières minutes")
                    st.write("4. ✅ Température après = maximum pendant le cycle")
                    st.write("")
                    st.write(f"Total cycles détectés (après filtrage): {len(cycles_df)}")
                    st.write(f"Total cycles créés: {len(all_door_cycles)}")
                    st.write(f"Cycles sans données de température: {cycles_with_no_temp_data}")
                    st.write(f"Cycles avec températures invalides: {cycles_with_invalid_temps}")
                    st.write(f"**Cycles avec données de température complètes: {len(door_cycles)}**")
                    
                # Afficher tous les cycles dans un tableau
                with st.expander("📊 Voir tous les cycles détectés"):
                    if all_door_cycles:
                        df_all_cycles = pd.DataFrame(all_door_cycles)
                        df_all_cycles['Open_Time'] = pd.to_datetime(df_all_cycles['Open_Time'])
                        df_all_cycles['Close_Time'] = pd.to_datetime(df_all_cycles['Close_Time'])
                        
                        # Ajouter des colonnes formatées pour l'affichage
                        df_all_cycles['Ouverture'] = df_all_cycles['Open_Time'].dt.strftime('%d/%m/%Y %H:%M')
                        df_all_cycles['Fermeture'] = df_all_cycles['Close_Time'].dt.strftime('%d/%m/%Y %H:%M')
                        df_all_cycles['Durée (min)'] = df_all_cycles['Duration_min'].round(1)
                        df_all_cycles['Cycle complet'] = df_all_cycles['Is_Complete_Cycle'].map({True: '✓', False: '✗'})
                        df_all_cycles['Données temp.'] = df_all_cycles['Has_Temp_Data'].map({True: '✓', False: '✗'})
                        
                        # Afficher le tableau
                        st.dataframe(
                            df_all_cycles[['Ouverture', 'Fermeture', 'Durée (min)', 'Cycle complet', 'Données temp.']],
                            use_container_width=True
                        )
                        
                        # Statistiques supplémentaires
                        st.write(f"**Statistiques des cycles:**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Durée moyenne", f"{df_all_cycles['Duration_min'].mean():.1f} min")
                        with col2:
                            cycles_with_temp = df_all_cycles['Has_Temp_Data'].sum()
                            pct_with_temp = (cycles_with_temp / len(df_all_cycles)) * 100
                            st.metric("% avec données temp.", f"{pct_with_temp:.1f}%")
                        with col3:
                            complete_cycles = df_all_cycles['Is_Complete_Cycle'].sum()
                            st.metric("Cycles complets", f"{complete_cycles}/{len(df_all_cycles)}")
            
            if len(door_cycles) > 0:
                # Convertir en DataFrame pour les statistiques
                door_impacts = []
                for cycle in door_cycles:
                    # Vérifier que les valeurs ne sont pas NaN
                    if (pd.notna(cycle['Temp_Before']) and 
                        pd.notna(cycle['Temp_After']) and 
                        pd.notna(cycle['Duration_min'])):
                        
                        door_impacts.append({
                            'Timestamp': cycle['Open_Time'],
                            'Duree_Analyse': cycle['Duration_min'],
                            'Temp_Avant': cycle['Temp_Before'],
                            'Temp_Apres': cycle['Temp_After'],
                            'Delta_Temp': cycle['Delta_Temp']
                        })
                
                st.write(f"**Cycles valides après nettoyage:** {len(door_impacts)}")
                
                if door_impacts and len(door_impacts) > 0:
                    df_impacts = pd.DataFrame(door_impacts)
                    
                    # Debug temporaire: Afficher les données pour vérifier
                    with st.expander("🔍 Débogage - Voir les données"):
                        st.write(f"Shape df_impacts: {df_impacts.shape}")
                        st.write("Colonnes:", df_impacts.columns.tolist())
                        st.write("Premières lignes:")
                        st.dataframe(df_impacts.head())
                        st.write("Valeurs NaN par colonne:")
                        st.write(df_impacts.isnull().sum())
                    
                    # Graphiques d'analyse
                    
                    # 1. Sélection individuelle de cycle avec dropdown
                    st.subheader("📈 Évolution temporelle de la température par cycle")
                    
                    # Créer le dropdown pour sélectionner un cycle spécifique
                    cycle_idx = st.selectbox(
                        "Sélectionner un cycle à visualiser",
                        range(len(door_cycles)),
                        format_func=lambda x: f"Cycle {x+1} - {door_cycles[x]['Open_Time'].strftime('%Y-%m-%d %H:%M')} (ΔT: {door_cycles[x]['Delta_Temp']:.2f}°C, Durée: {door_cycles[x]['Duration_min']:.1f} min)"
                    )
                    
                    if cycle_idx is not None:
                        selected_cycle = door_cycles[cycle_idx]
                        
                        # Visualisation détaillée du cycle sélectionné
                        cycle_data = selected_cycle['Cycle_Data']
                        if len(cycle_data) > 0:
                            fig_selected = go.Figure()
                            
                            # Température
                            fig_selected.add_trace(go.Scatter(
                                x=cycle_data['Timestamp'],
                                y=cycle_data['Temp_Ambiante'],
                                mode='lines+markers',
                                name='Température',
                                line=dict(color='red', width=2),
                                marker=dict(size=6)
                            ))
                            
                            # Marquer l'ouverture de porte
                            fig_selected.add_shape(
                                type="line",
                                x0=selected_cycle['Open_Time'], x1=selected_cycle['Open_Time'],
                                y0=0, y1=1,
                                yref="paper",
                                line=dict(color="green", width=2, dash="dash")
                            )
                            fig_selected.add_annotation(
                                x=selected_cycle['Open_Time'],
                                y=1.05,
                                yref="paper",
                                text="Ouverture",
                                showarrow=False
                            )
                            
                            # Marquer la fermeture de porte
                            fig_selected.add_shape(
                                type="line",
                                x0=selected_cycle['Close_Time'], x1=selected_cycle['Close_Time'],
                                y0=0, y1=1,
                                yref="paper",
                                line=dict(color="orange", width=2, dash="dash")
                            )
                            fig_selected.add_annotation(
                                x=selected_cycle['Close_Time'],
                                y=1.05,
                                yref="paper",
                                text="Fermeture",
                                showarrow=False
                            )
                            
                            # Ajouter les lignes horizontales pour les températures avant/après
                            fig_selected.add_hline(
                                y=selected_cycle['Temp_Before'],
                                line_dash="dot",
                                line_color="blue",
                                annotation_text=f"Temp avant: {selected_cycle['Temp_Before']:.1f}°C"
                            )
                            
                            fig_selected.add_hline(
                                y=selected_cycle['Temp_After'],
                                line_dash="dot",
                                line_color="purple",
                                annotation_text=f"Temp après: {selected_cycle['Temp_After']:.1f}°C"
                            )
                            
                            fig_selected.update_layout(
                                title=f"Cycle {cycle_idx+1} - {selected_cycle['Open_Time'].strftime('%Y-%m-%d %H:%M')} (Durée: {selected_cycle['Duration_min']:.1f} min, ΔT: {selected_cycle['Delta_Temp']:.2f}°C)",
                                xaxis_title="Temps",
                                yaxis_title="Température (°C)",
                                height=450,
                                hovermode='x unified'
                            )
                            
                            st.plotly_chart(fig_selected, use_container_width=True)
                            
                            # Afficher les détails du cycle sélectionné
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Température avant", f"{selected_cycle['Temp_Before']:.1f}°C")
                            with col2:
                                st.metric("Température après", f"{selected_cycle['Temp_After']:.1f}°C")
                            with col3:
                                st.metric("Variation", f"{selected_cycle['Delta_Temp']:.2f}°C",
                                        delta=f"{'↑' if selected_cycle['Delta_Temp'] > 0 else '↓'} {abs(selected_cycle['Delta_Temp']):.2f}°C")
                            with col4:
                                st.metric("Durée", f"{selected_cycle['Duration_min']:.1f} min")
                    
                    # 2. Graphique comparatif: Vue d'ensemble de tous les cycles
                    st.subheader("📊 Comparaison de tous les cycles")
                    
                    fig = go.Figure()
                    
                    # Ajouter chaque cycle comme une série
                    colors = px.colors.qualitative.Set3
                    for i, cycle in enumerate(door_cycles[:10]):  # Limiter à 10 cycles pour la lisibilité
                        cycle_data = cycle['Cycle_Data']
                        if len(cycle_data) > 0:
                            # Calculer le temps relatif depuis l'ouverture (en minutes)
                            relative_time = [(t - cycle['Open_Time']).total_seconds() / 60 
                                           for t in cycle_data['Timestamp']]
                            
                            fig.add_trace(go.Scatter(
                                x=relative_time,
                                y=cycle_data['Temp_Ambiante'],
                                mode='lines+markers',
                                name=f"Cycle {i+1} ({cycle['Open_Time'].strftime('%m-%d %H:%M')})",
                                line=dict(color=colors[i % len(colors)], width=2),
                                marker=dict(size=6),
                                hovertemplate='Temps: %{x:.1f} min<br>Temp: %{y:.1f}°C<extra></extra>'
                            ))
                            
                            # Ajouter une ligne verticale pour marquer l'ouverture de porte
                            fig.add_vline(
                                x=0, 
                                line_dash="dash", 
                                line_color="red",
                                opacity=0.7,
                                annotation_text=f"Ouverture {i+1}",
                                annotation_position="top"
                            )
                    
                    fig.update_layout(
                        title="Évolution de température pendant les cycles d'ouverture",
                        xaxis_title="Temps depuis ouverture (minutes)",
                        yaxis_title="Température ambiante (°C)",
                        height=500,
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 2. Graphique de corrélation durée vs changement température
                    st.subheader("📊 Analyse de corrélation")
                    
                    # Utiliser une seule colonne au lieu de deux
                    with st.container():
                        # Corrélation durée vs changement température
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=df_impacts['Duree_Analyse'],
                            y=df_impacts['Delta_Temp'],
                            mode='markers',
                            marker=dict(size=10, color='darkblue', opacity=0.7),
                            name='Cycles',
                            text=[f"Cycle {i+1}<br>Durée: {d:.1f} min<br>ΔT: {t:.2f}°C" 
                                  for i, (d, t) in enumerate(zip(df_impacts['Duree_Analyse'], df_impacts['Delta_Temp']))],
                            hovertemplate='%{text}<extra></extra>'
                        ))
                        
                        # Ligne de tendance si assez de points
                        # Commented out because duration is constant
                        # if len(df_impacts) > 3:
                        #     z = np.polyfit(df_impacts['Duree_Analyse'], df_impacts['Delta_Temp'], 1)
                        #     p = np.poly1d(z)
                        #     x_trend = np.linspace(df_impacts['Duree_Analyse'].min(), 
                        #                         df_impacts['Duree_Analyse'].max(), 100)
                        #     fig.add_trace(go.Scatter(
                        #         x=x_trend,
                        #         y=p(x_trend),
                        #         mode='lines',
                        #         line=dict(color='red', dash='dash'),
                        #         name='Tendance'
                        #     ))
                        
                        fig.add_hline(y=0, line_dash="dash", line_color="gray")
                        
                        fig.update_layout(
                            title="Durée vs Changement température",
                            xaxis_title="Durée d'ouverture (min)",
                            yaxis_title="ΔT (°C)",
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Statistiques des cycles
                    st.subheader("📊 Statistiques des cycles d'ouverture")
                    
                    # Utiliser les données valides seulement
                    valid_data = df_impacts.dropna(subset=['Delta_Temp', 'Duree_Analyse'])
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Nombre de cycles", len(valid_data))
                    with col2:
                        if len(valid_data) > 0:
                            st.metric("ΔT moyen", f"{valid_data['Delta_Temp'].mean():.2f}°C")
                        else:
                            st.metric("ΔT moyen", "N/A")
                    with col3:
                        if len(valid_data) > 0:
                            avg_duration = valid_data['Duree_Analyse'].mean()
                            st.metric("Durée moyenne cycle", f"{avg_duration:.0f} min")
                        else:
                            st.metric("Durée moyenne cycle", "N/A")
                    with col4:
                        if len(valid_data) > 0:
                            st.metric("ΔT max", f"{valid_data['Delta_Temp'].max():.2f}°C")
                        else:
                            st.metric("ΔT max", "N/A")
                    
                    # Tableau détaillé
                    with st.expander("📋 Détail des cycles d'ouverture-fermeture"):
                        st.dataframe(
                            df_impacts.style.format({
                                'Duree_Analyse': '{:.0f} min',
                                'Temp_Avant': '{:.1f}°C',
                                'Temp_Apres': '{:.1f}°C',
                                'Delta_Temp': '{:.2f}°C'
                            }),
                            use_container_width=True
                        )
                    
                    # Interprétation
                    if len(valid_data) > 0:
                        avg_impact = valid_data['Delta_Temp'].mean()
                        avg_duration = valid_data['Duree_Analyse'].mean()  # Durée moyenne des cycles
                        
                        if avg_impact > 0.1:
                            interpretation = f"🔥 Pendant l'ouverture de porte (durée moyenne: {avg_duration:.1f} min), la température tend à **augmenter** de {avg_impact:.2f}°C en moyenne."
                        elif avg_impact < -0.1:
                            interpretation = f"❄️ Pendant l'ouverture de porte (durée moyenne: {avg_duration:.1f} min), la température tend à **diminuer** de {abs(avg_impact):.2f}°C en moyenne."
                        else:
                            interpretation = f"🌡️ Pendant l'ouverture de porte (durée moyenne: {avg_duration:.1f} min), la température reste **relativement stable**."
                    else:
                        interpretation = "⚠️ Pas assez de données valides pour faire une interprétation."
                    
                    st.info(interpretation)
                    
                else:
                    st.warning("Impossible de calculer l'impact sur la température - données insuffisantes.")
            else:
                st.warning("Aucun cycle d'ouverture valide trouvé. Vérifiez que les données de température sont disponibles pendant les périodes d'ouverture.")
                
                # Si on a détecté des cycles mais aucun avec température
                if len(all_door_cycles) > 0:
                    st.info(f"ℹ️ Cependant, {len(all_door_cycles)} cycles de porte ont été détectés. Consultez l'onglet 'Voir tous les cycles détectés' ci-dessus pour plus de détails.")
        else:
            st.warning("Aucun événement d'ouverture de porte détecté dans les données.")
    else:
        st.warning("Données de porte ou de température manquantes pour l'analyse.")

# 6. ANALYSE PORTE
with tab6:
    st.info(f"📅 Période sélectionnée: {start_date.strftime('%Y-%m-%d %H:%M')} - {end_date.strftime('%Y-%m-%d %H:%M')}")
    if render_incident_lens_interface:
        # Pass filtered data to Incident Lens
        render_incident_lens_interface(data=filtered_merged_data, start_date=start_date, end_date=end_date)
    else:
        st.error("🚫 Incident Lens non disponible - problème d'import des modules")
        st.info("📋 Vérifiez que tous les modules sont correctement installés")

# 7. CORRÉLATIONS
with tab7:
    st.header("🔗 Analyse des Relations entre Variables")
    st.info(f"📅 Période sélectionnée: {start_date.strftime('%Y-%m-%d %H:%M')} - {end_date.strftime('%Y-%m-%d %H:%M')}")
    
    # Sélection des variables pour la corrélation
    numeric_vars = ['Temp_Ambiante', 'Temp_Exterieure', 'Puissance_IT', 'Porte_Status']
    
    # Ajouter les colonnes CLIM individuelles si elles existent
    clim_status_columns = [col for col in filtered_merged_data.columns if 'CLIM' in col and 'Status' in col]
    numeric_vars.extend(clim_status_columns)
    
    available_vars = [var for var in numeric_vars if var in filtered_merged_data.columns]
    
    if len(available_vars) >= 2:
        # Create a copy for correlation calculation to avoid modifying original data
        corr_data = filtered_merged_data[available_vars].copy()
        
        
        # Convert Porte_Status to numeric if needed
        if 'Porte_Status' in corr_data.columns:
            if corr_data['Porte_Status'].dtype == 'object':
                corr_data['Porte_Status'] = corr_data['Porte_Status'].map({
                    'Open': 1, 'Ouvert': 1, 'open': 1, '1': 1, 1: 1,
                    'Close': 0, 'Fermé': 0, 'closed': 0, '0': 0, 0: 0
                })
            corr_data['Porte_Status'] = pd.to_numeric(corr_data['Porte_Status'], errors='coerce')
        
        # Convert CLIM columns to numeric
        for col in clim_status_columns:
            if col in corr_data.columns:
                if corr_data[col].dtype == 'object':
                    corr_data[col] = corr_data[col].map({
                        'ON': 1, 'on': 1, 'On': 1, '1': 1, 1: 1,
                        'OFF': 0, 'off': 0, 'Off': 0, '0': 0, 0: 0
                    })
                corr_data[col] = pd.to_numeric(corr_data[col], errors='coerce')
        
        # Only keep rows where at least 50% of values are non-NaN
        min_non_nan = len(available_vars) * 0.5
        corr_data = corr_data.dropna(thresh=min_non_nan)
        
        # Calculate correlation matrix with both methods
        if len(corr_data) > 10:  # Need minimum data points
            # Calculate both Pearson and Spearman
            pearson_corr = corr_data.corr(method='pearson')
            spearman_corr = corr_data.corr(method='spearman')
            
            # Use Spearman by default as it's more robust
            corr_matrix = spearman_corr
        else:
            st.warning("⚠️ Données insuffisantes pour calculer les relations. Au moins 10 points de données sont nécessaires.")
            corr_matrix = pd.DataFrame()
        
        if not corr_matrix.empty and 'Temp_Ambiante' in corr_matrix.columns:
            
            # Extract correlations with Temp_Ambiante
            temp_correlations = corr_matrix['Temp_Ambiante'].drop('Temp_Ambiante', errors='ignore')
            
            # Function to interpret correlation strength
            def interpret_correlation(value):
                abs_val = abs(value)
                if abs_val >= 0.8:
                    return "très forte", "🔴"
                elif abs_val >= 0.6:
                    return "forte", "🟠"
                elif abs_val >= 0.4:
                    return "modérée", "🟡"
                elif abs_val >= 0.2:
                    return "faible", "🟢"
                else:
                    return "négligeable", "⚪"
            
            # Function to get relationship description
            def get_relationship_description(var, corr_value):
                strength, emoji = interpret_correlation(corr_value)
                
                if pd.isna(corr_value):
                    return f"{emoji} **{var}**: Données insuffisantes pour établir une relation"
                
                if abs(corr_value) < 0.2:
                    return f"{emoji} **{var}**: Aucune relation significative détectée"
                
                direction = "augmente" if corr_value > 0 else "diminue"
                opposite = "augmente" if corr_value > 0 else "diminue"
                
                # Custom descriptions for each variable
                descriptions = {
                    'Temp_Exterieure': {
                        'positive': f"Quand la température extérieure augmente, la température ambiante tend à augmenter également (relation {strength})",
                        'negative': f"Quand la température extérieure augmente, la température ambiante tend à diminuer (relation {strength} - situation inhabituelle)"
                    },
                    'Puissance_IT': {
                        'positive': f"Quand la charge IT augmente, la température ambiante augmente (relation {strength})",
                        'negative': f"Quand la charge IT augmente, la température ambiante diminue (relation {strength} - situation inhabituelle)"
                    },
                    'Porte_Status': {
                        'positive': f"Les ouvertures de porte ont tendance à faire augmenter la température ambiante (relation {strength})",
                        'negative': f"Les ouvertures de porte ont tendance à faire baisser la température ambiante (relation {strength})"
                    }
                }
                
                # For CLIM units
                if 'CLIM' in var and 'Status' in var:
                    if corr_value < 0:
                        return f"L'activation de {var.replace('_Status', '')} aide à réduire la température (relation {strength})"
                    else:
                        return f"L'activation de {var.replace('_Status', '')} est associée à une hausse de température (relation {strength} - vérifier l'efficacité)"
                
                # Get appropriate description
                if var in descriptions:
                    desc_key = 'positive' if corr_value > 0 else 'negative'
                    base_desc = descriptions[var][desc_key]
                else:
                    base_desc = f"Relation {strength} {'positive' if corr_value > 0 else 'négative'} avec {var}"
                
                return f"{emoji} **{var}**: {base_desc}"
            
            # Main analysis section
            st.markdown("## 📊 Comprendre les Relations avec la Température Ambiante")
            st.markdown("""
            Cette analyse identifie les facteurs qui influencent la température ambiante dans votre centre de données.
            Les relations sont classées par ordre d'importance pour faciliter la prise de décision.
            """)
            
            # Sort correlations by absolute value
            sorted_correlations = temp_correlations.abs().sort_values(ascending=False)
            
            # Key drivers section
            st.markdown("### 🎯 Facteurs Principaux Affectant la Température")
            
            # Identify top drivers
            top_drivers = []
            for var in sorted_correlations.index:
                corr_val = temp_correlations[var]
                if abs(corr_val) >= 0.3:  # Only significant correlations
                    top_drivers.append((var, corr_val))
            
            if top_drivers:
                st.markdown("**Facteurs ayant un impact significatif (classés par importance):**")
                
                for i, (var, corr_val) in enumerate(top_drivers, 1):
                    strength, emoji = interpret_correlation(corr_val)
                    
                    # Create readable variable names
                    var_display = {
                        'Temp_Exterieure': 'Température Extérieure',
                        'Puissance_IT': 'Charge IT',
                        'Porte_Status': 'État de la Porte',
                        'CLIM_A_Status': 'Climatisation A',
                        'CLIM_B_Status': 'Climatisation B',
                        'CLIM_C_Status': 'Climatisation C',
                        'CLIM_D_Status': 'Climatisation D'
                    }.get(var, var)
                    
                    impact_desc = get_relationship_description(var, corr_val)
                    st.markdown(f"{i}. {impact_desc}")
            else:
                st.info("Aucun facteur n'a d'impact significatif sur la température pendant cette période.")
        
            # Detailed insights section
            st.markdown("### 💡 Insights Détaillés et Recommandations")
            
            # Create three columns for different categories
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 🌡️ Facteurs Environnementaux")
                if 'Temp_Exterieure' in temp_correlations:
                    ext_corr = temp_correlations['Temp_Exterieure']
                    if abs(ext_corr) > 0.5:
                        st.error(f"Impact élevé de la température extérieure (corrélation: {ext_corr:.2f})")
                        st.markdown("**Recommandations:**")
                        st.markdown("- Améliorer l'isolation thermique")
                        st.markdown("- Vérifier l'étanchéité du bâtiment")
                        st.markdown("- Installer des pare-soleil si nécessaire")
                    elif abs(ext_corr) > 0.3:
                        st.warning(f"Impact modéré de la température extérieure (corrélation: {ext_corr:.2f})")
                        st.markdown("**Recommandations:**")
                        st.markdown("- Surveiller lors des pics de chaleur")
                        st.markdown("- Planifier la maintenance préventive")
                    else:
                        st.success(f"Bonne isolation thermique (corrélation: {ext_corr:.2f})")
                        st.markdown("- L'isolation fonctionne bien")
                        st.markdown("- Maintenir les bonnes pratiques")
            
            with col2:
                st.markdown("#### ❄️ Système de Refroidissement")
                clim_effectiveness = []
                for col in clim_status_columns:
                    if col in temp_correlations:
                        clim_effectiveness.append((col, temp_correlations[col]))
                
                if clim_effectiveness:
                    effective_units = [unit for unit, corr in clim_effectiveness if corr < -0.2]
                    ineffective_units = [unit for unit, corr in clim_effectiveness if corr >= 0]
                    
                    if effective_units:
                        st.success(f"{len(effective_units)} unité(s) CLIM fonctionnent correctement")
                        for unit in effective_units:
                            unit_name = unit.replace('_Status', '')
                            st.markdown(f"- ✅ {unit_name} réduit efficacement la température")
                    
                    if ineffective_units:
                        st.error(f"{len(ineffective_units)} unité(s) CLIM nécessitent attention")
                        for unit in ineffective_units:
                            unit_name = unit.replace('_Status', '')
                            st.markdown(f"- ⚠️ {unit_name} pourrait nécessiter maintenance")
                        st.markdown("**Action requise:** Vérifier l'efficacité de ces unités")
                else:
                    st.info("Données CLIM non disponibles")
            
            with col3:
                st.markdown("#### 💻 Charge IT et Accès")
                if 'Puissance_IT' in temp_correlations:
                    it_corr = temp_correlations['Puissance_IT']
                    if abs(it_corr) > 0.5:
                        st.warning(f"Forte influence de la charge IT (corrélation: {it_corr:.2f})")
                        st.markdown("**Recommandations:**")
                        st.markdown("- Optimiser la distribution de charge")
                        st.markdown("- Considérer l'ajout de capacité de refroidissement")
                    else:
                        st.success(f"Impact IT gérable (corrélation: {it_corr:.2f})")
                
                if 'Porte_Status' in temp_correlations:
                    door_corr = temp_correlations['Porte_Status']
                    if abs(door_corr) > 0.3:
                        st.warning(f"Impact des ouvertures de porte (corrélation: {door_corr:.2f})")
                        st.markdown("**Recommandations:**")
                        st.markdown("- Former le personnel aux bonnes pratiques")
                        st.markdown("- Installer des alertes pour portes ouvertes")
                    else:
                        st.success("Impact minimal des portes")
            
            # Summary and action plan
            st.markdown("### 📋 Plan d'Action Prioritaire")
            
            # Generate priority actions based on correlations
            priority_actions = []
            
            # Check external temperature
            if 'Temp_Exterieure' in temp_correlations and abs(temp_correlations['Temp_Exterieure']) > 0.5:
                priority_actions.append(("Haute", "🔴", "Améliorer l'isolation thermique du bâtiment", 
                                        "La température extérieure a un impact trop important"))
            
            # Check CLIM effectiveness
            ineffective_clims = sum(1 for col in clim_status_columns 
                                   if col in temp_correlations and temp_correlations[col] >= 0)
            if ineffective_clims > 0:
                priority_actions.append(("Haute", "🔴", f"Maintenance urgente de {ineffective_clims} unité(s) CLIM",
                                        "Certaines unités ne refroidissent pas efficacement"))
            
            # Check IT load
            if 'Puissance_IT' in temp_correlations and temp_correlations['Puissance_IT'] > 0.6:
                priority_actions.append(("Moyenne", "🟡", "Optimiser la répartition de la charge IT",
                                        "La charge IT contribue significativement à la chaleur"))
            
            # Check door impact
            if 'Porte_Status' in temp_correlations and abs(temp_correlations['Porte_Status']) > 0.4:
                priority_actions.append(("Moyenne", "🟡", "Réviser les procédures d'accès",
                                        "Les ouvertures de porte affectent la température"))
            
            if priority_actions:
                st.markdown("**Actions recommandées par ordre de priorité:**")
                
                # Sort by priority
                priority_order = {"Haute": 1, "Moyenne": 2, "Basse": 3}
                priority_actions.sort(key=lambda x: priority_order[x[0]])
                
                for priority, emoji, action, reason in priority_actions:
                    st.markdown(f"{emoji} **Priorité {priority}:** {action}")
                    st.markdown(f"   *Raison: {reason}*")
            else:
                st.success("✅ Aucune action urgente requise. Le système fonctionne dans des paramètres acceptables.")
            
            # Technical details expander for those who want more info
            with st.expander("📊 Détails Techniques (pour les experts)", expanded=False):
                st.markdown("#### Valeurs de Corrélation")
                
                # Create a clean dataframe for display
                tech_df = pd.DataFrame({
                    'Variable': temp_correlations.index,
                    'Corrélation': temp_correlations.values,
                    'Interprétation': [interpret_correlation(x)[0] for x in temp_correlations.values],
                    'Impact': ['Positif' if x > 0 else 'Négatif' if x < 0 else 'Neutre' for x in temp_correlations.values]
                })
                tech_df = tech_df.sort_values('Corrélation', key=abs, ascending=False)
                
                st.dataframe(
                    tech_df.style.format({'Corrélation': '{:.3f}'})
                    .background_gradient(subset=['Corrélation'], cmap='RdBu_r', vmin=-1, vmax=1),
                    use_container_width=True
                )
                
                st.markdown("""
                **Guide d'interprétation:**
                - **Corrélation positive:** Les deux variables évoluent dans le même sens
                - **Corrélation négative:** Les variables évoluent en sens opposé
                - **Valeur absolue:** Indique la force de la relation (0 = aucune, 1 = parfaite)
                - **Méthode utilisée:** Corrélation de Spearman (robuste aux valeurs extrêmes)
                """)
        
        else:
            if corr_matrix.empty:
                st.warning("⚠️ Impossible de calculer les relations entre variables. Vérifiez la disponibilité des données.")
            else:
                st.warning("⚠️ La variable 'Temp_Ambiante' n'est pas disponible dans les données.")
    
    else:
        st.warning("⚠️ Pas assez de variables disponibles pour l'analyse des relations")

# 8. RAPPORTS
with tab8:
    st.header("📋 Génération de rapports")
    st.info(f"📅 Période sélectionnée: {start_date.strftime('%Y-%m-%d %H:%M')} - {end_date.strftime('%Y-%m-%d %H:%M')}")
    
    report_type = st.selectbox(
        "Type de rapport",
        ["Rapport quotidien", "Rapport hebdomadaire", "Rapport d'anomalies", "Rapport d'efficacité énergétique"]
    )
    
    if report_type == "Rapport d'efficacité énergétique":
        st.subheader("⚡ Rapport d'efficacité énergétique")
        
        # Explication du PUE
        with st.expander("💡 Comprendre le PUE (Power Usage Effectiveness)", expanded=True):
            st.write("""
            **Le PUE en termes simples :** Imaginez que votre data center est comme une voiture. Le PUE mesure combien d'énergie totale vous consommez pour faire fonctionner vos serveurs informatiques.
            
            🔢 **Comment ça marche ?**
            - PUE = Énergie totale du data center ÷ Énergie des équipements IT
            - Un PUE de 2.0 signifie que pour chaque kWh utilisé par vos serveurs, vous dépensez 1 kWh supplémentaire en climatisation, éclairage, etc.
            
            🎯 **Pourquoi viser 1.5 ?**
            - **PUE = 1.0** : Perfection théorique (impossible en pratique - il faut toujours de la climatisation!)
            - **PUE = 1.5** : Excellence industrielle - seulement 50% d'énergie en plus pour le refroidissement
            - **PUE = 2.0** : Acceptable mais perfectible - vous doublez votre consommation
            - **PUE > 2.5** : Inefficace - il est temps d'optimiser!
            
            💰 **Impact concret :** Si votre PUE passe de 2.0 à 1.5, vous économisez 25% sur votre facture d'électricité totale!
            """)
        
        if all(col in filtered_merged_data.columns for col in ['Puissance_IT', 'Puissance_CLIM', 'Puissance_Generale']):
            # Calculs d'efficacité
            pue = filtered_merged_data['Puissance_Generale'] / filtered_merged_data['Puissance_IT']
            cooling_efficiency = filtered_merged_data['Puissance_CLIM'] / filtered_merged_data['Puissance_IT']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("PUE Moyen", f"{pue.mean():.2f}")
            with col2:
                st.metric("Efficacité CLIM", f"{cooling_efficiency.mean():.2f}")
            with col3:
                energy_waste = (filtered_merged_data['Puissance_Generale'] - filtered_merged_data['Puissance_IT']).sum()
                st.metric("Énergie non-IT totale", f"{energy_waste:.0f} kWh")
            
            # Graphique d'évolution du PUE
            daily_pue = filtered_merged_data.copy()
            daily_pue['Date'] = daily_pue['Timestamp'].dt.date
            daily_pue['PUE'] = daily_pue['Puissance_Generale'] / daily_pue['Puissance_IT']
            daily_avg_pue = daily_pue.groupby('Date')['PUE'].mean().reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_avg_pue['Date'],
                y=daily_avg_pue['PUE'],
                mode='lines+markers',
                name='PUE journalier',
                line=dict(color='green', width=2)
            ))
            
            # Ligne de référence pour PUE idéal
            fig.add_hline(y=1.5, line_dash="dash", line_color="red",
                         annotation_text="PUE cible: 1.5")
            
            fig.update_layout(
                title="Évolution du PUE (Power Usage Effectiveness)",
                xaxis_title="Date",
                yaxis_title="PUE",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Recommandations
            st.subheader("💡 Recommandations d'optimisation")
            
            avg_pue = pue.mean()
            if avg_pue > 2.0:
                st.error(f"""
                ⚠️ **PUE élevé détecté : {avg_pue:.2f}**
                
                Votre data center consomme plus du double de l'énergie nécessaire! 
                Pour chaque euro dépensé en serveurs, vous dépensez {avg_pue-1:.2f}€ en infrastructure.
                
                **Actions recommandées :**
                - Vérifier l'efficacité du système de refroidissement
                - Optimiser la circulation d'air (hot aisle/cold aisle)
                - Identifier et éliminer les points chauds
                """)
            elif avg_pue > 1.5:
                st.warning(f"""
                ⚡ **PUE modéré : {avg_pue:.2f}**
                
                Votre efficacité est correcte mais des économies sont possibles!
                Potentiel d'économie : environ {((avg_pue-1.5)/avg_pue)*100:.0f}% sur votre facture totale.
                
                **Suggestions d'amélioration :**
                - Augmenter légèrement la température de consigne
                - Utiliser le free cooling quand possible
                - Optimiser la charge des serveurs
                """)
            else:
                st.success(f"""
                ✅ **PUE excellent : {avg_pue:.2f}**
                
                Félicitations! Votre data center est dans le top 10% mondial en efficacité.
                Vous ne dépensez que {(avg_pue-1)*100:.0f}% d'énergie supplémentaire pour le refroidissement.
                
                **Continuez ainsi en :**
                - Maintenant cette performance
                - Partageant vos bonnes pratiques
                - Surveillant régulièrement les indicateurs
                """)
            
            # Analyse des périodes de surconsommation
            high_consumption = filtered_merged_data[pue > pue.quantile(0.9)].copy()
            if not high_consumption.empty:
                high_consumption['Hour'] = high_consumption['Timestamp'].dt.hour
                peak_hours = high_consumption['Hour'].value_counts().head(3)
                
                st.write("**Heures de pic de consommation:**")
                for hour, count in peak_hours.items():
                    st.write(f"• {hour}h00 - {hour+1}h00")

# 9. SIMULATION DE COÛTS
with tab9:
    st.header("💰 Simulation et Analyse des Coûts Énergétiques")
    st.info(f"📅 Période sélectionnée: {start_date.strftime('%Y-%m-%d %H:%M')} - {end_date.strftime('%Y-%m-%d %H:%M')}")
    
    # Explication
    st.info("""
    💡 **Cette section vous permet de:**
    - Calculer vos coûts énergétiques actuels
    - Simuler des économies potentielles
    - Comparer différents scénarios d'optimisation
    - Analyser l'impact financier du PUE
    """)
    
    if all(col in filtered_merged_data.columns for col in ['Puissance_IT', 'Puissance_CLIM', 'Puissance_Generale']):
        # Input pour le tarif électrique
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            electricity_rate = st.number_input(
                "💵 Tarif électrique ($/kWh)",
                min_value=0.01,
                max_value=1.0,
                value=0.12,
                step=0.01,
                help="Entrez votre tarif électrique actuel"
            )
        
        with col2:
            currency = st.selectbox(
                "Devise",
                ["USD ($)", "EUR (€)", "MAD (DH)"],
                index=0
            )
            currency_symbol = currency.split()[1].strip("()")
        
        # Calculs de base
        st.subheader("📊 Analyse des Coûts Actuels")
        
        # Calcul des consommations
        time_range = (filtered_merged_data['Timestamp'].max() - filtered_merged_data['Timestamp'].min()).total_seconds() / 3600
        
        # Consommations moyennes
        avg_it_power = filtered_merged_data['Puissance_IT'].mean()
        avg_clim_power = filtered_merged_data['Puissance_CLIM'].mean()
        avg_total_power = filtered_merged_data['Puissance_Generale'].mean()
        avg_pue = avg_total_power / avg_it_power if avg_it_power > 0 else 0
        
        # Coûts horaires, journaliers, mensuels et annuels
        hourly_cost = avg_total_power * electricity_rate
        daily_cost = hourly_cost * 24
        monthly_cost = daily_cost * 30
        annual_cost = daily_cost * 365
        
        # Affichage des métriques de coût
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "💸 Coût Horaire",
                f"{currency_symbol}{hourly_cost:.2f}",
                help="Coût moyen par heure de fonctionnement"
            )
        with col2:
            st.metric(
                "📅 Coût Journalier",
                f"{currency_symbol}{daily_cost:.2f}",
                delta=f"{currency_symbol}{daily_cost - (avg_it_power * 24 * electricity_rate):.2f} non-IT"
            )
        with col3:
            st.metric(
                "📆 Coût Mensuel",
                f"{currency_symbol}{monthly_cost:,.2f}",
                help="Estimation sur 30 jours"
            )
        with col4:
            st.metric(
                "🗓️ Coût Annuel",
                f"{currency_symbol}{annual_cost:,.2f}",
                help="Projection sur 365 jours"
            )
        
        # Répartition des coûts
        st.subheader("📊 Répartition des Coûts par Composant")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Camembert de répartition
            it_cost = avg_it_power * electricity_rate
            clim_cost = avg_clim_power * electricity_rate
            other_cost = (avg_total_power - avg_it_power - avg_clim_power) * electricity_rate
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=['IT', 'Climatisation', 'Autres (éclairage, etc.)'],
                values=[it_cost, clim_cost, other_cost],
                hole=.3,
                marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c']
            )])
            
            fig_pie.update_layout(
                title=f"Répartition des coûts horaires ({currency_symbol}/h)",
                height=400
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Tableau de détail
            cost_breakdown = pd.DataFrame({
                'Composant': ['Équipements IT', 'Climatisation', 'Infrastructure', 'Total'],
                'Puissance (kW)': [avg_it_power, avg_clim_power, 
                                 avg_total_power - avg_it_power - avg_clim_power, avg_total_power],
                f'Coût/heure ({currency_symbol})': [it_cost, clim_cost, other_cost, hourly_cost],
                f'Coût/mois ({currency_symbol})': [it_cost * 720, clim_cost * 720, other_cost * 720, monthly_cost],
                '% du Total': [it_cost/hourly_cost * 100, clim_cost/hourly_cost * 100, 
                             other_cost/hourly_cost * 100, 100]
            })
            
            st.dataframe(
                cost_breakdown.style.format({
                    'Puissance (kW)': '{:.2f}',
                    f'Coût/heure ({currency_symbol})': '{:.2f}',
                    f'Coût/mois ({currency_symbol})': '{:,.2f}',
                    '% du Total': '{:.1f}%'
                }),
                use_container_width=True
            )
        
        # Simulation d'optimisation
        st.subheader("🚀 Simulation d'Optimisation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Ensure max_value is at least greater than min_value
            max_pue = max(avg_pue, 2.5)
            default_pue = 1.5 if avg_pue > 1.5 else max(1.2, avg_pue * 0.9)
            
            target_pue = st.slider(
                "PUE cible pour simulation",
                min_value=1.1,
                max_value=max_pue,
                value=default_pue,
                step=0.01,
                format="%.2f",
                help="Simulez l'impact d'une amélioration du PUE"
            )
        
        with col2:
            temp_increase = st.slider(
                "Augmentation température (°C)",
                min_value=0,
                max_value=5,
                value=2,
                step=1,
                help="Impact d'une augmentation de la température de consigne"
            )
        
        # Calcul des économies potentielles
        new_total_power = avg_it_power * target_pue
        power_savings = avg_total_power - new_total_power
        
        # Estimation de l'impact de la température (règle empirique : 4% d'économie par °C)
        temp_savings_percent = temp_increase * 0.04
        clim_savings = avg_clim_power * temp_savings_percent
        total_savings = power_savings + clim_savings
        
        # Affichage des économies
        st.subheader("💰 Économies Potentielles")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            hourly_savings = total_savings * electricity_rate
            st.metric(
                "Économies/heure",
                f"{currency_symbol}{hourly_savings:.2f}",
                delta=f"-{(total_savings/avg_total_power)*100:.1f}%"
            )
        
        with col2:
            monthly_savings = hourly_savings * 720
            st.metric(
                "Économies/mois",
                f"{currency_symbol}{monthly_savings:,.2f}",
                help="Sur base de 720 heures"
            )
        
        with col3:
            annual_savings = hourly_savings * 8760
            st.metric(
                "Économies/an",
                f"{currency_symbol}{annual_savings:,.2f}",
                help="Sur base de 8760 heures"
            )
        
        # Graphique de comparaison
        fig_comparison = go.Figure()
        
        categories = ['Actuel', f'PUE {target_pue}', f'+{temp_increase}°C', 'Optimisé']
        it_costs = [avg_it_power * electricity_rate] * 4
        clim_costs = [avg_clim_power * electricity_rate,
                     avg_clim_power * electricity_rate,
                     avg_clim_power * (1 - temp_savings_percent) * electricity_rate,
                     (new_total_power - avg_it_power - clim_savings) * electricity_rate]
        other_costs = [(avg_total_power - avg_it_power - avg_clim_power) * electricity_rate,
                      (new_total_power - avg_it_power - avg_clim_power) * electricity_rate,
                      (avg_total_power - avg_it_power - avg_clim_power) * electricity_rate,
                      0]
        
        fig_comparison.add_trace(go.Bar(name='IT', x=categories, y=it_costs, marker_color='#1f77b4'))
        fig_comparison.add_trace(go.Bar(name='Climatisation', x=categories, y=clim_costs, marker_color='#ff7f0e'))
        fig_comparison.add_trace(go.Bar(name='Autres', x=categories, y=other_costs, marker_color='#2ca02c'))
        
        fig_comparison.update_layout(
            title=f"Comparaison des scénarios de coûts ({currency_symbol}/heure)",
            barmode='stack',
            yaxis_title=f"Coût ({currency_symbol}/h)",
            height=400
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # ROI et temps de retour
        st.subheader("📈 Retour sur Investissement")
        
        investment = st.number_input(
            f"💼 Investissement estimé pour optimisation ({currency_symbol})",
            min_value=0,
            value=50000,
            step=1000,
            help="Coût estimé des améliorations (isolation, free cooling, etc.)"
        )
        
        if annual_savings > 0 and investment > 0:
            roi_years = investment / annual_savings
            roi_months = roi_years * 12
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "⏱️ Temps de retour",
                    f"{roi_years:.1f} ans",
                    help="Durée pour récupérer l'investissement"
                )
            
            with col2:
                roi_percent = (annual_savings / investment) * 100
                st.metric(
                    "📊 ROI annuel",
                    f"{roi_percent:.1f}%",
                    help="Retour sur investissement par an"
                )
            
            with col3:
                five_year_profit = (annual_savings * 5) - investment
                st.metric(
                    "💵 Profit sur 5 ans",
                    f"{currency_symbol}{five_year_profit:,.0f}",
                    help="Économies nettes après investissement"
                )
        
        # Recommandations personnalisées
        st.subheader("🎯 Recommandations Personnalisées")
        
        if avg_pue > 2.0:
            st.error("""
            **Actions prioritaires pour réduire les coûts:**
            1. 🔧 Audit énergétique complet du système de refroidissement
            2. 🌡️ Augmentation progressive de la température de consigne
            3. 💨 Mise en place du free cooling si possible
            4. 🔌 Consolidation des serveurs sous-utilisés
            """)
        elif avg_pue > 1.5:
            st.warning("""
            **Opportunités d'économies identifiées:**
            1. 📊 Optimisation de la distribution d'air (containment)
            2. 🌡️ Ajustement fin des paramètres de climatisation
            3. 💡 Passage à l'éclairage LED si pas déjà fait
            4. 🔄 Mise à jour des équipements les moins efficaces
            """)
        else:
            st.success("""
            **Maintenir l'excellence énergétique:**
            1. ✅ Surveillance continue des métriques
            2. 🔄 Maintenance préventive régulière
            3. 📈 Benchmarking avec les meilleures pratiques
            4. 🌱 Explorer les énergies renouvelables
            """)
        
    else:
        st.warning("Données de puissance manquantes pour l'analyse des coûts.")

# Footer
st.markdown("---")
st.caption("🏢 BGU-ONE Data Center Monitoring Dashboard | © 2025")