
import streamlit as st
import pandas as pd
import os

st.title("Due Diligence IT M&A - Avril")

st.sidebar.header("Navigation")
view = st.sidebar.selectbox("Choisir une vue", ["Applications", "Infrastructures", "Socles Mosaic", "Adhérences", "Entités"])

data_dir = "streamlit_due_diligence_data"

if view == "Applications":
    st.header("Applications")
    df = pd.read_csv(os.path.join(data_dir, "Feuil1.csv"))
    st.dataframe(df)

elif view == "Infrastructures":
    st.header("Infrastructures")
    df = pd.read_csv(os.path.join(data_dir, "Feuil1.csv"))
    st.dataframe(df)

elif view == "Socles Mosaic":
    st.header("Socles Mosaic")
    df = pd.read_csv(os.path.join(data_dir, "Feuil1.csv"))
    st.dataframe(df)

elif view == "Adhérences":
    st.header("Adhérences entre applications")
    df = pd.read_csv(os.path.join(data_dir, "Feuil1.csv"))
    st.dataframe(df)

elif view == "Entités":
    st.header("Entités du Groupe Avril")
    df = pd.read_csv(os.path.join(data_dir, "Feuil1.csv"))
    st.dataframe(df)
