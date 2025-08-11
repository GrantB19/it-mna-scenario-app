
import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="IT M&A Scenario App", layout="wide")

st.title("🧩 IT M&A Scenario Simulator")

# --- Sidebar Configuration ---
st.sidebar.header("⚙️ Paramétrage")

# Infrastructure Elements
st.sidebar.subheader("Éléments d'infrastructure")
infra_elements = st.sidebar.multiselect(
    "Sélectionner les éléments d'infrastructure",
    ["PC", "Serveur", "LAN", "WAN", "Firewall", "WiFi", "Switch", "Backup", "Antivirus"]
)

# Mosaic Platforms
st.sidebar.subheader("Socles Mosaic")
mosaic_options = {
    "Entry": ["PC", "LAN", "Firewall"],
    "Advanced": ["PC", "Serveur", "LAN", "WAN", "Firewall"],
    "Complete": ["PC", "Serveur", "LAN", "WAN", "Firewall", "WiFi", "Switch", "Backup", "Antivirus"]
}
selected_mosaic = st.sidebar.selectbox("Choisir un socle Mosaic", list(mosaic_options.keys()))
mosaic_elements = mosaic_options[selected_mosaic]

# Applications
st.sidebar.subheader("Applications")
app_list = st.sidebar.text_area("Lister les applications (une par ligne)", "ERP\nCRM\nWMS\nBI")

# Coûts associés
st.sidebar.subheader("Coûts associés")
all_elements = list(set(infra_elements + mosaic_elements + app_list.splitlines()))
costs_data = {
    "Élément": all_elements,
    "CAPEX (€)": [1000] * len(all_elements),
    "OPEX (€ / an)": [500] * len(all_elements)
}
costs_df = pd.DataFrame(costs_data)

# --- Main Interface ---
st.header("📊 Visualiser les éléments configurés")

edited_df = st.data_editor(costs_df, num_rows="dynamic", use_container_width=True)
st.divider()

# --- Simulation ---
st.header("📈 Simulation des coûts par phase M&A")

phases = ["Préparation au Closing", "Transition (TSA)", "Post-TSA"]
phase_durations = {
    "Préparation au Closing": 3,
    "Transition (TSA)": 6,
    "Post-TSA": 12
}

simulation = []
for _, row in edited_df.iterrows():
    for phase in phases:
        simulation.append({
            "Élément": row["Élément"],
            "Phase": phase,
            "Durée (mois)": phase_durations[phase],
            "CAPEX (€)": row["CAPEX (€)"] if phase == "Préparation au Closing" else 0,
            "OPEX (€)": row["OPEX (€ / an)"] * (phase_durations[phase] / 12)
        })

sim_df = pd.DataFrame(simulation)
st.dataframe(sim_df, use_container_width=True)
