
import streamlit as st
import pandas as pd

# Initialisation des données
if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=["Nom", "Opex", "Capex"])
if "infrastructures" not in st.session_state:
    st.session_state.infrastructures = pd.DataFrame(columns=["Nom", "Opex", "Capex"])
if "mosaic" not in st.session_state:
    st.session_state.mosaic = {"Entry": [], "Advanced": [], "Complete": []}
if "adhérences_app" not in st.session_state:
    st.session_state.adhérences_app = []
if "adhérences_mosaic" not in st.session_state:
    st.session_state.adhérences_mosaic = []
if "entités" not in st.session_state:
    st.session_state.entités = []

# Vue sélectionnée
vue = st.sidebar.selectbox("Choisir la vue", ["Base de données", "Environnements existants", "Extrapolation cible"])

# Vue 1 : Base de données
if vue == "Base de données":
    st.header("Vue 1 : Base de données")

    st.subheader("Ajouter une application")
    nom_app = st.text_input("Nom de l'application")
    opex_app = st.number_input("Opex", min_value=0.0)
    capex_app = st.number_input("Capex", min_value=0.0)
    if st.button("Ajouter application") and nom_app:
        st.session_state.applications.loc[len(st.session_state.applications)] = [nom_app, opex_app, capex_app]

    st.subheader("Ajouter une infrastructure")
    nom_inf = st.text_input("Nom de l'infrastructure")
    opex_inf = st.number_input("Opex infra", min_value=0.0, key="opex_inf")
    capex_inf = st.number_input("Capex infra", min_value=0.0, key="capex_inf")
    if st.button("Ajouter infrastructure") and nom_inf:
        st.session_state.infrastructures.loc[len(st.session_state.infrastructures)] = [nom_inf, opex_inf, capex_inf]

    st.subheader("Composer les socles Mosaic")
    infra_options = st.session_state.infrastructures["Nom"].tolist() if not st.session_state.infrastructures.empty else []
    for niveau in ["Entry", "Advanced", "Complete"]:
        selection = st.multiselect(f"{niveau}", infra_options, default=st.session_state.mosaic[niveau])
        st.session_state.mosaic[niveau] = selection

    st.subheader("Définir les adhérences entre applications")
    app_options = st.session_state.applications["Nom"].tolist() if not st.session_state.applications.empty else []
    if len(app_options) >= 2:
        app1 = st.selectbox("Application source", app_options)
        app2 = st.selectbox("Application cible", app_options, index=1)
        if st.button("Ajouter adhérence application"):
            st.session_state.adhérences_app.append((app1, app2))

    st.subheader("Définir les adhérences entre applications et Mosaic")
    mosaic_options = list(st.session_state.mosaic.keys())
    if app_options:
        app_mosaic = st.selectbox("Application", app_options, key="app_mosaic")
        mosaic_sel = st.selectbox("Socle Mosaic", mosaic_options)
        if st.button("Ajouter adhérence Mosaic"):
            st.session_state.adhérences_mosaic.append((app_mosaic, mosaic_sel))

    st.subheader("Visualisation des données")
    st.write("Applications", st.session_state.applications)
    st.write("Infrastructures", st.session_state.infrastructures)
    st.write("Socles Mosaic", st.session_state.mosaic)
    st.write("Adhérences Applications", st.session_state.adhérences_app)
    st.write("Adhérences Mosaic", st.session_state.adhérences_mosaic)

# Vue 2 : Environnements existants
elif vue == "Environnements existants":
    st.header("Vue 2 : Environnements entités existants")

    domaines = ["ASA", "AGC", "APTER", "AD", "AIS"]
    nom_entité = st.text_input("Nom de l'entité")
    domaine = st.selectbox("Domaine", domaines)
    apps_entité = st.multiselect("Applications", st.session_state.applications["Nom"].tolist() if not st.session_state.applications.empty else [])
    mosaic_entité = st.selectbox("Socle Mosaic", list(st.session_state.mosaic.keys()))
    if st.button("Créer entité existante") and nom_entité:
        st.session_state.entités.append({
            "Nom": nom_entité,
            "Domaine": domaine,
            "Applications": apps_entité,
            "Mosaic": mosaic_entité
        })

    st.subheader("Entités existantes")
    for ent in st.session_state.entités:
        st.write(ent)

# Vue 3 : Extrapolation cible
elif vue == "Extrapolation cible":
    st.header("Vue 3 : Extrapolation d'environnement cible")

    domaines = ["ASA", "AGC", "APTER", "AD", "AIS"]
    nom_entité = st.text_input("Nom de l'entité cible")
    domaine = st.selectbox("Domaine cible", domaines, key="domaine_cible")
    apps_entité = st.multiselect("Applications cible", st.session_state.applications["Nom"].tolist() if not st.session_state.applications.empty else [], key="apps_cible")

    # Recommandation automatique du socle Mosaic
    if len(apps_entité) <= 3:
        mosaic_reco = "Entry"
    elif len(apps_entité) <= 6:
        mosaic_reco = "Advanced"
    else:
        mosaic_reco = "Complete"

    st.write(f"Socle Mosaic recommandé : {mosaic_reco}")

    if st.button("Créer entité cible") and nom_entité:
        st.session_state.entités.append({
            "Nom": nom_entité,
            "Domaine": domaine,
            "Applications": apps_entité,
            "Mosaic": mosaic_reco
        })

    st.subheader("Entités extrapolées")
    for ent in st.session_state.entités:
        st.write(ent)
