import streamlit as st
import pandas as pd
# Initial setup
st.set_page_config(page_title="Due Diligence IT M&A", layout="wide")
# Session state initialization
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
st.session_state.entités = pd.DataFrame(columns=["Nom", "Domaine", "Applications",
"Socle Mosaic"])
# Sidebar navigation
view = st.sidebar.radio("Choisir la vue", ["Base de données", "Création des
environnements"])
# Vue 1 : Base de données
if view == "Base de données":
st.title("Vue 1 : Base de données")
st.subheader("Ajouter une application")
nom_app = st.text_input("Nom de l'application")
opex_app = st.number_input("Coût Opex", min_value=0.0)
capex_app = st.number_input("Coût Capex", min_value=0.0)
if st.button("Ajouter application"):
st.session_state.applications.loc[len(st.session_state.applications)] =
[nom_app, opex_app, capex_app]
st.subheader("Ajouter une infrastructure")
nom_inf = st.text_input("Nom de l'infrastructure")
opex_inf = st.number_input("Coût Opex infra", min_value=0.0, key="opex_inf")
capex_inf = st.number_input("Coût Capex infra", min_value=0.0, key="capex_inf")
if st.button("Ajouter infrastructure"):
st.session_state.infrastructures.loc[len(st.session_state.infrastructures)] =
[nom_inf, opex_inf, capex_inf]
st.subheader("Composer les socles Mosaic")
for socle in st.session_state.mosaic.keys():
st.write(f"Socle {socle}")
selected = st.multiselect(f"Choisir les infrastructures pour {socle}",
st.session_state.infrastructures["Nom"].tolist(), key=socle)
st.session_state.mosaic[socle] = selected
st.subheader("Définir les adhérences entre applications")
app1 = st.selectbox("Application source",
st.session_state.applications["Nom"].tolist(), key="app1")
app2 = st.selectbox("Application cible",
st.session_state.applications["Nom"].tolist(), key="app2")
if st.button("Ajouter adhérence application"):
st.session_state.adhérences_app.append((app1, app2))
st.subheader("Définir les adhérences entre applications et socles Mosaic")
app_mosaic = st.selectbox("Application",
st.session_state.applications["Nom"].tolist(), key="app_mosaic")
socle_mosaic = st.selectbox("Socle Mosaic", list(st.session_state.mosaic.keys()),
key="socle_mosaic")
if st.button("Ajouter adhérence Mosaic"):
st.session_state.adhérences_mosaic.append((app_mosaic, socle_mosaic))
st.subheader("Importer un fichier Excel")
uploaded_file = st.file_uploader("Importer un fichier Excel", type=["xlsx"])
if uploaded_file:
df_uploaded = pd.read_excel(uploaded_file, engine="openpyxl")
st.write("Contenu du fichier importé :")
st.dataframe(df_uploaded)
st.subheader("Applications enregistrées")
st.dataframe(st.session_state.applications)
st.subheader("Infrastructures enregistrées")
st.dataframe(st.session_state.infrastructures)
# Vue 2 : Création des environnements
elif view == "Création des environnements":
st.title("Vue 2 : Création des environnements")
st.subheader("Créer une entité du Groupe Avril")
nom_entité = st.text_input("Nom de l'entité")
domaine = st.selectbox("Domaine", ["ASA", "AGC", "APTER", "AD", "AIS"])
apps_entité = st.multiselect("Applications associées",
st.session_state.applications["Nom"].tolist())
socle_entité = st.selectbox("Socle Mosaic associé",
list(st.session_state.mosaic.keys()))
if st.button("Ajouter entité"):
st.session_state.entités.loc[len(st.session_state.entités)] = [nom_entité,
domaine, apps_entité, socle_entité]
st.subheader("Entités du Groupe Avril")
st.dataframe(st.session_state.entités)
