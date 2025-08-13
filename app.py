
import streamlit as st
import pandas as pd
import os
import zipfile

# Initialisation des données en session
if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=["Nom", "Opex", "Capex", "Adherences"])

# Fonction de nettoyage et ajout des données depuis Excel
def importer_applications_excel(fichier_excel):
    try:
        df = pd.read_excel(fichier_excel, engine="openpyxl")
        # Nettoyage : suppression des doublons, remplissage des colonnes manquantes
        df = df.drop_duplicates()
        for col in ["Nom", "Opex", "Capex", "Adherences"]:
            if col not in df.columns:
                df[col] = ""
        df["Nom"] = df["Nom"].astype(str).str.strip()
        df["Adherences"] = df["Adherences"].fillna("").astype(str).str.strip()
        # Ajout à la base existante
        st.session_state.applications = pd.concat([st.session_state.applications, df], ignore_index=True)
        st.success("Importation réussie et données ajoutées.")
    except Exception as e:
        st.error(f"Erreur lors de l'importation : {e}")

# Interface Streamlit
st.title("Vue 1 : Base de données des applications")

# Formulaire d'import Excel
st.subheader("Importer un fichier Excel pour compléter les applications")
fichier_excel = st.file_uploader("Déposez un fichier Excel (.xlsx)", type=["xlsx"])
if fichier_excel:
    importer_applications_excel(fichier_excel)

# Affichage des données actuelles
st.subheader("Applications enregistrées")
st.dataframe(st.session_state.applications)
