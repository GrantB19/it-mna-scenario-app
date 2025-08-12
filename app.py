import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="IT M&A Scenario App", layout="wide")

st.title("🧩 IT M&A Scenario Simulator")

# --- Sidebar Configuration ---
st.sidebar.header("⚙️ Paramétrage")

# Section: Modifier les éléments d'infrastructure disponibles
st.sidebar.subheader("🔧 Gestion des éléments d'infrastructure disponibles")
default_infra_elements = ["PC", "Serveur", "LAN", "WAN", "Firewall", "WiFi", "Switch", "Backup", "Antivirus"]
infra_elements_input = st.sidebar.text_area(
    "Liste des éléments d'infrastructure (une par ligne)",
    "\n".join(default_infra_elements)
)
infra_elements_available = [e.strip() for e in infra_elements_input.splitlines() if e.strip()]

# Section: Définir les socles Mosaic
st.sidebar.subheader("🏗️ Définir les socles Mosaic")
mosaic_entry_input = st.sidebar.text_area("Socle Entry", "PC\nLAN\nFirewall")
mosaic_advanced_input = st.sidebar.text_area("Socle Advanced", "PC\nServeur\nLAN\nWAN\nFirewall")
mosaic_complete_input = st.sidebar.text_area("Socle Complete", "PC\nServeur\nLAN\nWAN\nFirewall\nWiFi\nSwitch\nBackup\nAntivirus")

mosaic_options = {
    "Entry": [e.strip() for e in mosaic_entry_input.splitlines() if e.strip()],
    "Advanced": [e.strip() for e in mosaic_advanced_input.splitlines() if e.strip()],
    "Complete": [e.strip() for e in mosaic_complete_input.splitlines() if e.strip()]
}
selected_mosaic = st.sidebar.selectbox("Choisir un socle Mosaic", list(mosaic_options.keys()))
mosaic_elements = mosaic_options[selected_mosaic]

# Section: Définir les applications
st.sidebar.subheader("📱 Applications")
app_list_input = st.sidebar.text_area("Lister les applications (une par ligne)", "ERP\nCRM\nWMS\nBI")
app_list = [app.strip() for app in app_list_input.splitlines() if app.strip()]

# Section: Sélectionner les éléments d'infrastructure à utiliser
st.sidebar.subheader("🧩 Sélectionner les éléments d'infrastructure à utiliser")
infra_elements_selected = st.sidebar.multiselect(
    "Éléments sélectionnés",
    options=infra_elements_available,
    default=infra_elements_available
)

# --- Main Interface ---
st.header("📊 Visualiser et modifier les coûts des éléments")

# Créer le tableau des coûts
all_elements = list(set(infra_elements_selected + mosaic_elements + app_list))
costs_data = {
    "Élément": all_elements,
    "Type": ["Infrastructure" if e in infra_elements_available else "Application" for e in all_elements],
    "CAPEX (€)": [1000] * len(all_elements),
    "OPEX (€ / an)": [500] * len(all_elements)
}
costs_df = pd.DataFrame(costs_data)

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
            "Type": row["Type"],
            "Phase": phase,
            "Durée (mois)": phase_durations[phase],
            "CAPEX (€)": row["CAPEX (€)"] if phase == "Préparation au Closing" else 0,
            "OPEX (€)": row["OPEX (€ / an)"] * (phase_durations[phase] / 12)
        })

sim_df = pd.DataFrame(simulation)
st.dataframe(sim_df, use_container_width=True)
