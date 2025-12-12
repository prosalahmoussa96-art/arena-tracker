import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import urllib.parse
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Hearthstone Arena Master", page_icon="🍺", layout="wide")

# --- LE SKIN "AUBERGE" ---
css_code = """
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Lato&display=swap" rel="stylesheet">
<style>
.stApp {background: radial-gradient(circle, #3b2b1e 0%, #1a120b 100%); color: #f0e6d2; font-family: 'Lato', sans-serif;}
h1, h2, h3 {font-family: 'Cinzel', serif !important; color: #fcd144 !important; text-shadow: 2px 2px 0px #000; letter-spacing: 1px;}
section[data-testid="stSidebar"] {background-color: #241c15; border-right: 2px solid #5c4b35;}
div[data-testid="stMetric"] {background-color: #4a3b2a; border: 2px solid #fcd144; border-radius: 10px; padding: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.5);}
div[data-testid="stMetricValue"] {color: #fff !important; font-family: 'Cinzel', serif;}
div[data-testid="stMetricLabel"] {color: #e0d0b0 !important;}
.stButton>button {background: linear-gradient(to bottom, #3b5ca3 0%, #223a6b 100%); color: white; border: 2px solid #6b8cce; border-radius: 5px; font-family: 'Cinzel', serif; font-weight: bold; text-transform: uppercase;}
.stButton>button:hover {background: linear-gradient(to bottom, #4a75cc 0%, #2b4b8a 100%); border-color: #fff;}
.stAlert {background-color: #2b221a; border: 1px solid #5c4b35; color: #f0e6d2;}
.mail-link {display: inline-block; padding: 10px 20px; background-color: #fcd144; color: #3b2b1e !important; text-decoration: none; border-radius: 5px; font-weight: bold; font-family: 'Cinzel', serif; border: 2px solid #b8860b;}
.mail-link:hover {background-color: #e5be35; border-color: #fff;}
</style>
"""
st.markdown(css_code, unsafe_allow_html=True)

# --- DONNÉES ET LOGOS ---
CLASSES_LOGOS = {
    "Chevalier de la Mort": "💀", "Chasseur de Démons": "🦇", "Druide": "🐻",
    "Chasseur": "🏹", "Mage": "🔮", "Paladin": "🛡️", "Prêtre": "🙏",
    "Voleur": "🗡️", "Chaman": "⚡", "Démoniste": "🩸", "Guerrier": "⚔️"
}

# --- CONNEXION GOOGLE SHEETS ---
# On établit la connexion avec les secrets configurés
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    """Charge les données depuis Google Sheets"""
    try:
        # On lit le sheet. ttl=0 permet de ne pas garder de cache (données fraîches à chaque rechargement)
        df = conn.read(ttl=0)
        
        # Si le sheet est vide ou nouveau, on s'assure d'avoir les bonnes colonnes
        expected_cols = [
            'Date', 'Classe', 'Victoires', 'Défaites', 'Mode_Paiement', 
            'Cout_Gold', 'Cout_Euros', 
            'Rec_Gold', 'Rec_Poussiere', 'Rec_Tickets', 'Rentabilite_Gold'
        ]
        
        # Vérification si le DataFrame est vide ou manque de colonnes
        if df.empty or len(df.columns) < len(expected_cols):
             return pd.DataFrame(columns=expected_cols)
             
        # Conversion de la date
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        return df

    except Exception as e:
        # En cas d'erreur (fichier vide ou inexistant), on retourne un tableau vide sans planter
        return pd.DataFrame(columns=[
            'Date', 'Classe', 'Victoires', 'Défaites', 'Mode_Paiement', 
            'Cout_Gold', 'Cout_Euros', 
            'Rec_Gold', 'Rec_Poussiere', 'Rec_Tickets', 'Rentabilite_Gold'
        ])

def save_new_run(new_row_df):
    """Ajoute une ligne au Google Sheet"""
    try:
        # On charge les données actuelles
        current_df = load_data()
        
        # On s'assure que current_df a bien les bonnes colonnes, sinon on concatène quand même
        updated_df = pd.concat([current_df, new_row_df], ignore_index=True)
        
        # On écrit tout dans le Google Sheet
        conn.update(data=updated_df)
        st.cache_data.clear() # On vide le cache
        return updated_df
    except Exception as e:
        st.error(f"Erreur de connexion Google Sheets : {e}")
        return None

