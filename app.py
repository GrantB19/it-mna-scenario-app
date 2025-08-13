
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
    st.session_state.entités = pd.DataFrame(columns=["Nom", "Domaine", "Applications", "Socle Mosaic"])

# Navigation
vue = st.sidebar.selectbox("Choisir la vue", ["Base de données", "Création des environnements"])

if vue == "Base de données":
    st.header("📊 Base de données")

    st.subheader("Ajouter une application")
    nom_app = st.text_input("Nom de l'application")
    opex_app = st.number_input("Coût Opex", min_value=0.0)
    capex_app = st.number_input("Coût Capex", min_value=0.0)
    if st.button("Ajouter application"):
        st.session_state.applications.loc[len(st.session_state.applications)] = [nom_app, opex_app, capex_app]

    st.subheader("Ajouter une infrastructure")
    nom_inf = st.text_input("Nom de l'infrastructure")
    opex_inf = st.number_input("Coût Opex infra", min_value=0.0, key="opex_inf")
    capex_inf = st.number_input("Coût Capex infra", min_value=0.0, key="capex_inf")
    if st.button("Ajouter infrastructure"):
        st.session_state.infrastructures.loc[len(st.session_state.infrastructures)] = [nom_inf, opex_inf, capex_inf]

    st.subheader("Composer les socles Mosaic")
    for socle in st.session_state.mosaic.keys():
        st.markdown(f"**{socle}**")
        selected = st.multiselect(f"Éléments pour {socle}", st.session_state.infrastructures["Nom"].tolist(), key=socle)
        st.session_state.mosaic[socle] = selected

    st.subheader("Définir les adhérences entre applications")
    app1 = st.selectbox("Application source", st.session_state.applications["Nom"].tolist(), key="app1")
    app2 = st.selectbox("Application cible", st.session_state.applications["Nom"].tolist(), key="app2")
    if st.button("Ajouter adhérence app"):
        st.session_state.adhérences_app.append((app1, app2))

    st.subheader("Définir les adhérences entre applications et socles Mosaic")
    app_m = st.selectbox("Application", st.session_state.applications["Nom"].tolist(), key="app_m")
    socle_m = st.selectbox("Socle Mosaic", list(st.session_state.mosaic.keys()), key="socle_m")
    if st.button("Ajouter adhérence Mosaic"):
        st.session_state.adhérences_mosaic.append((app_m, socle_m))

    st.subheader("Importer un fichier Excel")
    fichier = st.file_uploader("Importer un fichier Excel", type=["xlsx"])
    if fichier:
        df_import = pd.read_excel(fichier, engine="openpyxl")
        st.write(df_import)

    st.subheader("Visualisation des données")
    st.write("Applications", st.session_state.applications)
    st.write("Infrastructures", st.session_state.infrastructures)
    st.write("Socles Mosaic", st.session_state.mosaic)
    st.write("Adhérences Applications", st.session_state.adhérences_app)
    st.write("Adhérences Applications-Socles", st.session_state.adhérences_mosaic)

elif vue == "Création des environnements":
    st.header("🏗️ Création des environnements")

    st.subheader("Créer une entité")
    nom_entité = st.text_input("Nom de l'entité")
    domaine = st.selectbox("Domaine", ["ASA", "AGC", "APTER", "AD", "AIS"])
    apps_entité = st.multiselect("Applications associées", st.session_state.applications["Nom"].tolist())
    socle_entité = st.selectbox("Socle Mosaic associé", list(st.session_state.mosaic.keys()))
    if st.button("Ajouter entité"):
        st.session_state.entités.loc[len(st.session_state.entités)] = [nom_entité, domaine, apps_entité, socle_entité]

    st.subheader("Visualisation des entités")
    st.write(st.session_state.entités)
