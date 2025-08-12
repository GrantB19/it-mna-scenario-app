
import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="IT M&A Scenario App", layout="wide")

# --- Session State Initialization ---
if "mode" not in st.session_state:
    st.session_state.mode = "Utilisateur"

if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=["Nom", "CAPEX (€)", "OPEX (€ / an)"])

if "infra_elements" not in st.session_state:
    st.session_state.infra_elements = pd.DataFrame(columns=["Nom", "CAPEX (€)", "OPEX (€ / an)"])

if "mosaic_socles" not in st.session_state:
    st.session_state.mosaic_socles = {
        "Entry": [],
        "Advanced": [],
        "Complete": []
    }

if "adh_app_app" not in st.session_state:
    st.session_state.adh_app_app = pd.DataFrame(columns=["Application Source", "Application Cible", "Type d'Adhérence"])

if "adh_app_socle" not in st.session_state:
    st.session_state.adh_app_socle = pd.DataFrame(columns=["Application", "Socle Mosaic", "Type d'Adhérence"])

if "environnements" not in st.session_state:
    st.session_state.environnements = pd.DataFrame(columns=["Entité Juridique", "Applications", "Socle Mosaic"])

# --- Mode Selection ---
st.sidebar.title("🔐 Sélection du Mode")
mode = st.sidebar.radio("Choisir le mode :", ["Administrateur", "Utilisateur"])
st.session_state.mode = mode

# --- ADMINISTRATEUR MODE ---
if st.session_state.mode == "Administrateur":
    st.title("🛠️ Vue Administrateur - Configuration IT")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Applications", "Éléments d'Infrastructure", "Socles Mosaic",
        "Adhérences App ↔ App", "Adhérences App ↔ Socle", "Environnements IT par Entité"
    ])

    with tab1:
        st.subheader("📦 Définir les Applications")
        st.session_state.applications = st.data_editor(
            st.session_state.applications, num_rows="dynamic", use_container_width=True
        )

    with tab2:
        st.subheader("🧱 Définir les Éléments d'Infrastructure")
        st.session_state.infra_elements = st.data_editor(
            st.session_state.infra_elements, num_rows="dynamic", use_container_width=True
        )

    with tab3:
        st.subheader("🧩 Définir les Socles Mosaic")
        for socle in st.session_state.mosaic_socles.keys():
            selected_elements = st.multiselect(
                f"{socle} - Sélectionner les éléments d'infrastructure",
                st.session_state.infra_elements["Nom"].tolist(),
                default=st.session_state.mosaic_socles[socle]
            )
            st.session_state.mosaic_socles[socle] = selected_elements

    with tab4:
        st.subheader("🔗 Adhérences entre Applications")
        st.session_state.adh_app_app = st.data_editor(
            st.session_state.adh_app_app, num_rows="dynamic", use_container_width=True
        )

    with tab5:
        st.subheader("🔗 Adhérences entre Applications et Socles Mosaic")
        st.session_state.adh_app_socle = st.data_editor(
            st.session_state.adh_app_socle, num_rows="dynamic", use_container_width=True
        )

    with tab6:
        st.subheader("🏢 Définir les Environnements IT par Entité Juridique")
        entite = st.text_input("Nom de l'entité juridique")
        selected_apps = st.multiselect("Applications", st.session_state.applications["Nom"].tolist())
        selected_socle = st.selectbox("Socle Mosaic", list(st.session_state.mosaic_socles.keys()))
        if st.button("Ajouter l'environnement IT"):
            new_env = {
                "Entité Juridique": entite,
                "Applications": selected_apps,
                "Socle Mosaic": selected_socle
            }
            st.session_state.environnements = pd.concat([
                st.session_state.environnements,
                pd.DataFrame([new_env])
            ], ignore_index=True)
        st.dataframe(st.session_state.environnements, use_container_width=True)

# --- UTILISATEUR MODE ---
elif st.session_state.mode == "Utilisateur":
    st.title("👤 Vue Utilisateur - Simulation M&A")

    st.subheader("🏢 Sélectionner une Entité Juridique")
    entite_selected = st.selectbox("Entité", st.session_state.environnements["Entité Juridique"].unique())

    env_data = st.session_state.environnements[
        st.session_state.environnements["Entité Juridique"] == entite_selected
    ].iloc[0]

    selected_apps = env_data["Applications"]
    selected_socle = env_data["Socle Mosaic"]
    infra_elements = st.session_state.mosaic_socles[selected_socle]

    st.markdown(f"**Applications sélectionnées :** {', '.join(selected_apps)}")
    st.markdown(f"**Socle Mosaic :** {selected_socle}")
    st.markdown(f"**Éléments d'infrastructure :** {', '.join(infra_elements)}")

    # Simulation des coûts
    st.subheader("📈 Simulation des coûts par phase M&A")
    phases = ["Préparation au Closing", "Transition (TSA)", "Post-TSA"]
    phase_durations = {
        "Préparation au Closing": 3,
        "Transition (TSA)": 6,
        "Post-TSA": 12
    }

    simulation = []

    # Coûts des applications
    for app in selected_apps:
        app_row = st.session_state.applications[st.session_state.applications["Nom"] == app].iloc[0]
        for phase in phases:
            simulation.append({
                "Élément": app,
                "Type": "Application",
                "Phase": phase,
                "Durée (mois)": phase_durations[phase],
                "CAPEX (€)": app_row["CAPEX (€)"] if phase == "Préparation au Closing" else 0,
                "OPEX (€)": app_row["OPEX (€ / an)"] * (phase_durations[phase] / 12)
            })

    # Coûts des éléments d'infrastructure
    for infra in infra_elements:
        infra_row = st.session_state.infra_elements[st.session_state.infra_elements["Nom"] == infra].iloc[0]
        for phase in phases:
            simulation.append({
                "Élément": infra,
                "Type": "Infrastructure",
                "Phase": phase,
                "Durée (mois)": phase_durations[phase],
                "CAPEX (€)": infra_row["CAPEX (€)"] if phase == "Préparation au Closing" else 0,
                "OPEX (€)": infra_row["OPEX (€ / an)"] * (phase_durations[phase] / 12)
            })

    sim_df = pd.DataFrame(simulation)
    st.dataframe(sim_df, use_container_width=True)
