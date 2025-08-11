
import streamlit as st
import pandas as pd

# Initialisation des données
if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=["nom", "opex", "capex", "infra", "liens"])

if "infra_elements" not in st.session_state:
    st.session_state.infra_elements = pd.DataFrame(columns=["type", "nom", "opex", "capex"])

if "socles_mosaic" not in st.session_state:
    st.session_state.socles_mosaic = pd.DataFrame(columns=["nom", "elements", "opex", "capex"])

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
            new_app = pd.DataFrame([{
                "nom": nom_app,
                "opex": opex_app,
                "capex": capex_app,
                "infra": infra_associee,
                "liens": [x.strip() for x in autres_adhérences.split(",") if x.strip()]
            }])
            st.session_state.applications = pd.concat([st.session_state.applications, new_app], ignore_index=True)
            st.success(f"Application '{nom_app}' ajoutée.")

    with st.expander("➕ Ajouter un élément d'infrastructure"):
        type_infra = st.selectbox("Type d'infrastructure", ["PC", "LAN", "WAN", "Serveur", "Firewall", "Autre"])
        nom_infra = st.text_input("Nom de l'élément")
        opex_infra = st.number_input("OPEX annuel (€)", min_value=0.0, key="opex_infra_elem")
        capex_infra = st.number_input("CAPEX projet (€)", min_value=0.0, key="capex_infra_elem")
        if st.button("Ajouter l'élément d'infrastructure"):
            new_elem = pd.DataFrame([{
                "type": type_infra,
                "nom": nom_infra,
                "opex": opex_infra,
                "capex": capex_infra
            }])
            st.session_state.infra_elements = pd.concat([st.session_state.infra_elements, new_elem], ignore_index=True)
            st.success(f"Élément '{nom_infra}' ajouté.")

    with st.expander("➕ Ajouter un socle Mosaic"):
        nom_socle = st.text_input("Nom du socle Mosaic")
        elements_socle = st.multiselect("Éléments d'infrastructure inclus", st.session_state.infra_elements["nom"].tolist())
        opex_socle = st.number_input("OPEX annuel (€)", min_value=0.0, key="opex_socle")
        capex_socle = st.number_input("CAPEX projet (€)", min_value=0.0, key="capex_socle")
        if st.button("Ajouter le socle Mosaic"):
            new_socle = pd.DataFrame([{
                "nom": nom_socle,
                "elements": elements_socle,
                "opex": opex_socle,
                "capex": capex_socle
            }])
            st.session_state.socles_mosaic = pd.concat([st.session_state.socles_mosaic, new_socle], ignore_index=True)
            st.success(f"Socle Mosaic '{nom_socle}' ajouté.")

    with st.expander("📋 Visualiser et modifier les éléments configurés"):
        st.subheader("Applications")
        st.session_state.applications = st.data_editor(st.session_state.applications, num_rows="dynamic")

        st.subheader("Éléments d'infrastructure")
        st.session_state.infra_elements = st.data_editor(st.session_state.infra_elements, num_rows="dynamic")

        st.subheader("Socles Mosaic")
        st.session_state.socles_mosaic = st.data_editor(st.session_state.socles_mosaic, num_rows="dynamic")

elif menu == "Simulation":
    st.header("📊 Simulation des coûts IT")

    phase = st.selectbox("Phase M&A", ["Préparation au Closing", "Transition (TSA)", "Post-TSA"])

    selected_apps = st.multiselect("Sélectionner les applications", st.session_state.applications["nom"].tolist())
    selected_elements = st.multiselect("Sélectionner les éléments d'infrastructure", st.session_state.infra_elements["nom"].tolist())
    selected_socles = st.multiselect("Sélectionner les socles Mosaic", st.session_state.socles_mosaic["nom"].tolist())

    total_opex = 0
    total_capex = 0
    adhérences_detectées = []

    for _, app in st.session_state.applications.iterrows():
        if app["nom"] in selected_apps:
            total_opex += app["opex"]
            total_capex += app["capex"]
            all_socle_elements = sum(st.session_state.socles_mosaic["elements"].tolist(), [])
            if app["infra"] and app["infra"] not in selected_elements and app["infra"] not in all_socle_elements:
                adhérences_detectées.append(f"{app['nom']} nécessite l'infrastructure {app['infra']}")
            for lien in app["liens"]:
                if lien not in selected_apps:
                    adhérences_detectées.append(f"{app['nom']} est lié à l'application {lien}")

    for _, elem in st.session_state.infra_elements.iterrows():
        if elem["nom"] in selected_elements:
            total_opex += elem["opex"]
            total_capex += elem["capex"]

    for _, socle in st.session_state.socles_mosaic.iterrows():
        if socle["nom"] in selected_socles:
            total_opex += socle["opex"]
            total_capex += socle["capex"]

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
