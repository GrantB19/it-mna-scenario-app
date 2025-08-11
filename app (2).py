
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="M&A IT Scenario Tool", layout="wide")

# --- Data Models ---
default_entities = {
    "Avril Agro": {
        "applications": ["ERP", "CRM", "BI"],
        "infrastructure": ["Serveurs locaux", "VPN", "Stockage NAS"]
    },
    "Avril Nutrition": {
        "applications": ["SIRH", "WMS", "Portail client"],
        "infrastructure": ["Cloud privé", "Firewall", "Backup"]
    },
    "Avril Ingrédients": {
        "applications": ["MES", "LIMS", "SCADA"],
        "infrastructure": ["Edge computing", "IoT Gateway", "Monitoring"]
    }
}

mosaic_profiles = {
    "Mosaic Entry": 1.0,
    "Mosaic Advanced": 1.2,
    "Mosaic Complete": 1.5
}

cost_per_app = 50000
cost_per_infra = 30000
adhérence_cost = 10000

# --- Sidebar Navigation ---
view = st.sidebar.radio("Vue", ["Paramétrage", "Visualisation", "Roadmap / Planning"])

# --- Scenario Storage ---
if "scenarios" not in st.session_state:
    st.session_state.scenarios = []

# --- Paramétrage View ---
if view == "Paramétrage":
    st.title("Paramétrage des scénarios IT")

    num_scenarios = st.number_input("Nombre de scénarios à comparer", min_value=1, max_value=3, value=1)

    st.session_state.scenarios = []

    for i in range(num_scenarios):
        st.subheader(f"Scénario {i+1}")
        entity = st.selectbox(f"Entité {i+1}", list(default_entities.keys()), key=f"entity_{i}")
        mosaic = st.selectbox(f"Socle Mosaic {i+1}", list(mosaic_profiles.keys()), key=f"mosaic_{i}")
        duration = st.slider(f"Durée de projection (années) {i+1}", 1, 10, 5, key=f"duration_{i}")

        apps = st.multiselect(f"Applications métier {i+1}", default_entities[entity]["applications"], default=default_entities[entity]["applications"], key=f"apps_{i}")
        infra = st.multiselect(f"Infrastructure IT {i+1}", default_entities[entity]["infrastructure"], default=default_entities[entity]["infrastructure"], key=f"infra_{i}")

        adhérences = st.slider(f"Nombre d’adhérences applicatives {i+1}", 0, 10, 2, key=f"adh_{i}")

        transition = st.number_input(f"Coût de transition initial (€) {i+1}", min_value=0, value=200000, key=f"trans_{i}")
        synergies = st.number_input(f"Synergies annuelles (€) {i+1}", min_value=0, value=50000, key=f"syn_{i}")

        opex = len(apps) * cost_per_app + len(infra) * cost_per_infra + adhérences * adhérence_cost
        capex = int(opex * 0.5)
        mosaic_factor = mosaic_profiles[mosaic]

        scenario = {
            "entity": entity,
            "mosaic": mosaic,
            "duration": duration,
            "apps": apps,
            "infra": infra,
            "adhérences": adhérences,
            "transition": transition,
            "synergies": synergies,
            "opex": int(opex * mosaic_factor),
            "capex": int(capex * mosaic_factor)
        }

        st.session_state.scenarios.append(scenario)

# --- Visualisation View ---
elif view == "Visualisation":
    st.title("Visualisation des projections de coûts")

    if not st.session_state.scenarios:
        st.warning("Veuillez d'abord paramétrer les scénarios.")
    else:
        df_all = pd.DataFrame()
        fig, ax = plt.subplots()

        for idx, sc in enumerate(st.session_state.scenarios):
            years = list(range(1, sc["duration"] + 1))
            costs = []
            for y in years:
                if y == 1:
                    cost = sc["transition"] + sc["opex"] + sc["capex"] - sc["synergies"]
                else:
                    cost = sc["opex"] + sc["capex"] - sc["synergies"]
                costs.append(cost)

            df = pd.DataFrame({
                "Année": years,
                f"Scénario {idx+1} ({sc['entity']})": costs
            })
            df_all = pd.concat([df_all, df], axis=1)
            ax.plot(years, costs, marker='o', label=f"Scénario {idx+1} ({sc['entity']})")

        st.dataframe(df_all)
        ax.set_title("Projection des coûts IT")
        ax.set_xlabel("Année")
        ax.set_ylabel("Coût (€)")
        ax.legend()
        st.pyplot(fig)

        # Export Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_all.to_excel(writer, index=False, sheet_name="Projections")
        st.download_button("📥 Télécharger les projections Excel", data=output.getvalue(), file_name="projections_mna.xlsx")

# --- Roadmap / Planning View ---
elif view == "Roadmap / Planning":
    st.title("Roadmap / Planning des phases IT")

    if "roadmap" not in st.session_state:
        st.session_state.roadmap = []

    with st.form("roadmap_form"):
        st.subheader("Ajouter une phase")
        phase_name = st.text_input("Nom de la phase")
        phase_desc = st.text_area("Description")
        phase_type = st.selectbox("Type de phase", ["Avant J0", "Post J0"])
        start_week = st.number_input("Semaine de démarrage", min_value=0, value=0)
        duration_week = st.number_input("Durée (semaines)", min_value=1, value=4)
        submitted = st.form_submit_button("Ajouter")

        if submitted and phase_name:
            st.session_state.roadmap.append({
                "Nom": phase_name,
                "Description": phase_desc,
                "Type": phase_type,
                "Début": start_week,
                "Durée": duration_week,
                "Fin": start_week + duration_week
            })

    if st.session_state.roadmap:
        df_roadmap = pd.DataFrame(st.session_state.roadmap)
        st.subheader("Tableau des phases")
        st.dataframe(df_roadmap)

        # Gantt chart
        fig, ax = plt.subplots(figsize=(10, 4))
        for idx, row in df_roadmap.iterrows():
            ax.barh(row["Nom"], row["Durée"], left=row["Début"], color="skyblue" if row["Type"] == "Avant J0" else "lightgreen")
        ax.set_xlabel("Semaines")
        ax.set_title("Diagramme de Gantt des phases IT")
        st.pyplot(fig)

        # Export Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_roadmap.to_excel(writer, index=False, sheet_name="Roadmap")
        st.download_button("📥 Télécharger la roadmap Excel", data=output.getvalue(), file_name="roadmap_mna.xlsx")
