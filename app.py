
import streamlit as st
import pandas as pd

# Initialisation des données
if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=["Nom", "Opex", "Capex", "Adherences", "Socles"])
if "infrastructures" not in st.session_state:
    st.session_state.infrastructures = pd.DataFrame(columns=["Nom", "Opex", "Capex"])
if "socles" not in st.session_state:
    st.session_state.socles = {
        "Mosaic Entry": [],
        "Mosaic Advanced": [],
        "Mosaic Complete": []
    }
if "entites" not in st.session_state:
    st.session_state.entites = pd.DataFrame(columns=["Nom", "Domaine", "Applications", "Socle Mosaic"])

# Vue 1 : Base de données
def vue_base_de_donnees():
    st.header("Vue 1 : Base de données")

    st.subheader("Ajouter une application")
    nom_app = st.text_input("Nom de l'application")
    opex_app = st.number_input("Coût Opex", min_value=0.0)
    capex_app = st.number_input("Coût Capex", min_value=0.0)
    adherences_app = st.text_input("Adhérences (séparées par des virgules)")
    socles_app = st.multiselect("Socles nécessaires", ["Mosaic Entry", "Mosaic Advanced", "Mosaic Complete"])
    if st.button("Ajouter l'application"):
        st.session_state.applications.loc[len(st.session_state.applications)] = [nom_app, opex_app, capex_app, adherences_app.split(","), socles_app]

    st.subheader("Ajouter une infrastructure")
    nom_inf = st.text_input("Nom de l'infrastructure")
    opex_inf = st.number_input("Opex Infra", min_value=0.0, key="opex_inf")
    capex_inf = st.number_input("Capex Infra", min_value=0.0, key="capex_inf")
    if st.button("Ajouter l'infrastructure"):
        st.session_state.infrastructures.loc[len(st.session_state.infrastructures)] = [nom_inf, opex_inf, capex_inf]

    st.subheader("Composer les socles Mosaic")
    for socle in st.session_state.socles.keys():
        selected_infra = st.multiselect(f"{socle}", st.session_state.infrastructures["Nom"].tolist(), key=socle)
        st.session_state.socles[socle] = selected_infra

    st.subheader("Applications enregistrées")
    st.dataframe(st.session_state.applications)

st.subheader("Infrastructures enregistrées")
    st.dataframe(st.session_state.infrastructures)

# Vue 2 : Environnements entités existantes
def vue_entites_existantes():
    st.header("Vue 2 : Environnements des entités existantes")

    nom_entite = st.text_input("Nom de l'entité")
    domaine = st.selectbox("Domaine", ["ASA", "AGC", "APTER", "AD", "AIS"])
    apps_dispo = st.session_state.applications["Nom"].tolist()
    apps_entite = st.multiselect("Applications de l'entité", apps_dispo)
    socle_entite = st.selectbox("Socle Mosaic", ["Mosaic Entry", "Mosaic Advanced", "Mosaic Complete"])
    if st.button("Créer l'entité"):
        st.session_state.entites.loc[len(st.session_state.entites)] = [nom_entite, domaine, apps_entite, socle_entite]

    st.subheader("Entités existantes")
    st.dataframe(st.session_state.entites)

# Vue 3 : Extrapolation d’environnement cible
def vue_extrapolation():
    st.header("Vue 3 : Extrapolation d’environnement cible")

    nom_entite = st.text_input("Nom de l'entité cible")
    domaine = st.selectbox("Domaine cible", ["ASA", "AGC", "APTER", "AD", "AIS"], key="domaine_cible")
    apps_dispo = st.session_state.applications["Nom"].tolist()
    apps_entite = st.multiselect("Applications de l'entité cible", apps_dispo, key="apps_cible")

    # Déduction du socle recommandé
    socles_requis = []
    for app in apps_entite:
        row = st.session_state.applications[st.session_state.applications["Nom"] == app]
        if not row.empty:
            socles_requis.extend(row.iloc[0]["Socles"])
    socles_requis = list(set(socles_requis))

    if "Mosaic Complete" in socles_requis:
        socle_recommande = "Mosaic Complete"
    elif "Mosaic Advanced" in socles_requis:
        socle_recommande = "Mosaic Advanced"
    else:
        socle_recommande = "Mosaic Entry"

    st.success(f"Socle Mosaic recommandé : {socle_recommande}")

    if st.button("Créer l'entité cible"):
        st.session_state.entites.loc[len(st.session_state.entites)] = [nom_entite, domaine, apps_entite, socle_recommande]

    st.subheader("Entités avec extrapolation")
    st.dataframe(st.session_state.entites)

# Navigation
st.sidebar.title("Navigation")
vue = st.sidebar.radio("Choisir une vue", ["Base de données", "Entités existantes", "Extrapolation cible"])

if vue == "Base de données":
    vue_base_de_donnees()
elif vue == "Entités existantes":
    vue_entites_existantes()
elif vue == "Extrapolation cible":
    vue_extrapolation()
