
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title of the app
st.title("Modélisation de scénarios IT pour M&A")

# Sidebar for entity selection
entity = st.sidebar.selectbox("Sélectionnez l'entité", ["Avril", "Autre"])
years = st.sidebar.slider("Durée de projection (années)", min_value=1, max_value=10, value=5)

# Environment selection or creation
st.subheader("1. Environnement IT")
env_option = st.radio("Souhaitez-vous :", ["Sélectionner un environnement existant", "Créer un nouvel environnement"])

if env_option == "Sélectionner un environnement existant":
    selected_env = st.selectbox("Choisissez un environnement", ["Environnement A", "Environnement B"])
else:
    new_env_name = st.text_input("Nom du nouvel environnement")
    st.write("Ajoutez les applications à cet environnement :")
    applications = st.text_area("Liste des applications (séparées par des virgules)", "ERP, CRM, BI")

# Cost inputs
st.subheader("2. Hypothèses de coûts")
transition_cost = st.number_input("Coût de transition initial (€)", min_value=0, value=500000)
opex = st.number_input("OPEX annuel (€)", min_value=0, value=300000)
capex = st.number_input("CAPEX annuel (€)", min_value=0, value=200000)
synergies = st.number_input("Synergies annuelles (€)", min_value=0, value=100000)

# Projection calculation
st.subheader("3. Projection des coûts")
years_range = list(range(1, years + 1))
total_costs = []

for year in years_range:
    if year == 1:
        cost = transition_cost + opex + capex - synergies
    else:
        cost = opex + capex - synergies
    total_costs.append(cost)

projection_df = pd.DataFrame({
    "Année": years_range,
    "Coût projeté (€)": total_costs
})

# Display table
st.dataframe(projection_df)

# Plotting
st.subheader("4. Visualisation")
fig, ax = plt.subplots()
ax.plot(projection_df["Année"], projection_df["Coût projeté (€)"], marker='o')
ax.set_title("Projection des coûts IT")
ax.set_xlabel("Année")
ax.set_ylabel("Coût (€)")
st.pyplot(fig)

# Export to Excel
st.subheader("5. Export Excel")
def convert_df_to_excel(df):
    return df.to_excel("projection_mna.xlsx", index=False)

if st.button("Exporter en Excel"):
    convert_df_to_excel(projection_df)
    st.success("Fichier Excel généré : projection_mna.xlsx")
