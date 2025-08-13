import streamlit as st

# Initialisation des données
if "applications" not in st.session_state:
    st.session_state.applications = {}
if "infrastructures" not in st.session_state:
    st.session_state.infrastructures = {}
if "mosaic" not in st.session_state:
    st.session_state.mosaic = {"Entry": [], "Advanced": [], "Complete": []}
if "app_mosaic_links" not in st.session_state:
    st.session_state.app_mosaic_links = {}
if "app_app_links" not in st.session_state:
    st.session_state.app_app_links = {}
if "domains" not in st.session_state:
    st.session_state.domains = {"ASA": [], "AGC": [], "APTER": [], "AD": [], "AIS": []}
if "entities" not in st.session_state:
    st.session_state.entities = {}

st.title("🧠 Due Diligence IT - Groupe Avril")

# Vue 1 : Base de données
st.header("1️⃣ Base de données")

with st.expander("📦 Ajouter une application"):
    app_name = st.text_input("Nom de l'application")
    app_opex = st.number_input("Coût Opex", min_value=0.0)
    app_capex = st.number_input("Coût Capex", min_value=0.0)
    if st.button("Ajouter l'application"):
        st.session_state.applications[app_name] = {"Opex": app_opex, "Capex": app_capex}

with st.expander("🖥️ Ajouter un élément d'infrastructure"):
    infra_name = st.text_input("Nom de l'infrastructure")
    infra_opex = st.number_input("Coût Opex infra", min_value=0.0)
    infra_capex = st.number_input("Coût Capex infra", min_value=0.0)
    if st.button("Ajouter l'infrastructure"):
        st.session_state.infrastructures[infra_name] = {"Opex": infra_opex, "Capex": infra_capex}

with st.expander("🧩 Composer les socles Mosaic"):
    mosaic_type = st.selectbox("Type de socle", ["Entry", "Advanced", "Complete"])
    infra_choice = st.selectbox("Ajouter une infrastructure au socle", list(st.session_state.infrastructures.keys()))
    if st.button("Ajouter au socle Mosaic"):
        st.session_state.mosaic[mosaic_type].append(infra_choice)

with st.expander("🔗 Définir les adhérences entre applications et socles Mosaic"):
    app_select = st.selectbox("Application", list(st.session_state.applications.keys()), key="app_mosaic")
    mosaic_select = st.selectbox("Socle Mosaic", ["Entry", "Advanced", "Complete"])
    if st.button("Définir l'adhérence app-socle"):
        st.session_state.app_mosaic_links.setdefault(app_select, []).append(mosaic_select)

with st.expander("🔗 Définir les adhérences entre applications"):
    app_source = st.selectbox("Application source", list(st.session_state.applications.keys()), key="app_source")
    app_target = st.selectbox("Application cible", list(st.session_state.applications.keys()), key="app_target")
    if st.button("Définir l'adhérence app-app"):
        st.session_state.app_app_links.setdefault(app_source, []).append(app_target)

# Vue 2 : Création des environnements
st.header("2️⃣ Création des environnements")

with st.expander("🏢 Créer une entité du Groupe Avril"):
    entity_name = st.text_input("Nom de l'entité")
    domain_select = st.selectbox("Domaine", list(st.session_state.domains.keys()))
    if st.button("Créer l'entité"):
        st.session_state.entities[entity_name] = {"Domaine": domain_select, "Applications": [], "Mosaic": None}
        st.session_state.domains[domain_select].append(entity_name)

with st.expander("🔧 Rattacher des éléments à une entité"):
    entity_select = st.selectbox("Entité", list(st.session_state.entities.keys()))
    apps_to_add = st.multiselect("Applications à rattacher", list(st.session_state.applications.keys()))
    mosaic_to_add = st.selectbox("Socle Mosaic à rattacher", ["Entry", "Advanced", "Complete"])
    if st.button("Rattacher les éléments"):
        st.session_state.entities[entity_select]["Applications"] = apps_to_add
        st.session_state.entities[entity_select]["Mosaic"] = mosaic_to_add

# Visualisation
st.header("📊 Visualisation des environnements")

for entity, data in st.session_state.entities.items():
    st.subheader(f"Entité : {entity}")
    st.write(f"Domaine : {data['Domaine']}")
    st.write(f"Applications : {', '.join(data['Applications'])}")
    st.write(f"Socle Mosaic : {data['Mosaic']}")
