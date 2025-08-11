
import streamlit as st
import pandas as pd

st.set_page_config(page_title="IT M&A Cost Modeling", layout="wide")

# Initialize session state
if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=["Nom", "Coût OPEX", "Coût CAPEX", "Adhérences Infra", "Adhérences Applis"])
if "infra_elements" not in st.session_state:
    st.session_state.infra_elements = pd.DataFrame(columns=["Nom", "Type", "Coût OPEX", "Coût CAPEX"])
if "mosaic_socles" not in st.session_state:
    st.session_state.mosaic_socles = pd.DataFrame(columns=["Nom", "Éléments inclus", "Coût OPEX", "Coût CAPEX"])

st.title("🧠 IT M&A Cost Modeling - Groupe Avril")

tab1, tab2 = st.tabs(["⚙️ Paramétrage", "📊 Simulation"])

with tab1:
    st.header("Paramétrage des éléments IT")

    subtab1, subtab2, subtab3 = st.tabs(["Applications", "Éléments d'Infrastructure", "Socles Mosaic"])

    with subtab1:
        st.subheader("Applications")
        st.session_state.applications = st.data_editor(
            st.session_state.applications,
            num_rows="dynamic",
            use_container_width=True
        )

    with subtab2:
        st.subheader("Éléments d'Infrastructure")
        st.session_state.infra_elements = st.data_editor(
            st.session_state.infra_elements,
            num_rows="dynamic",
            use_container_width=True
        )

    with subtab3:
        st.subheader("Socles Mosaic")
        st.markdown("Définissez les socles Mosaic (Entry, Advanced, Complete) comme des regroupements d'éléments d'infrastructure.")
        st.session_state.mosaic_socles = st.data_editor(
            st.session_state.mosaic_socles,
            num_rows="dynamic",
            use_container_width=True
        )

with tab2:
    st.header("Simulation des coûts et timings")

    st.subheader("Sélection des éléments")
    selected_apps = st.multiselect("Applications à intégrer", options=st.session_state.applications["Nom"].tolist())
    selected_infra = st.multiselect("Éléments d'infrastructure à intégrer", options=st.session_state.infra_elements["Nom"].tolist())
    selected_socles = st.multiselect("Socles Mosaic à intégrer", options=st.session_state.mosaic_socles["Nom"].tolist())

    st.subheader("Phase du projet")
    phase = st.selectbox("Choisissez la phase", ["Préparation au Closing", "Transition (TSA)", "Post-TSA"])

    # Calcul des coûts
    total_opex = 0
    total_capex = 0

    apps_df = st.session_state.applications
    infra_df = st.session_state.infra_elements
    socles_df = st.session_state.mosaic_socles

    for app in selected_apps:
        row = apps_df[apps_df["Nom"] == app]
        if not row.empty:
            total_opex += float(row["Coût OPEX"].values[0])
            total_capex += float(row["Coût CAPEX"].values[0])

    for infra in selected_infra:
        row = infra_df[infra_df["Nom"] == infra]
        if not row.empty:
            total_opex += float(row["Coût OPEX"].values[0])
            total_capex += float(row["Coût CAPEX"].values[0])

    for socle in selected_socles:
        row = socles_df[socles_df["Nom"] == socle]
        if not row.empty:
            total_opex += float(row["Coût OPEX"].values[0])
            total_capex += float(row["Coût CAPEX"].values[0])

    st.subheader("Résultat de la simulation")
    st.metric("Coût OPEX total", f"{total_opex:,.2f} €")
    st.metric("Coût CAPEX total", f"{total_capex:,.2f} €")
    st.write(f"Phase sélectionnée : **{phase}**")

    st.subheader("Adhérences détectées")
    adh_appli = []
    adh_infra = []

    for app in selected_apps:
        row = apps_df[apps_df["Nom"] == app]
        if not row.empty:
            adh_appli.extend(str(row["Adhérences Applis"].values[0]).split(","))
            adh_infra.extend(str(row["Adhérences Infra"].values[0]).split(","))

    st.write("🔗 Adhérences applicatives :", list(set(adh_appli)))
    st.write("🔌 Adhérences infrastructure :", list(set(adh_infra)))
