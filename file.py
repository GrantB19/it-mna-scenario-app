import streamlit as st
import pandas as pd
import json
from copy import deepcopy

# ─────────────────────────────────────────────
# CONFIG & INIT
# ─────────────────────────────────────────────
st.set_page_config(page_title="Due Diligence IT – Groupe Avril", layout="wide")

DOMAINS = ["ASA", "AGC", "APTER", "AD", "AIS"]
MOSAIC_LEVELS = ["Mosaic Entry", "Mosaic Advanced", "Mosaic Complete"]
MOSAIC_RANK   = {"Mosaic Entry": 1, "Mosaic Advanced": 2, "Mosaic Complete": 3}

def init_state():
    defaults = {
        "applications": [],        # [{name, opex, capex, adherences_apps:[], adherences_mosaic:[]}]
        "infrastructures": [],     # [{name, opex, capex}]
        "mosaic_socles": {         # {socle_name: [infra_name, ...]}
            "Mosaic Entry": [],
            "Mosaic Advanced": [],
            "Mosaic Complete": []
        },
        "entities_existing": [],   # [{name, domain, applications:[], mosaic_socle}]
        "entities_target": [],     # [{name, domain, applications:[], recommended_mosaic}]
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def recommend_mosaic(app_names: list[str]) -> str:
    """Retourne le socle Mosaic conseillé en fonction des adhérences des applications sélectionnées."""
    required_rank = 0
    for app_name in app_names:
        app = next((a for a in st.session_state.applications if a["name"] == app_name), None)
        if app:
            for mosaic in app.get("adherences_mosaic", []):
                r = MOSAIC_RANK.get(mosaic, 0)
                if r > required_rank:
                    required_rank = r
    if required_rank == 0:
        return "Aucun socle requis"
    return {1: "Mosaic Entry", 2: "Mosaic Advanced", 3: "Mosaic Complete"}[required_rank]

def get_linked_apps(selected_apps: list[str]) -> list[str]:
    """Retourne toutes les apps liées par adhérence à la sélection."""
    result = set(selected_apps)
    for app_name in selected_apps:
        app = next((a for a in st.session_state.applications if a["name"] == app_name), None)
        if app:
            for linked in app.get("adherences_apps", []):
                result.add(linked)
    return list(result)

def clean_excel(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie un DataFrame importé depuis Excel."""
    df = df.dropna(how="all")
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    df = df.fillna("")
    return df

# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
st.sidebar.title("Navigation")
view = st.sidebar.radio(
    "Vue",
    ["🗄️ Base de données", "🏢 Environnements existants", "🎯 Extrapolation cible"],
    label_visibility="collapsed"
)

# ═══════════════════════════════════════════════════════════════
# VUE 1 – BASE DE DONNÉES
# ═══════════════════════════════════════════════════════════════
if view == "🗄️ Base de données":
    st.title("🗄️ Base de données – Référentiel IT")

    tab1, tab2, tab3 = st.tabs(["📦 Applications", "🖥️ Infrastructures & Mosaic", "🔗 Adhérences"])

    # ── TAB 1 : Applications ──────────────────────────────────
    with tab1:
        st.subheader("Gestion des applications")

        # Import Excel
        with st.expander("📥 Importer un fichier Excel d'applications"):
            uploaded = st.file_uploader("Déposer un fichier Excel (.xlsx)", type=["xlsx"], key="upload_apps")
            if uploaded:
                try:
                    df_raw = pd.read_excel(uploaded)
                    df = clean_excel(df_raw)
                    st.write("**Aperçu nettoyé :**", df.head())

                    col_name = st.selectbox("Colonne → Nom application", df.columns, key="col_app_name")
                    col_opex = st.selectbox("Colonne → OPEX", ["(aucune)"] + list(df.columns), key="col_app_opex")
                    col_capex = st.selectbox("Colonne → CAPEX", ["(aucune)"] + list(df.columns), key="col_app_capex")

                    if st.button("✅ Importer les applications"):
                        existing_names = {a["name"] for a in st.session_state.applications}
                        added = 0
                        for _, row in df.iterrows():
                            name = str(row[col_name]).strip()
                            if name and name not in existing_names:
                                st.session_state.applications.append({
                                    "name": name,
                                    "opex": float(row[col_opex]) if col_opex != "(aucune)" and row[col_opex] != "" else 0.0,
                                    "capex": float(row[col_capex]) if col_capex != "(aucune)" and row[col_capex] != "" else 0.0,
                                    "adherences_apps": [],
                                    "adherences_mosaic": []
                                })
                                existing_names.add(name)
                                added += 1
                        st.success(f"{added} application(s) importée(s).")
                except Exception as e:
                    st.error(f"Erreur lecture Excel : {e}")

        # Ajout manuel
        with st.expander("➕ Ajouter une application manuellement"):
            with st.form("form_add_app", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                new_app_name  = c1.text_input("Nom de l'application")
                new_app_opex  = c2.number_input("OPEX (k€/an)", min_value=0.0, step=0.5)
                new_app_capex = c3.number_input("CAPEX (k€)", min_value=0.0, step=0.5)
                submitted = st.form_submit_button("Ajouter")
                if submitted:
                    if not new_app_name.strip():
                        st.warning("Le nom est obligatoire.")
                    elif any(a["name"] == new_app_name.strip() for a in st.session_state.applications):
                        st.warning("Cette application existe déjà.")
                    else:
                        st.session_state.applications.append({
                            "name": new_app_name.strip(),
                            "opex": new_app_opex,
                            "capex": new_app_capex,
                            "adherences_apps": [],
                            "adherences_mosaic": []
                        })
                        st.success(f"✅ Application « {new_app_name.strip()} » ajoutée.")

        # Liste des applications
        if st.session_state.applications:
            st.markdown("### Liste des applications")
            for i, app in enumerate(st.session_state.applications):
                with st.expander(f"**{app['name']}** — OPEX: {app['opex']} k€ | CAPEX: {app['capex']} k€"):
                    ec1, ec2, ec3 = st.columns(3)
                    new_name  = ec1.text_input("Nom", value=app["name"], key=f"app_name_{i}")
                    new_opex  = ec2.number_input("OPEX", value=app["opex"], key=f"app_opex_{i}", min_value=0.0, step=0.5)
                    new_capex = ec3.number_input("CAPEX", value=app["capex"], key=f"app_capex_{i}", min_value=0.0, step=0.5)
                    if st.button("💾 Sauvegarder", key=f"save_app_{i}"):
                        st.session_state.applications[i]["name"]  = new_name.strip()
                        st.session_state.applications[i]["opex"]  = new_opex
                        st.session_state.applications[i]["capex"] = new_capex
                        st.success("Modifications sauvegardées.")
                    if st.button("🗑️ Supprimer", key=f"del_app_{i}"):
                        st.session_state.applications.pop(i)
                        st.rerun()
        else:
            st.info("Aucune application enregistrée.")

    # ── TAB 2 : Infrastructures & Mosaic ─────────────────────
    with tab2:
        st.subheader("Éléments d'infrastructure")

        with st.expander("➕ Ajouter une infrastructure"):
            with st.form("form_add_infra", clear_on_submit=True):
                ci1, ci2, ci3 = st.columns(3)
                new_infra_name  = ci1.text_input("Nom de l'infrastructure")
                new_infra_opex  = ci2.number_input("OPEX (k€/an)", min_value=0.0, step=0.5, key="infra_opex")
                new_infra_capex = ci3.number_input("CAPEX (k€)", min_value=0.0, step=0.5, key="infra_capex")
                sub_infra = st.form_submit_button("Ajouter")
                if sub_infra:
                    if not new_infra_name.strip():
                        st.warning("Nom obligatoire.")
                    elif any(inf["name"] == new_infra_name.strip() for inf in st.session_state.infrastructures):
                        st.warning("Infrastructure déjà existante.")
                    else:
                        st.session_state.infrastructures.append({
                            "name": new_infra_name.strip(),
                            "opex": new_infra_opex,
                            "capex": new_infra_capex
                        })
                        st.success(f"✅ Infrastructure « {new_infra_name.strip()} » ajoutée.")

        if st.session_state.infrastructures:
            st.markdown("### Liste des infrastructures")
            for i, inf in enumerate(st.session_state.infrastructures):
                with st.expander(f"**{inf['name']}** — OPEX: {inf['opex']} k€ | CAPEX: {inf['capex']} k€"):
                    ei1, ei2, ei3 = st.columns(3)
                    n = ei1.text_input("Nom", value=inf["name"], key=f"inf_name_{i}")
                    o = ei2.number_input("OPEX", value=inf["opex"], key=f"inf_opex_{i}", min_value=0.0, step=0.5)
                    c = ei3.number_input("CAPEX", value=inf["capex"], key=f"inf_capex_{i}", min_value=0.0, step=0.5)
                    if st.button("💾 Sauvegarder", key=f"save_inf_{i}"):
                        st.session_state.infrastructures[i].update({"name": n.strip(), "opex": o, "capex": c})
                        st.success("Sauvegardé.")
                    if st.button("🗑️ Supprimer", key=f"del_inf_{i}"):
                        st.session_state.infrastructures.pop(i)
                        st.rerun()
        else:
            st.info("Aucune infrastructure enregistrée.")

        st.divider()
        st.subheader("🧱 Composition des socles Mosaic")
        infra_names = [inf["name"] for inf in st.session_state.infrastructures]

        if infra_names:
            for socle in MOSAIC_LEVELS:
                current = st.session_state.mosaic_socles.get(socle, [])
                selected = st.multiselect(
                    f"**{socle}** — infrastructures incluses",
                    options=infra_names,
                    default=[x for x in current if x in infra_names],
                    key=f"mosaic_{socle}"
                )
                st.session_state.mosaic_socles[socle] = selected

                # Résumé coûts
                total_opex  = sum(inf["opex"]  for inf in st.session_state.infrastructures if inf["name"] in selected)
                total_capex = sum(inf["capex"] for inf in st.session_state.infrastructures if inf["name"] in selected)
                st.caption(f"OPEX total: **{total_opex} k€** | CAPEX total: **{total_capex} k€**")
        else:
            st.info("Ajoutez des infrastructures pour composer les socles Mosaic.")

    # ── TAB 3 : Adhérences ────────────────────────────────────
    with tab3:
        st.subheader("🔗 Adhérences entre applications")
        app_names = [a["name"] for a in st.session_state.applications]

        if len(app_names) >= 2:
            for i, app in enumerate(st.session_state.applications):
                others = [n for n in app_names if n != app["name"]]
                current_app_adh = [x for x in app.get("adherences_apps", []) if x in others]
                selected_adh = st.multiselect(
                    f"**{app['name']}** → adhère à",
                    options=others,
                    default=current_app_adh,
                    key=f"adh_app_{i}"
                )
                st.session_state.applications[i]["adherences_apps"] = selected_adh

            st.divider()
            st.subheader("🔗 Adhérences applications → socles Mosaic")
            for i, app in enumerate(st.session_state.applications):
                current_mosaic_adh = [x for x in app.get("adherences_mosaic", []) if x in MOSAIC_LEVELS]
                selected_mosaic = st.multiselect(
                    f"**{app['name']}** → socle(s) requis",
                    options=MOSAIC_LEVELS,
                    default=current_mosaic_adh,
                    key=f"adh_mosaic_{i}"
                )
                st.session_state.applications[i]["adherences_mosaic"] = selected_mosaic
        else:
            st.info("Ajoutez au moins 2 applications pour définir des adhérences.")


# ═══════════════════════════════════════════════════════════════
# VUE 2 – ENVIRONNEMENTS EXISTANTS
# ═══════════════════════════════════════════════════════════════
elif view == "🏢 Environnements existants":
    st.title("🏢 Environnements entités existantes – Groupe Avril")

    app_names   = [a["name"] for a in st.session_state.applications]
    mosaic_opts = MOSAIC_LEVELS + ["Aucun"]

    # Créer une nouvelle entité
    with st.expander("➕ Créer une entité existante"):
        with st.form("form_entity_existing", clear_on_submit=True):
            ec1, ec2 = st.columns(2)
            ent_name   = ec1.text_input("Nom de l'entité")
            ent_domain = ec2.selectbox("Domaine", DOMAINS)
            ent_apps   = st.multiselect("Applications rattachées", app_names)
            ent_mosaic = st.selectbox("Socle Mosaic", mosaic_opts)
            sub_ent = st.form_submit_button("Créer l'entité")
            if sub_ent:
                if not ent_name.strip():
                    st.warning("Nom obligatoire.")
                else:
                    # Expansion automatique par adhérences
                    expanded = get_linked_apps(ent_apps)
                    st.session_state.entities_existing.append({
                        "name": ent_name.strip(),
                        "domain": ent_domain,
                        "applications": expanded,
                        "mosaic_socle": ent_mosaic
                    })
                    if len(expanded) > len(ent_apps):
                        added_linked = [a for a in expanded if a not in ent_apps]
                        st.success(f"✅ Entité créée. Applications liées automatiquement ajoutées : {', '.join(added_linked)}")
                    else:
                        st.success(f"✅ Entité « {ent_name.strip()} » créée.")

    # Affichage et édition des entités existantes
    if st.session_state.entities_existing:
        st.markdown("---")
        # Filtre par domaine
        filter_domain = st.selectbox("Filtrer par domaine", ["Tous"] + DOMAINS, key="filter_exist")
        entities_shown = [
            e for e in st.session_state.entities_existing
            if filter_domain == "Tous" or e["domain"] == filter_domain
        ]

        for i, ent in enumerate(st.session_state.entities_existing):
            if filter_domain != "Tous" and ent["domain"] != filter_domain:
                continue

            real_i = st.session_state.entities_existing.index(ent)
            with st.expander(f"🏢 **{ent['name']}** | Domaine: {ent['domain']} | Socle: {ent['mosaic_socle']}"):
                col1, col2 = st.columns(2)
                new_ent_name   = col1.text_input("Nom", value=ent["name"], key=f"ent_name_{real_i}")
                new_ent_domain = col2.selectbox("Domaine", DOMAINS, index=DOMAINS.index(ent["domain"]), key=f"ent_domain_{real_i}")

                new_ent_apps = st.multiselect(
                    "Applications",
                    options=app_names,
                    default=[a for a in ent["applications"] if a in app_names],
                    key=f"ent_apps_{real_i}"
                )
                # Auto-expand adhérences
                expanded_apps = get_linked_apps(new_ent_apps)
                if len(expanded_apps) > len(new_ent_apps):
                    st.info(f"ℹ️ Applications liées automatiquement incluses : {', '.join([a for a in expanded_apps if a not in new_ent_apps])}")

                new_ent_mosaic = st.selectbox(
                    "Socle Mosaic",
                    mosaic_opts,
                    index=mosaic_opts.index(ent["mosaic_socle"]) if ent["mosaic_socle"] in mosaic_opts else 0,
                    key=f"ent_mosaic_{real_i}"
                )

                # Résumé coûts
                total_opex  = sum(a["opex"]  for a in st.session_state.applications if a["name"] in expanded_apps)
                total_capex = sum(a["capex"] for a in st.session_state.applications if a["name"] in expanded_apps)
                st.caption(f"💰 OPEX applications: **{total_opex} k€** | CAPEX: **{total_capex} k€**")

                bc1, bc2 = st.columns(2)
                if bc1.button("💾 Sauvegarder", key=f"save_ent_{real_i}"):
                    st.session_state.entities_existing[real_i] = {
                        "name": new_ent_name.strip(),
                        "domain": new_ent_domain,
                        "applications": expanded_apps,
                        "mosaic_socle": new_ent_mosaic
                    }
                    st.success("Sauvegardé.")
                    st.rerun()
                if bc2.button("🗑️ Supprimer", key=f"del_ent_{real_i}"):
                    st.session_state.entities_existing.pop(real_i)
                    st.rerun()
    else:
        st.info("Aucune entité existante créée.")


# ═══════════════════════════════════════════════════════════════
# VUE 3 – EXTRAPOLATION ENVIRONNEMENT CIBLE
# ═══════════════════════════════════════════════════════════════
elif view == "🎯 Extrapolation cible":
    st.title("🎯 Extrapolation – Environnement Cible")

    app_names = [a["name"] for a in st.session_state.applications]

    # Créer une entité cible
    with st.expander("➕ Créer une entité cible"):
        with st.form("form_entity_target", clear_on_submit=True):
            tc1, tc2 = st.columns(2)
            tgt_name   = tc1.text_input("Nom de l'entité cible")
            tgt_domain = tc2.selectbox("Domaine", DOMAINS, key="tgt_domain")
            tgt_apps   = st.multiselect("Applications rattachées", app_names, key="tgt_apps")
            sub_tgt = st.form_submit_button("Créer l'entité cible")
            if sub_tgt:
                if not tgt_name.strip():
                    st.warning("Nom obligatoire.")
                else:
                    expanded = get_linked_apps(tgt_apps)
                    recommended = recommend_mosaic(expanded)
                    st.session_state.entities_target.append({
                        "name": tgt_name.strip(),
                        "domain": tgt_domain,
                        "applications": expanded,
                        "recommended_mosaic": recommended
                    })
                    msg = f"✅ Entité « {tgt_name.strip()} » créée. Socle conseillé : **{recommended}**"
                    if len(expanded) > len(tgt_apps):
                        msg += f"\n\nApplications liées ajoutées : {', '.join([a for a in expanded if a not in tgt_apps])}"
                    st.success(msg)

    # Affichage entités cibles
    if st.session_state.entities_target:
        st.markdown("---")
        filter_tgt = st.selectbox("Filtrer par domaine", ["Tous"] + DOMAINS, key="filter_target")

        for i, ent in enumerate(st.session_state.entities_target):
            if filter_tgt != "Tous" and ent["domain"] != filter_tgt:
                continue

            real_i = st.session_state.entities_target.index(ent)
            recommended = ent.get("recommended_mosaic", "—")
            badge_color = {"Mosaic Entry": "🟢", "Mosaic Advanced": "🟠", "Mosaic Complete": "🔴"}.get(recommended, "⚪")

            with st.expander(f"🎯 **{ent['name']}** | {ent['domain']} | {badge_color} Conseillé: {recommended}"):
                cc1, cc2 = st.columns(2)
                new_tgt_name   = cc1.text_input("Nom", value=ent["name"], key=f"tgt_name_{real_i}")
                new_tgt_domain = cc2.selectbox("Domaine", DOMAINS, index=DOMAINS.index(ent["domain"]), key=f"tgt_domain_{real_i}")

                new_tgt_apps = st.multiselect(
                    "Applications",
                    options=app_names,
                    default=[a for a in ent["applications"] if a in app_names],
                    key=f"tgt_apps_{real_i}"
                )
                expanded_apps  = get_linked_apps(new_tgt_apps)
                new_recommended = recommend_mosaic(expanded_apps)

                if len(expanded_apps) > len(new_tgt_apps):
                    st.info(f"ℹ️ Liées automatiquement : {', '.join([a for a in expanded_apps if a not in new_tgt_apps])}")

                # Affichage recommandation avec logique hiérarchique
                st.markdown("#### 📊 Analyse Mosaic")
                mosaic_details = {}
                for app_name in expanded_apps:
                    app = next((a for a in st.session_state.applications if a["name"] == app_name), None)
                    if app and app.get("adherences_mosaic"):
                        mosaic_details[app_name] = app["adherences_mosaic"]

                if mosaic_details:
                    detail_rows = [{"Application": k, "Socles requis": ", ".join(v)} for k, v in mosaic_details.items()]
                    st.dataframe(pd.DataFrame(detail_rows), use_container_width=True, hide_index=True)

                badge = {"Mosaic Entry": "🟢", "Mosaic Advanced": "🟠", "Mosaic Complete": "🔴"}.get(new_recommended, "⚪")
                st.metric("Socle Mosaic conseillé", f"{badge} {new_recommended}")

                # Résumé financier
                total_opex  = sum(a["opex"]  for a in st.session_state.applications if a["name"] in expanded_apps)
                total_capex = sum(a["capex"] for a in st.session_state.applications if a["name"] in expanded_apps)
                mosaic_infras = st.session_state.mosaic_socles.get(new_recommended, [])
                mosaic_opex   = sum(inf["opex"]  for inf in st.session_state.infrastructures if inf["name"] in mosaic_infras)
                mosaic_capex  = sum(inf["capex"] for inf in st.session_state.infrastructures if inf["name"] in mosaic_infras)

                st.markdown("#### 💰 Estimation des coûts")
                cost_df = pd.DataFrame([
                    {"Poste": "Applications (OPEX)", "Montant (k€)": total_opex},
                    {"Poste": "Applications (CAPEX)", "Montant (k€)": total_capex},
                    {"Poste": f"Socle {new_recommended} (OPEX)", "Montant (k€)": mosaic_opex},
                    {"Poste": f"Socle {new_recommended} (CAPEX)", "Montant (k€)": mosaic_capex},
                    {"Poste": "TOTAL OPEX", "Montant (k€)": total_opex + mosaic_opex},
                    {"Poste": "TOTAL CAPEX", "Montant (k€)": total_capex + mosaic_capex},
                ])
                st.dataframe(cost_df, use_container_width=True, hide_index=True)

                bc1, bc2 = st.columns(2)
                if bc1.button("💾 Sauvegarder", key=f"save_tgt_{real_i}"):
                    st.session_state.entities_target[real_i] = {
                        "name": new_tgt_name.strip(),
                        "domain": new_tgt_domain,
                        "applications": expanded_apps,
                        "recommended_mosaic": new_recommended
                    }
                    st.success("Sauvegardé.")
                    st.rerun()
                if bc2.button("🗑️ Supprimer", key=f"del_tgt_{real_i}"):
                    st.session_state.entities_target.pop(real_i)
                    st.rerun()
    else:
        st.info("Aucune entité cible créée.")
