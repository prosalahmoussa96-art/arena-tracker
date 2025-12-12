import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Arena Tracker HS", page_icon="🃏")

# --- TITRE ---
st.title("🃏 Hearthstone Arena Tracker")

# --- INITIALISATION DES DONNÉES (SESSION) ---
# Pour l'instant, les données vivent le temps que tu restes sur la page
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['Classe', 'Victoires', 'Défaites', 'Cout', 'Recompense_Or', 'Recompense_Poussiere'])

# --- SIDEBAR : FORMULAIRE D'ENTRÉE ---
st.sidebar.header("Nouvelle Run")
with st.sidebar.form("run_form"):
    classe = st.selectbox("Classe", ["Mage", "Paladin", "Démoniste", "Chasseur", "Guerrier", "Druide", "Voleur", "Chaman", "Prêtre", "Chasseur de Démons", "Chevalier de la Mort"])
    victoires = st.slider("Victoires", 0, 12, 3)
    defaites = st.slider("Défaites", 0, 3, 3)
    cout = st.number_input("Coût d'entrée (Or)", value=150)
    rec_or = st.number_input("Récompense : Or", value=0)
    rec_pouss = st.number_input("Récompense : Poussière", value=0)
    
    submit = st.form_submit_button("Ajouter la Run")

    if submit:
        new_row = pd.DataFrame({
            'Classe': [classe],
            'Victoires': [victoires],
            'Défaites': [defaites],
            'Cout': [cout],
            'Recompense_Or': [rec_or],
            'Recompense_Poussiere': [rec_pouss]
        })
        st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
        st.success("Run ajoutée !")

# --- ANALYSE & STATS ---
df = st.session_state.data

if not df.empty:
    # Calculs de rentabilité
    df['Profit_Or'] = df['Recompense_Or'] - df['Cout']
    total_profit = df['Profit_Or'].sum()
    total_runs = len(df)
    avg_wins = df['Victoires'].mean()

    # --- KPI (Indicateurs Clés) ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Runs Totales", total_runs)
    col2.metric("Moyenne Victoires", f"{avg_wins:.2f}")
    col3.metric("Balance Or", f"{total_profit} po", delta=int(total_profit))

    # --- SYSTÈME DE SÉCURITÉ (TILT CONTROL) ---
    st.markdown("---")
    st.subheader("🛡️ Zone de Contrôle")
    
    # Seuil de tolérance : Si tu perds plus de 300 golds sur tes 3 dernières runs
    if total_runs >= 3:
        last_3_runs = df.tail(3)
        perte_recente = last_3_runs['Profit_Or'].sum()
        
        if perte_recente < -300:
            st.error(f"🚨 ALERTE ROUGE : Tu as perdu {abs(perte_recente)} gold sur les 3 dernières runs !")
            st.warning("🛑 CONSEIL DU COACH : Arrête tout de suite. Tu es en tilt ou la méta est mauvaise. Reviens demain.")
        else:
            st.success("✅ Feu vert : Tu es dans une zone de gestion saine.")
    else:
        st.info("Joue au moins 3 runs pour activer le système de sécurité.")

    # --- GRAPHIQUES ---
    st.markdown("---")
    st.subheader("📊 Performance")
    
    # Graphique 1 : Évolution de l'Or
    df['Run_Index'] = range(1, len(df) + 1)
    df['Cumul_Or'] = df['Profit_Or'].cumsum()
    
    fig_line = px.line(df, x='Run_Index', y='Cumul_Or', title="Évolution de ta banque (Or)", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

    # Graphique 2 : Moyenne par classe
    # (Simple table pour l'instant)
    st.write("Détail des runs :")
    st.dataframe(df)

else:
    st.info("👈 Rentre ta première run dans le menu à gauche pour voir les stats !")
