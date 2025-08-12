import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="IT M&A Scenario App", layout="wide")

# --- Session State Initialization ---
if "infra_catalog" not in st.session_state:
    st.session_state.infra_catalog = pd.DataFrame(columns=["Élément", "CAPEX (€)", "OPEX (€ / an)"])
if "app_catalog" not in st.session_state:
    st.session_state.app_catalog = pd.DataFrame(columns=["Application", "CAPEX (€)", "OPEX (€ / an)"])
if "entities" not in st.session_state:
    st.session_state.entities = {}

# --- Sidebar Navigation ---
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Aller à", ["Définir les environnements IT types", "Composer l'environnement d'une entité", "Restitution des coûts"])

# --- Page 1: Définir les environnements IT types ---
if page == "Définir les environnements IT types":
    st.title("🔧 Définir les environnements IT types")

    st.subheader("Éléments d'infrastructure disponibles")
    infra_editor = st.data_editor(st.session_state.infra_catalog, num_rows="dynamic", use_container_width=True)
    st.session_state.infra_catalog = infra_editor

    st.subheader("Applications disponibles")
    app_editor = st.data_editor(st.session_state.app_catalog, num_rows="dynamic", use_container_width=True)
    st.session_state.app_catalog = app_editor

# --- Page 2: Composer l'environnement d'une entité ---
elif page == "Composer l'environnement d'une entité":
    st.title("🏢 Composer l'environnement IT d'une entité juridique")

    entity_name = st.text_input("Nom de l'entité juridique")
    if entity_name:
        st.subheader("Sélectionner les éléments d'infrastructure")
        selected_infra = st.multiselect("Éléments d'infrastructure", st.session_state.infra_catalog["Élément"].tolist())

        st.subheader("Sélectionner les applications")
        selected_apps = st.multiselect("Applications", st.session_state.app_catalog["Application"].tolist())

        if st.button("Enregistrer l'environnement IT de l'entité"):
            st.session_state.entities[entity_name] = {
                "infrastructure": selected_infra,
                "applications": selected_apps
            }
            st.success(f"Environnement IT enregistré pour l'entité {entity_name}")

    st.divider()
    st.subheader("📋 Entités enregistrées")
    for name, config in st.session_state.entities.items():
        st.markdown(f"**{name}**")
        st.write("Infrastructure:", config["infrastructure"])
        st.write("Applications:", config["applications"])

# --- Page 3: Restitution des coûts ---
elif page == "Restitution des coûts":
    st.title("📊 Restitution des coûts par entité et par phase M&A")

    phases = ["Préparation au Closing", "Transition (TSA)", "Post-TSA"]
    phase_durations = {
        "Préparation au Closing": 3,
        "Transition (TSA)": 6,
        "Post-TSA": 12
    }

    simulation = []
    for entity, config in st.session_state.entities.items():
        for element in config["infrastructure"]:
            cost_row = st.session_state.infra_catalog[st.session_state.infra_catalog["Élément"] == element].iloc[0]
            for phase in phases:
                simulation.append({
                    "Entité": entity,
                    "Élément": element,
                    "Type": "Infrastructure",
                    "Phase": phase,
                    "Durée (mois)": phase_durations[phase],
                    "CAPEX (€)": cost_row["CAPEX (€)"] if phase == "Préparation au Closing" else 0,
                    "OPEX (€)": cost_row["OPEX (€ / an)"] * (phase_durations[phase] / 12)
                })
        for app in config["applications"]:
            cost_row = st.session_state.app_catalog[st.session_state.app_catalog["Application"] == app].iloc[0]
            for phase in phases:
                simulation.append({
                    "Entité": entity,
                    "Élément": app,
                    "Type": "Application",
                    "Phase": phase,
                    "Durée (mois)": phase_durations[phase],
                    "CAPEX (€)": cost_row["CAPEX (€)"] if phase == "Préparation au Closing" else 0,
                    "OPEX (€)": cost_row["OPEX (€ / an)"] * (phase_durations[phase] / 12)
                })

    sim_df = pd.DataFrame(simulation)
    st.dataframe(sim_df, use_container_width=True)
