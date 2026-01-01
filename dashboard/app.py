import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Panipuri World Twin", layout="wide")

st.title("🌍 Panipuri: Global Economic World Twin")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Simulation Control", "Graph Explorer", "Analytics"])

if page == "Simulation Control":
    st.header("🚀 Simulation Control Center")
    
    with st.form("sim_form"):
        scenario_id = st.text_input("Scenario ID", value="SCENARIO_001")
        steps = st.number_input("Simulation Steps", min_value=1, max_value=100, value=10)
        countries = st.multiselect("Target Countries (Empty for All)", ["USA", "CHN", "DEU", "IND"])
        
        submitted = st.form_submit_button("Run Simulation")
        
        if submitted:
            payload = {
                "scenario_id": scenario_id,
                "steps": steps,
                "countries": countries
            }
            try:
                response = requests.post(f"{API_URL}/simulation/run", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"Simulation started! Run ID: {data['run_id']}")
                    st.info(f"Status: {data['status']}")
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to API. Is it running?")

elif page == "Graph Explorer":
    st.header("🕸️ Knowledge Graph Explorer")
    
    iso_code = st.text_input("Enter Country ISO3 Code", value="USA")
    
    if st.button("Fetch Details"):
        try:
            response = requests.get(f"{API_URL}/graph/country/{iso_code}")
            if response.status_code == 200:
                node = response.json()
                st.subheader(f"Country: {node['properties'].get('name', iso_code)}")
                st.json(node)
                
                # Placeholder for network viz
                st.info("Network visualization would appear here (using Cytoscape/Plotly).")
            else:
                st.warning("Country not found or API error.")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to API.")

elif page == "Analytics":
    st.header("📊 Results Analytics")
    st.write("Placeholder for Parquet/MinIO result visualization.")
    
    # Dummy data for visual
    df = pd.DataFrame({
        "Step": range(10),
        "GDP": [100 * (1.02**i) for i in range(10)]
    })
    
    fig = px.line(df, x="Step", y="GDP", title="Projected GDP Growth (Dummy Data)")
    st.plotly_chart(fig)
