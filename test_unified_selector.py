"""
Quick test script for the unified period selector
Run with: streamlit run test_unified_selector.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.ui.period_selector import period_selector

st.set_page_config(page_title="Test Unified Selector", layout="wide")

st.title("🧪 Test Unified Period Selector")

# Render the mini selector in sidebar
start_date, end_date = period_selector.render_mini_selector()

# Main content
st.header("Main Content Area")

# Display the selected period
st.success(f"✅ Selected Period: {start_date.strftime('%Y-%m-%d %H:%M')} to {end_date.strftime('%Y-%m-%d %H:%M')}")

# Create test data
test_data = pd.DataFrame({
    'Timestamp': pd.date_range(start=datetime.now() - timedelta(days=30), 
                               end=datetime.now(), 
                               freq='H'),
    'Value': range(721)  # 30 days * 24 hours + 1
})

# Filter the test data
filtered_data = period_selector.filter_dataframe(test_data)

# Display results
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Records", len(test_data))

with col2:
    st.metric("Filtered Records", len(filtered_data))

with col3:
    percentage = (len(filtered_data) / len(test_data)) * 100 if len(test_data) > 0 else 0
    st.metric("Percentage", f"{percentage:.1f}%")

# Show filtered data
st.subheader("Filtered Data Sample")
if not filtered_data.empty:
    st.dataframe(filtered_data.head(10))
else:
    st.warning("No data for selected period")

# Test the full selector
st.header("Full Period Selector UI")
full_start, full_end = period_selector.render_selector(key_suffix="full")

st.info(f"Full selector returned: {full_start} to {full_end}")

# Get current period info
current_period = period_selector.get_current_period()
st.json(current_period)