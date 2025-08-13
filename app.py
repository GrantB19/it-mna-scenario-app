
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Initialisation des données en session
if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=["Nom", "Opex", "Capex", "Adherences"])

# Fonction pour nettoyer et intégrer un fichier Excel
def importer_applications_excel():
    fichier = st.file_uploader("Importer un fichier Excel avec les applications", type=["xlsx"])
    if fichier:
        try:
            df = pd.read_excel(fichier, engine="openpyxl")
            df.columns = [col.strip().capitalize() for col in df.columns]
            colonnes_attendues = ["Nom", "Opex", "Capex", "Adherences"]
            for col in colonnes_attendues:
                if col not in df.columns:
                    df[col] = ""
            df = df[colonnes_attendues]
            df.drop_duplicates(subset=["Nom"], inplace=True)
            df["Nom"] = df["Nom"].astype(str).str.strip()
            df["Adherences"] = df["Adherences"].fillna("").astype(str)
            st.session_state.applications = pd.concat([st.session_state.applications, df], ignore_index=True).drop_duplicates(subset=["Nom"])
            st.success("Applications importées avec succès.")
        except Exception as e:
            st.error(f"Erreur lors de l'import : {e}")

# Interface principale
st.title("Due Diligence IT - Vue 1 : Base de données")
st.subheader("Ajouter une application manuellement")
col1, col2, col3 = st.columns(3)
with col1:
    nom_app = st.text_input("Nom de l'application")
with col2:
    opex_app = st.number_input("Coût Opex", min_value=0.0, step=100.0)
with col3:
    capex_app = st.number_input("Coût Capex", min_value=0.0, step=100.0)
adherences_app = st.text_input("Adhérences (séparées par des virgules)")

if st.button("Ajouter l'application"):
    if nom_app:
        nouvelle_ligne = {
            "Nom": nom_app.strip(),
            "Opex": opex_app,
            "Capex": capex_app,
            "Adherences": adherences_app
        }
        st.session_state.applications = pd.concat([
            st.session_state.applications,
            pd.DataFrame([nouvelle_ligne])
        ], ignore_index=True).drop_duplicates(subset=["Nom"])
        st.success(f"Application '{nom_app}' ajoutée.")
    else:
        st.warning("Veuillez saisir un nom d'application.")

st.markdown("---")
st.subheader("Importer des applications depuis un fichier Excel")
importer_applications_excel()

st.markdown("---")
st.subheader("Liste des applications enregistrées")
st.dataframe(st.session_state.applications, use_container_width=True)
