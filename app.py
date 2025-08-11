import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Base d'environnements IT pré-remplie
base_environnements = {
    "Avril Agro": {
        "applications": ["ERP", "CRM", "BI"],
        "infrastructure": ["Serveurs locaux", "VPN", "Stockage NAS"]
    },
    "Avril Nutrition": {
        "applications": ["SIRH", "WMS", "MES"],
        "infrastructure": ["Cloud privé", "Firewall", "Backup"]
    },
    "Avril Ingrédients": {
        "applications": ["PLM", "SCM", "Portail client"],
        "infrastructure": ["Cloud public", "Monitoring", "Load balancer"]
    }
}

# Coûts estimés par application
couts_applications = {
    "ERP": {"transition": 100000, "opex": 50000, "capex": 30000},
    "CRM": {"transition": 80000, "opex": 40000, "capex": 20000},
    "BI": {"transition": 60000, "opex": 30000, "capex": 15000},
    "SIRH": {"transition": 50000, "opex": 25000, "capex": 10000},
    "WMS": {"transition": 70000, "opex": 35000, "capex": 18000},
    "MES": {"transition": 90000, "opex": 45000, "capex": 22000},
    "PLM": {"transition": 75000, "opex": 38000, "capex": 17000},
    "SCM": {"transition": 85000, "opex": 42000, "capex": 19000},
    "Portail client": {"transition": 40000, "opex": 20000, "capex": 10000}
}

# Coûts estimés par infrastructure
couts_infrastructure = {
    "Serveurs locaux": {"transition": 30000, "opex": 15000, "capex": 10000},
    "VPN": {"transition": 20000, "opex": 10000, "capex": 5000},
    "Stockage NAS": {"transition": 25000, "opex": 12000, "capex": 8000},
    "Cloud privé": {"transition": 40000, "opex": 20000, "capex": 15000},
    "Firewall": {"transition": 15000, "opex": 8000, "capex": 5000},
    "Backup": {"transition": 10000, "opex": 5000, "capex": 3000},
    "Cloud public": {"transition": 35000, "opex": 18000, "capex": 12000},
    "Monitoring": {"transition": 12000, "opex": 6000, "capex": 4000},
    "Load balancer": {"transition": 18000, "opex": 9000, "capex": 6000}
}

# Adhérences selon Mosaic
mosaic_adhérences = {
    "Mosaic Entry": 1.0,
    "Mosaic Advanced": 0.9,
    "Mosaic Complete": 0.8
}

st.title("Modélisation de scénarios IT pour M&A")

nb_scenarios = st.sidebar.slider("Nombre de scénarios à comparer", 1, 3, 1)
scenarios = []

for i in range(nb_scenarios):
    st.header(f"Scénario {i+1}")
    entite = st.selectbox(f"Entité pour scénario {i+1}", list(base_environnements.keys()) + ["Personnalisé"], key=f"entite_{i}")
    if entite != "Personnalisé":
        apps = base_environnements[entite]["applications"]
        infra = base_environnements[entite]["infrastructure"]
    else:
        apps = st.multiselect(f"Applications métier scénario {i+1}", list(couts_applications.keys()), key=f"apps_{i}")
        infra = st.multiselect(f"Infrastructure IT scénario {i+1}", list(couts_infrastructure.keys()), key=f"infra_{i}")

    mosaic = st.selectbox(f"Socle d'intégration Mosaic scénario {i+1}", list(mosaic_adhérences.keys()), key=f"mosaic_{i}")
    years = st.slider(f"Durée de projection (années) scénario {i+1}", 1, 10, 5, key=f"years_{i}")

    # Calcul des coûts
    transition = sum(couts_applications[app]["transition"] for app in apps) + sum(couts_infrastructure[inf]["transition"] for inf in infra)
    opex = sum(couts_applications[app]["opex"] for app in apps) + sum(couts_infrastructure[inf]["opex"] for inf in infra)
    capex = sum(couts_applications[app]["capex"] for app in apps) + sum(couts_infrastructure[inf]["capex"] for inf in infra)

    # Adhérences
    facteur_adh = mosaic_adhérences[mosaic]
    transition *= facteur_adh
    opex *= facteur_adh
    capex *= facteur_adh

    # Projection
    projection = []
    for y in range(1, years+1):
        if y == 1:
            total = transition + opex + capex
        else:
            total = opex + capex
        projection.append(total)

    df = pd.DataFrame({
        "Année": list(range(1, years+1)),
        "Coût projeté (€)": projection
    })

    scenarios.append((f"Scénario {i+1}", df))

# Affichage des résultats
st.subheader("Comparaison des scénarios")
for name, df in scenarios:
    st.write(name)
    st.dataframe(df)

# Graphique comparatif
fig, ax = plt.subplots()
for name, df in scenarios:
    ax.plot(df["Année"], df["Coût projeté (€)"], marker='o', label=name)
ax.set_title("Projection des coûts IT")
ax.set_xlabel("Année")
ax.set_ylabel("Coût (€)")
ax.legend()
st.pyplot(fig)

# Export Excel
st.subheader("Export Excel")
def export_excel(scenarios):
    with pd.ExcelWriter("projection_scenarios.xlsx") as writer:
        for name, df in scenarios:
            df.to_excel(writer, sheet_name=name, index=False)

if st.button("Exporter les scénarios en Excel"):
    export_excel(scenarios)
    st.success("Fichier Excel généré : projection_scenarios.xlsx")
