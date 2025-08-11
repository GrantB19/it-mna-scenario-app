
import streamlit as st
import pandas as pd

st.set_page_config(page_title="IT M&A Simulator", layout="wide")

# Initialisation des données
if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=["nom", "OPEX", "CAPEX", "adhérences_infra", "adhérences_appli"])

if "infrastructure_elements" not in st.session_state:
    st.session_state.infrastructure_elements = pd.DataFrame(columns=["nom", "type", "coût"])

if "socles_mosaic" not in st.session_state:
    st.session_state.socles_mosaic = pd.DataFrame(columns=["nom", "éléments_infra", "coût_total"])

st.title("💼 IT M&A Simulator - Groupe Avril")

tab1, tab2 = st.tabs(["⚙️ Paramétrage", "📊 Simulation"])

with tab1:
    st.header("Paramétrage des éléments IT")

    st.subheader("Applications")
    st.session_state.applications = st.data_editor(
        st.session_state.applications,
        num_rows="dynamic",
        use_container_width=True
    )

    st.subheader("Éléments d'infrastructure")
    st.session_state.infrastructure_elements = st.data_editor(
        st.session_state.infrastructure_elements,
        num_rows="dynamic",
        use_container_width=True
    )

    st.subheader("Socles Mosaic")
    st.session_state.socles_mosaic = st.data_editor(
        st.session_state.socles_mosaic,
        num_rows="dynamic",
        use_container_width=True
    )

with tab2:
    st.header("Simulation des coûts et timings")

    phase = st.selectbox("Phase du projet", ["Préparation au Closing", "Transition (TSA)", "Post-TSA"])

    selected_apps = st.multiselect(
        "Applications à intégrer",
        options=st.session_state.applications["nom"].tolist()
    )

    selected_infra = st.multiselect(
        "Éléments d'infrastructure à intégrer",
        options=st.session_state.infrastructure_elements["nom"].tolist()
    )

    selected_socles = st.multiselect(
        "Socles Mosaic à intégrer",
        options=st.session_state.socles_mosaic["nom"].tolist()
    )

    total_opex = 0
    total_capex = 0

    for app in selected_apps:
        app_data = st.session_state.applications[st.session_state.applications["nom"] == app]
        if not app_data.empty:
            total_opex += float(app_data["OPEX"].values[0])
            total_capex += float(app_data["CAPEX"].values[0])

    for infra in selected_infra:
        infra_data = st.session_state.infrastructure_elements[st.session_state.infrastructure_elements["nom"] == infra]
        if not infra_data.empty:
            total_opex += float(infra_data["coût"].values[0])

    for socle in selected_socles:
        socle_data = st.session_state.socles_mosaic[st.session_state.socles_mosaic["nom"] == socle]
        if not socle_data.empty:
            total_capex += float(socle_data["coût_total"].values[0])

    st.subheader("Résultat de la simulation")
    st.metric("Coût OPEX estimé", f"{total_opex:,.2f} €")
    st.metric("Coût CAPEX estimé", f"{total_capex:,.2f} €")

    st.write("📌 Adhérences détectées :")
    for app in selected_apps:
        app_data = st.session_state.applications[st.session_state.applications["nom"] == app]
        if not app_data.empty:
            adh_infra = app_data["adhérences_infra"].values[0]
            adh_appli = app_data["adhérences_appli"].values[0]
            st.write(f"- **{app}** : Infra → {adh_infra}, Appli → {adh_appli}")
