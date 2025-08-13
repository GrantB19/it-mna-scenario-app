
import streamlit as st
import pandas as pd

# Initialisation des données dans la session
if "applications" not in st.session_state:
    st.session_state.applications = []

if "infrastructures" not in st.session_state:
    st.session_state.infrastructures = []

if "mosaic" not in st.session_state:
    st.session_state.mosaic = {
        "Entry": [],
        "Advanced": [],
        "Complete": []
    }

if "adhérences_app" not in st.session_state:
    st.session_state.adhérences_app = []

if "adhérences_mosaic" not in st.session_state:
    st.session_state.adhérences_mosaic = []

if "entités" not in st.session_state:
    st.session_state.entités = []

# Vue sélectionnée
vue = st.sidebar.selectbox("Choisir la vue", ["Base de données", "Création des environnements", "Visualisation des coûts"])

# Vue 1 : Base de données
if vue == "Base de données":
    st.title("Base de données IT")

    st.subheader("Ajouter une application")
    nom_app = st.text_input("Nom de l'application")
    opex_app = st.number_input("Coût Opex", min_value=0.0)
    capex_app = st.number_input("Coût Capex", min_value=0.0)
    if st.button("Ajouter l'application"):
        st.session_state.applications.append({"nom": nom_app, "opex": opex_app, "capex": capex_app})

    st.subheader("Ajouter un élément d'infrastructure")
    nom_inf = st.text_input("Nom de l'infrastructure")
    opex_inf = st.number_input("Coût Opex infra", min_value=0.0, key="opex_inf")
    capex_inf = st.number_input("Coût Capex infra", min_value=0.0, key="capex_inf")
    if st.button("Ajouter l'infrastructure"):
        st.session_state.infrastructures.append({"nom": nom_inf, "opex": opex_inf, "capex": capex_inf})

    st.subheader("Composer les socles Mosaic")
    socle = st.selectbox("Choisir le socle", ["Entry", "Advanced", "Complete"])
    infra_select = st.multiselect("Sélectionner les infrastructures", [i["nom"] for i in st.session_state.infrastructures])
    if st.button("Ajouter au socle"):
        st.session_state.mosaic[socle] = infra_select

    st.subheader("Définir les adhérences entre applications")
    app1 = st.selectbox("Application source", [a["nom"] for a in st.session_state.applications], key="app1")
    app2 = st.selectbox("Application cible", [a["nom"] for a in st.session_state.applications], key="app2")
    if st.button("Ajouter adhérence application"):
        st.session_state.adhérences_app.append((app1, app2))

    st.subheader("Définir les adhérences entre applications et socles Mosaic")
    app_mosaic = st.selectbox("Application", [a["nom"] for a in st.session_state.applications], key="app_mosaic")
    socle_mosaic = st.selectbox("Socle Mosaic", ["Entry", "Advanced", "Complete"], key="socle_mosaic")
    if st.button("Ajouter adhérence Mosaic"):
        st.session_state.adhérences_mosaic.append((app_mosaic, socle_mosaic))

    st.subheader("Applications enregistrées")
    st.dataframe(pd.DataFrame(st.session_state.applications))

    st.subheader("Infrastructures enregistrées")
    st.dataframe(pd.DataFrame(st.session_state.infrastructures))

# Vue 2 : Création des environnements
elif vue == "Création des environnements":
    st.title("Création des environnements")

    st.subheader("Créer une entité")
    nom_entité = st.text_input("Nom de l'entité")
    domaine = st.selectbox("Domaine", ["ASA", "AGC", "APTER", "AD", "AIS"])
    apps_entité = st.multiselect("Applications de l'entité", [a["nom"] for a in st.session_state.applications])
    socle_entité = st.selectbox("Socle Mosaic", ["Entry", "Advanced", "Complete"])
    if st.button("Ajouter l'entité"):
        st.session_state.entités.append({
            "nom": nom_entité,
            "domaine": domaine,
            "applications": apps_entité,
            "socle": socle_entité
        })

    st.subheader("Entités du Groupe Avril")
    st.dataframe(pd.DataFrame(st.session_state.entités))

# Vue 3 : Visualisation des coûts
elif vue == "Visualisation des coûts":
    st.title("Visualisation des coûts IT")

    data = []
    for entité in st.session_state.entités:
        opex_total = 0
        capex_total = 0

        # Coûts des applications
        for app in entité["applications"]:
            for a in st.session_state.applications:
                if a["nom"] == app:
                    opex_total += a["opex"]
                    capex_total += a["capex"]

        # Coûts des infrastructures du socle
        socle = entité["socle"]
        for infra_nom in st.session_state.mosaic.get(socle, []):
            for i in st.session_state.infrastructures:
                if i["nom"] == infra_nom:
                    opex_total += i["opex"]
                    capex_total += i["capex"]

        data.append({
            "Entité": entité["nom"],
            "Domaine": entité["domaine"],
            "Socle": socle,
            "Opex Total": opex_total,
            "Capex Total": capex_total
        })

    st.subheader("Tableau récapitulatif des coûts")
    df_costs = pd.DataFrame(data)
    st.dataframe(df_costs)
