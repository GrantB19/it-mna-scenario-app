import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Initialisation des données
if "applications" not in st.session_state:
    st.session_state.applications = []

if "infrastructures" not in st.session_state:
    st.session_state.infrastructures = []

if "adhérences" not in st.session_state:
    st.session_state.adhérences = []

st.title("🧠 IT M&A - Modélisation des coûts OPEX & CAPEX")

menu = st.sidebar.radio("Menu", ["Paramétrage", "Simulation"])

if menu == "Paramétrage":
    st.header("🔧 Paramétrage des environnements IT")

    with st.expander("➕ Ajouter une application"):
        nom_app = st.text_input("Nom de l'application")
        opex_app = st.number_input("Coût OPEX annuel (€)", min_value=0.0)
        capex_app = st.number_input("Coût CAPEX projet (€)", min_value=0.0)
        infra_associee = st.text_input("Nom de l'infrastructure associée")
        autres_adhérences = st.text_input("Autres applications liées (séparées par des virgules)")

        if st.button("Ajouter l'application"):
            st.session_state.applications.append({
                "nom": nom_app,
                "opex": opex_app,
                "capex": capex_app,
                "infra": infra_associee,
                "liens": [x.strip() for x in autres_adhérences.split(",") if x.strip()]
            })
            st.success(f"Application '{nom_app}' ajoutée.")

    with st.expander("➕ Ajouter une infrastructure"):
        nom_infra = st.text_input("Nom de l'infrastructure")
        contenu_infra = st.text_area("Contenu (serveurs, réseau, etc.)")
        opex_infra = st.number_input("OPEX annuel infra (€)", min_value=0.0, key="opex_infra")
        capex_infra = st.number_input("CAPEX projet infra (€)", min_value=0.0, key="capex_infra")

        if st.button("Ajouter l'infrastructure"):
            st.session_state.infrastructures.append({
                "nom": nom_infra,
                "contenu": contenu_infra,
                "opex": opex_infra,
                "capex": capex_infra
            })
            st.success(f"Infrastructure '{nom_infra}' ajoutée.")

    with st.expander("📋 Visualiser les éléments configurés"):
        st.subheader("Applications")
        for app in st.session_state.applications:
            st.write(app)

        st.subheader("Infrastructures")
        for infra in st.session_state.infrastructures:
            st.write(infra)

elif menu == "Simulation":
    st.header("📊 Simulation des coûts IT")

    phase = st.selectbox("Phase M&A", ["Préparation au Closing", "Transition (TSA)", "Post-TSA"])

    selected_apps = st.multiselect("Sélectionner les applications", [app["nom"] for app in st.session_state.applications])
    selected_infras = st.multiselect("Sélectionner les infrastructures", [infra["nom"] for infra in st.session_state.infrastructures])

    total_opex = 0
    total_capex = 0
    adhérences_detectées = []

    for app in st.session_state.applications:
        if app["nom"] in selected_apps:
            total_opex += app["opex"]
            total_capex += app["capex"]
            if app["infra"] and app["infra"] not in selected_infras:
                adhérences_detectées.append(f"{app['nom']} nécessite l'infrastructure {app['infra']}")
            for lien in app["liens"]:
                if lien not in selected_apps:
                    adhérences_detectées.append(f"{app['nom']} est lié à l'application {lien}")

    for infra in st.session_state.infrastructures:
        if infra["nom"] in selected_infras:
            total_opex += infra["opex"]
            total_capex += infra["capex"]

    st.subheader("🧮 Résultat de la simulation")
    st.write(f"Phase sélectionnée : **{phase}**")
    st.write(f"Coût OPEX total : **{total_opex:,.2f} €**")
    st.write(f"Coût CAPEX total : **{total_capex:,.2f} €**")

    if adhérences_detectées:
        st.warning("⚠️ Adhérences détectées :")
        for a in adhérences_detectées:
            st.write(f"- {a}")
    else:
        st.success("✅ Aucun problème d'adhérence détecté.")
