
import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="IT M&A Scenario App", layout="wide")

st.title("🧩 IT M&A Scenario Simulator")

# --- Sidebar for mode selection ---
mode = st.sidebar.radio("Choisir le mode", ["Administrateur", "Utilisateur"], key="mode_selector")

# --- Shared Data Stores ---
if "applications" not in st.session_state:
    st.session_state["applications"] = pd.DataFrame(columns=["Nom", "CAPEX (€)", "OPEX (€ / an)"])
if "infra_elements" not in st.session_state:
    st.session_state["infra_elements"] = pd.DataFrame(columns=["Nom", "CAPEX (€)", "OPEX (€ / an)"])
if "mosaic_socles" not in st.session_state:
    st.session_state["mosaic_socles"] = {
        "Entry": [],
        "Advanced": [],
        "Complete": []
    }
if "adh_app_app" not in st.session_state:
    st.session_state["adh_app_app"] = pd.DataFrame(columns=["Application Source", "Application Cible"])
if "adh_app_socle" not in st.session_state:
    st.session_state["adh_app_socle"] = pd.DataFrame(columns=["Application", "Socle Mosaic"])
if "entites" not in st.session_state:
    st.session_state["entites"] = {}

# --- Administrateur View ---
if mode == "Administrateur":
    st.header("🔧 Vue Administrateur")

    st.subheader("Définir les applications")
    st.session_state["applications"] = st.data_editor(
        st.session_state["applications"], num_rows="dynamic", use_container_width=True, key="admin_app_editor"
    )

    st.subheader("Définir les éléments d'infrastructure")
    st.session_state["infra_elements"] = st.data_editor(
        st.session_state["infra_elements"], num_rows="dynamic", use_container_width=True, key="admin_infra_editor"
    )

    st.subheader("Définir les socles Mosaic")
    for socle in st.session_state["mosaic_socles"].keys():
        selected_elements = st.multiselect(
            f"Éléments pour le socle {socle}", 
            st.session_state["infra_elements"]["Nom"].tolist(), 
            default=st.session_state["mosaic_socles"][socle], 
            key=f"mosaic_{socle}_select"
        )
        st.session_state["mosaic_socles"][socle] = selected_elements

    st.subheader("Définir les adhérences entre applications")
    st.session_state["adh_app_app"] = st.data_editor(
        st.session_state["adh_app_app"], num_rows="dynamic", use_container_width=True, key="admin_adh_app_app"
    )

    st.subheader("Définir les adhérences entre applications et socles Mosaic")
    st.session_state["adh_app_socle"] = st.data_editor(
        st.session_state["adh_app_socle"], num_rows="dynamic", use_container_width=True, key="admin_adh_app_socle"
    )

    st.subheader("Créer des environnements IT par entité juridique")
    entite_name = st.text_input("Nom de l'entité juridique", key="entite_name_input")
    if entite_name:
        selected_apps = st.multiselect(
            "Applications pour cette entité", 
            st.session_state["applications"]["Nom"].tolist(), 
            key="entite_apps_select"
        )
        selected_socle = st.selectbox("Socle Mosaic pour cette entité", list(st.session_state["mosaic_socles"].keys()), key="entite_socle_select")
        if st.button("Enregistrer l'environnement IT", key="save_entite_env"):
            st.session_state["entites"][entite_name] = {
                "applications": selected_apps,
                "socle": selected_socle
            }
            st.success(f"Environnement IT enregistré pour l'entité {entite_name}")

# --- Utilisateur View ---
if mode == "Utilisateur":
    st.header("👤 Vue Utilisateur")

    entite_selected = st.selectbox("Sélectionner une entité juridique", list(st.session_state["entites"].keys()), key="user_entite_select")
    if entite_selected:
        entite_data = st.session_state["entites"][entite_selected]
        apps = entite_data["applications"]
        socle = entite_data["socle"]
        infra_elements = st.session_state["mosaic_socles"][socle]

        st.subheader("📦 Éléments IT sélectionnés")
        st.write("**Applications :**", apps)
        st.write("**Socle Mosaic :**", socle)
        st.write("**Éléments d'infrastructure :**", infra_elements)

        # Récupérer les coûts
        all_elements = apps + infra_elements
        costs = []
        for el in all_elements:
            app_row = st.session_state["applications"][st.session_state["applications"]["Nom"] == el]
            infra_row = st.session_state["infra_elements"][st.session_state["infra_elements"]["Nom"] == el]
            if not app_row.empty:
                capex = app_row["CAPEX (€)"].values[0]
                opex = app_row["OPEX (€ / an)"].values[0]
            elif not infra_row.empty:
                capex = infra_row["CAPEX (€)"].values[0]
                opex = infra_row["OPEX (€ / an)"].values[0]
            else:
                capex = 0
                opex = 0
            costs.append({"Élément": el, "CAPEX (€)": capex, "OPEX (€ / an)": opex})

        costs_df = pd.DataFrame(costs)

        st.subheader("📈 Simulation des coûts par phase M&A")
        phases = ["Préparation au Closing", "Transition (TSA)", "Post-TSA"]
        phase_durations = {
            "Préparation au Closing": 3,
            "Transition (TSA)": 6,
            "Post-TSA": 12
        }

        simulation = []
        for _, row in costs_df.iterrows():
            for phase in phases:
                simulation.append({
                    "Élément": row["Élément"],
                    "Phase": phase,
                    "Durée (mois)": phase_durations[phase],
                    "CAPEX (€)": row["CAPEX (€)"] if phase == "Préparation au Closing" else 0,
                    "OPEX (€)": row["OPEX (€ / an)"] * (phase_durations[phase] / 12)
                })

        sim_df = pd.DataFrame(simulation)
        st.dataframe(sim_df, use_container_width=True, key="user_simulation_table")
