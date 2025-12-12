import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Arena Master HS", page_icon="🔥", layout="wide")

# --- STYLE HEARTHSTONE (CSS INJECTION) ---
st.markdown("""
    <style>
    /* Fond sombre style HS */
    .stApp {
        background-color: #1a1510;
        color: #fcd144;
    }
    /* Titres dorés */
    h1, h2, h3 {
        color: #fcd144 !important;
        font-family: 'Georgia', serif;
        text-shadow: 2px 2px #000000;
    }
    /* Métriques */
    div[data-testid="stMetricValue"] {
        color: #fff !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #fcd144 !important;
    }
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #2b221a;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DONNÉES ET LOGO ---
CLASSES_LOGOS = {
    "Chevalier de la Mort": "💀", "Chasseur de Démons": "🦇", "Druide": "🐻",
    "Chasseur": "🏹", "Mage": "🔮", "Paladin": "🛡️", "Prêtre": "🙏",
    "Voleur": "🗡️", "Chaman": "⚡", "Démoniste": "🩸", "Guerrier": "⚔️"
}

# --- INITIALISATION ---
if 'data' not in st.session_state:
    # On ajoute des colonnes pour suivre l'argent réel
    st.session_state.data = pd.DataFrame(columns=[
        'Classe', 'Victoires', 'Défaites', 'Mode_Paiement', 
        'Cout_Gold', 'Cout_Euros', 
        'Rec_Gold', 'Rec_Poussiere', 'Rec_Tickets', 'Rentabilite_Gold'
    ])

# --- SIDEBAR : NOUVELLE RUN ---
st.sidebar.title("🍺 Nouvelle Run")
with st.sidebar.form("run_form"):
    
    # 1. Infos de jeu
    c_name = st.selectbox("Classe", list(CLASSES_LOGOS.keys()))
    wins = st.slider("Victoires 🏆", 0, 12, 3)
    loss = st.slider("Défaites ☠️", 0, 3, 3)
    
    st.markdown("---")
    
    # 2. Paiement
    paiement = st.radio("Moyen de paiement", ["Gold (300 po)", "Runes (Argent réel)"])
    
    st.markdown("---")
    
    # 3. Récompenses
    rec_gold = st.number_input("Gold gagnés", min_value=0, value=0)
    rec_dust = st.number_input("Poussière (Packs inclus)", min_value=0, value=0)
    rec_ticket = st.number_input("Tickets gagnés", min_value=0, value=0)
    
    submit = st.form_submit_button("Valider la Run")

    if submit:
        # LOGIQUE ÉCONOMIQUE
        cout_gold = 0
        cout_euros = 0
        
        # Calcul du coût
        if paiement == "Gold (300 po)":
            cout_gold = 300
        else:
            # 400 Runes pour 2 tickets. 
            # 500 Runes = 5€ => 1 Rune = 0.01€.
            # 400 Runes = 4.00€
            cout_euros = 4.00 
        
        # Calcul rentabilité Gold (Gold gagnés - Gold dépensés + Valeur des tickets gagnés)
        # On estime qu'un ticket gagné vaut 150 gold (moitié d'une entrée) pour le calcul de rentabilité virtuelle
        profit_gold_virtuel = rec_gold - cout_gold + (rec_ticket * 150)

        new_row = pd.DataFrame({
            'Classe': [c_name],
            'Victoires': [wins],
            'Défaites': [loss],
            'Mode_Paiement': [paiement],
            'Cout_Gold': [cout_gold],
            'Cout_Euros': [cout_euros],
            'Rec_Gold': [rec_gold],
            'Rec_Poussiere': [rec_dust],
            'Rec_Tickets': [rec_ticket],
            'Rentabilite_Gold': [profit_gold_virtuel]
        })
        st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
        st.success("Enregistré dans l'auberge !")

# --- DASHBOARD ---
df = st.session_state.data

st.title("🔥 Hearthstone Arena Manager")

if not df.empty:
    # --- KPI ---
    total_runs = len(df)
    total_euros = df['Cout_Euros'].sum()
    total_gold_net = df['Rentabilite_Gold'].sum()
    avg_wins = df['Victoires'].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Runs Jouées", total_runs)
    col2.metric("Moyenne Victoires", f"{avg_wins:.1f}")
    col3.metric("Gold Net (Virtuel)", f"{total_gold_net}", delta=int(total_gold_net))
    col4.metric("Dépense Réelle", f"{total_euros:.2f} €", delta=-total_euros, delta_color="inverse")

    # --- SÉCURITÉ : STOP LOSS ARGENT RÉEL ---
    st.markdown("---")
    
    # Seuil : Si on dépense plus de 15€ (3 runs payantes) sans gros résultat
    # On regarde les 5 dernières runs
    last_runs = df.tail(5)
    depense_recente = last_runs['Cout_Euros'].sum()
    
    if depense_recente >= 12.0: # 12 euros = 3 runs payantes en peu de temps
        st.error(f"🛑 STOP ! TU FLAMBES ! Dépense récente : {depense_recente}€")
        st.markdown("""
            <div style="background-color: #721c24; padding: 20px; border-radius: 10px; color: white;">
                <h3>🚨 ALERTE BALEINE ACTIVÉE</h3>
                <p>Tu as dépensé plus de 12€ sur tes dernières sessions.</p>
                <p>Ferme le jeu. Va prendre l'air. Ne relance pas une run avec ta carte bleue.</p>
            </div>
        """, unsafe_allow_html=True)
    elif depense_recente > 0:
        st.warning(f"⚠️ Attention, tu es en mode 'Payant'. Dépense récente : {depense_recente}€")
    else:
        st.success("✅ Mode 'Free to Play' ou dépenses maîtrisées.")

    # --- GRAPHIQUES ---
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("⚔️ Victoires par Classe")
        # Graphique en barre coloré
        fig_bar = px.bar(df, x='Classe', y='Victoires', color='Classe', title="Performance par héros")
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_g2:
        st.subheader("📉 Dépenses vs Or")
        # Comparaison Or vs Euros
        df['Run'] = range(1, len(df) + 1)
        df['Cumul_Euros'] = df['Cout_Euros'].cumsum()
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=df['Run'], y=df['Cumul_Euros'], mode='lines+markers', name='Dépense Cumulée (€)', line=dict(color='red')))
        fig_line.add_trace(go.Bar(x=df['Run'], y=df['Victoires'], name='Victoires', opacity=0.3))
        
        fig_line.update_layout(title="L'argent sort-il plus vite que les victoires ?", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_line, use_container_width=True)

    # --- HISTORIQUE ---
    st.subheader("📜 Registre des parties")
    st.dataframe(df.style.highlight_max(axis=0))

else:
    st.info("👋 Bienvenue à l'auberge ! Utilise le menu à gauche pour enregistrer ta première run.")