def clear_all_data():
    """Efface tout le contenu du Sheet"""
    empty_df = pd.DataFrame(columns=[
        'Date', 'Classe', 'Victoires', 'Défaites', 'Mode_Paiement', 
        'Cout_Gold', 'Cout_Euros', 
        'Rec_Gold', 'Rec_Poussiere', 'Rec_Tickets', 'Rentabilite_Gold'
    ])
    conn.update(data=empty_df)
    st.cache_data.clear()
    return empty_df

# --- INITIALISATION ---
# On charge les données au démarrage
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# --- SIDEBAR : NOUVELLE RUN ---
st.sidebar.markdown("## 🍺 L'Aubergiste")
with st.sidebar.form("run_form"):
    st.markdown("### Nouvelle Entrée")
    
    date_run = st.date_input("Date", datetime.now())
    c_name = st.selectbox("Héros", list(CLASSES_LOGOS.keys()))
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        wins = st.number_input("Victoires 🏆", 0, 12, 3)
    with col_s2:
        loss = st.number_input("Défaites ☠️", 0, 3, 3)
    
    st.markdown("---")
    st.markdown("### 💰 Trésorerie")
    paiement = st.radio("Droit d'entrée payé en :", ["Gold (300 po)", "Runes (Argent réel)"])
    
    rec_gold = st.number_input("Gold gagnés", min_value=0, value=0)
    rec_dust = st.number_input("Poussière (Packs inclus)", min_value=0, value=0)
    rec_ticket = st.number_input("Tickets gagnés", min_value=0, value=0)
    
    submit = st.form_submit_button("Enregistrer la Run")

    if submit:
        if wins > 12:
            st.error("⚠️ Maximum 12 victoires en Arena !")
        elif loss > 3:
            st.error("⚠️ Maximum 3 défaites en Arena !")
        else:
            cout_gold = 300 if paiement == "Gold (300 po)" else 0
            cout_euros = 4.00 if paiement != "Gold (300 po)" else 0
            profit_gold_virtuel = rec_gold - cout_gold + (rec_ticket * 150)

            new_row = pd.DataFrame({
                'Date': [pd.to_datetime(date_run)],
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
            
            with st.spinner('Sauvegarde dans le Cloud en cours...'):
                updated_data = save_new_run(new_row)
                if updated_data is not None:
                    st.session_state.data = updated_data
                    st.success("✅ Sauvegardé dans Google Sheets pour l'éternité !")

# Boutons de gestion
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Gestion")

col_b1, col_b2 = st.sidebar.columns(2)
with col_b1:
    if st.button("🔄 Recharger"):
        st.session_state.data = load_data()
        st.rerun()

with col_b2:
    if st.button("🗑️ Reset Sheet"):
        if st.session_state.get('confirm_delete', False):
            st.session_state.data = clear_all_data()
            st.session_state.confirm_delete = False
            st.rerun()
        else:
            st.session_state.confirm_delete = True
            st.warning("⚠️ Confirmation requise")

# --- DASHBOARD PRINCIPAL ---
df = st.session_state.data

# Nettoyage des types numériques
numeric_cols = ['Victoires', 'Défaites', 'Cout_Gold', 'Cout_Euros', 'Rec_Gold', 'Rec_Poussiere', 'Rec_Tickets', 'Rentabilite_Gold']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

st.title("🛡️ Hearthstone Arena Master")
st.markdown("*Connecté au Cloud - Données sécurisées*")
st.markdown("---")

if not df.empty:
    # --- KPI ---
    total_runs = len(df)
    total_euros = df['Cout_Euros'].sum()
    total_gold_net = df['Rentabilite_Gold'].sum()
    avg_wins = df['Victoires'].mean()
    
    total_wins = df['Victoires'].sum()
    total_games = df['Victoires'].sum() + df['Défaites'].sum()
    win_rate = (total_wins / total_games * 100) if total_games > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Runs Jouées", total_runs)
    col2.metric("Moyenne Victoires", f"{avg_wins:.2f}")
    col3.metric("Taux de Victoire", f"{win_rate:.1f}%")
    col4.metric("Bénéfice (Gold)", f"{total_gold_net:.0f}", delta=int(total_gold_net))
    col5.metric("Dépense Réelle", f"{total_euros:.2f} €", delta=-total_euros, delta_color="inverse")

    # --- KRAKEN ---
    last_runs = df.tail(5)
    depense_recente = last_runs['Cout_Euros'].sum()
    
    if depense_recente >= 12.0:
        st.markdown("""<div style="background-color: #590d0d; padding: 15px; border: 2px solid #ff0000; border-radius: 10px; color: #ffcccc;">
        <h3 style="color: #ffcccc !important;">🚨 STOP IMMÉDIAT !</h3><p>Dépense critique (>12€).</p></div>""", unsafe_allow_html=True)
    elif depense_recente > 0:
        st.warning(f"⚠️ Vigilance : {depense_recente}€ dépensés récemment.")

    # --- ONGLETS ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Stats", "📜 Historique", "📧 Rapport", "🏆 Records"])

    with tab1:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            class_stats = df.groupby('Classe').agg({'Victoires': 'sum', 'Défaites': 'sum'}).reset_index()
            class_stats['Total_Games'] = class_stats['Victoires'] + class_stats['Défaites']
            class_stats = class_stats[class_stats['Total_Games'] > 0]
            class_stats['Taux_Victoire'] = (class_stats['Victoires'] / class_stats['Total_Games'] * 100).round(1)
            
            fig_bar = px.bar(class_stats, x='Classe', y='Victoires', title="Victoires par Héros",
                             text='Taux_Victoire', color='Taux_Victoire', color_continuous_scale='RdYlGn')
            fig_bar.update_traces(texttemplate='%{text}%', textposition='outside')
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#f0e6d2')
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_g2:
            df_sorted = df.sort_values('Date')
            df_sorted['Cumul_Euros'] = df_sorted['Cout_Euros'].cumsum()
            fig_line = px.area(df_sorted, x='Date', y='Cumul_Euros', title="Dépenses (€)", color_discrete_sequence=['#ff4b4b'])
            fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#f0e6d2')
            st.plotly_chart(fig_line, use_container_width=True)
            
    with tab2:
        st.markdown("### 📜 Historique")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger CSV", csv, "history.csv", "text/csv")
        st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)

    with tab3:
        st.markdown("### 📧 Rapport")
        current_month = datetime.now().month
        runs_this_month = df[df['Date'].dt.month == current_month]
        
        if not runs_this_month.empty:
            m_depense = runs_this_month['Cout_Euros'].sum()
            m_gold = runs_this_month['Rec_Gold'].sum()
            m_wins = runs_this_month['Victoires'].mean()
            nb_runs = len(runs_this_month)
            best_run = runs_this_month.loc[runs_this_month['Victoires'].idxmax()]
            
            subject = f"Rapport HS - {datetime.now().strftime('%B %Y')}"
            rapport_text = f"""Bilan du mois :
- Runs : {nb_runs}
- Moy. Wins : {m_wins:.2f}
- Best : {best_run['Victoires']} ({best_run['Classe']})
- Dépense : {m_depense:.2f} €
- Gold : {m_gold:.0f}"""
            
            st.text_area("Aperçu", rapport_text, height=200)
            mailto = f"mailto:?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(rapport_text)}"
            st.markdown(f'<a href="{mailto}" target="_blank" class="mail-link">📧 Envoyer le rapport</a>', unsafe_allow_html=True)
        else:
            st.info("Pas de run ce mois-ci.")

    with tab4:
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            best = df.loc[df['Victoires'].idxmax()]
            st.metric("Meilleure Run", f"{best['Victoires']} Wins")
            st.caption(f"{best['Classe']} - {best['Date'].strftime('%d/%m')}")
        with col_r2:
            most_profit = df.loc[df['Rentabilite_Gold'].idxmax()]
            st.metric("Max Profit", f"{most_profit['Rentabilite_Gold']:.0f} Gold")
        with col_r3:
            fav_class = df['Classe'].value_counts().idxmax()
            st.metric("Classe Favorite", fav_class)

else:
    st.info("👋 Bienvenue ! Tes données sont maintenant connectées au Cloud Google.")
    st.markdown("""
    Enregistre ta première run dans la colonne de gauche pour initialiser la base de données.
    Si tu vois une erreur, vérifie que tu as bien partagé ton Google Sheet avec l'email du bot !
    """)
