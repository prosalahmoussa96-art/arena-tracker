import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
import urllib.parse

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

# --- FONCTIONS DE PERSISTANCE ---
DATA_FILE = 'arena_data.json'

def save_data(df):
    """Sauvegarde les données dans un fichier JSON"""
    try:
        df.to_json(DATA_FILE, orient='records', date_format='iso')
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde : {e}")

def load_data():
    """Charge les données depuis le fichier JSON"""
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_json(DATA_FILE)
            df['Date'] = pd.to_datetime(df['Date'])
            return df
        except Exception as e:
            st.warning(f"Impossible de charger les données : {e}")
    
    return pd.DataFrame(columns=[
        'Date', 'Classe', 'Victoires', 'Défaites', 'Mode_Paiement', 
        'Cout_Gold', 'Cout_Euros', 
        'Rec_Gold', 'Rec_Poussiere', 'Rec_Tickets', 'Rentabilite_Gold'
    ])

# --- INITIALISATION ---
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
        # Validation des données
        if wins > 12:
            st.error("⚠️ Maximum 12 victoires en Arena !")
        elif loss > 3:
            st.error("⚠️ Maximum 3 défaites en Arena !")
        else:
            cout_gold = 300 if paiement == "Gold (300 po)" else 0
            cout_euros = 4.00 if paiement != "Gold (300 po)" else 0
            
            # Calcul rentabilité virtuelle (1 ticket = 150 gold)
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
            st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
            save_data(st.session_state.data)
            st.success("✅ C'est noté dans le grand livre !")

# Boutons de gestion dans la sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Gestion des Données")

col_b1, col_b2 = st.sidebar.columns(2)

with col_b1:
    if st.button("🔄 Recharger"):
        st.session_state.data = load_data()
        st.rerun()

with col_b2:
    if st.button("🗑️ Effacer Tout"):
        if st.session_state.get('confirm_delete', False):
            st.session_state.data = pd.DataFrame(columns=[
                'Date', 'Classe', 'Victoires', 'Défaites', 'Mode_Paiement', 
                'Cout_Gold', 'Cout_Euros', 
                'Rec_Gold', 'Rec_Poussiere', 'Rec_Tickets', 'Rentabilite_Gold'
            ])
            save_data(st.session_state.data)
            st.session_state.confirm_delete = False
            st.rerun()
        else:
            st.session_state.confirm_delete = True
            st.warning("⚠️ Clique encore une fois pour confirmer")

# --- DASHBOARD PRINCIPAL ---
df = st.session_state.data

# --- CORRECTION ET NETTOYAGE DES TYPES ---
# On force les colonnes numériques à être des nombres
numeric_cols = ['Victoires', 'Défaites', 'Cout_Gold', 'Cout_Euros', 'Rec_Gold', 'Rec_Poussiere', 'Rec_Tickets', 'Rentabilite_Gold']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

st.title("🛡️ Hearthstone Arena Master")
st.markdown("*Gère ta fortune et évite la ruine...*")
st.markdown("---")

if not df.empty:
    # --- KPI (STYLES CARTE) ---
    total_runs = len(df)
    total_euros = df['Cout_Euros'].sum()
    total_gold_net = df['Rentabilite_Gold'].sum()
    avg_wins = df['Victoires'].mean()
    
    # Calcul du taux de victoire global
    total_wins = df['Victoires'].sum()
    total_games = df['Victoires'].sum() + df['Défaites'].sum()
    win_rate = (total_wins / total_games * 100) if total_games > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Runs Jouées", total_runs)
    col2.metric("Moyenne Victoires", f"{avg_wins:.2f}")
    col3.metric("Taux de Victoire", f"{win_rate:.1f}%")
    col4.metric("Bénéfice (Gold)", f"{total_gold_net:.0f}", delta=int(total_gold_net))
    col5.metric("Dépense Réelle", f"{total_euros:.2f} €", delta=-total_euros, delta_color="inverse")

    # --- SÉCURITÉ : STOP LOSS "KRAKEN" ---
    st.markdown("### 🦑 Zone de Danger")
    
    last_runs = df.tail(5)
    depense_recente = last_runs['Cout_Euros'].sum()
    
    if depense_recente >= 12.0:
        st.markdown("""
<div style="background-color: #590d0d; padding: 15px; border: 2px solid #ff0000; border-radius: 10px; color: #ffcccc;">
    <h3 style="color: #ffcccc !important;">🚨 STOP IMMÉDIAT !</h3>
    <p><strong>Dépense critique détectée :</strong> Tu as lâché plus de 12€ récemment.</p>
    <p>La spirale de la défaite est active. Ferme le jeu. C'est un ordre de l'ingénieur.</p>
</div>
""", unsafe_allow_html=True)
    elif depense_recente > 0:
        st.warning(f"⚠️ Vigilance : Tu as dépensé {depense_recente}€ récemment. Reste concentré.")
    else:
        st.success("✅ Océan calme : Aucune dépense d'argent réel récente.")

    # --- ONGLETS ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Statistiques", "📜 Historique", "📧 Rapport Mensuel", "🏆 Records"])

    with tab1:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            # Bar Chart Classe avec taux de victoire
            class_stats = df.groupby('Classe').agg({
                'Victoires': 'sum',
                'Défaites': 'sum'
            }).reset_index()
            class_stats['Total_Games'] = class_stats['Victoires'] + class_stats['Défaites']
            
            # Protection contre la division par zéro
            class_stats = class_stats[class_stats['Total_Games'] > 0]
            
            class_stats['Taux_Victoire'] = (class_stats['Victoires'] / class_stats['Total_Games'] * 100).round(1)
            
            fig_bar = px.bar(class_stats, x='Classe', y='Victoires', 
                             title="Victoires par Héros",
                             text='Taux_Victoire',
                             color='Taux_Victoire',
                             color_continuous_scale='RdYlGn')
            fig_bar.update_traces(texttemplate='%{text}%', textposition='outside')
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                font_color='#f0e6d2', font_family="Lato"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_g2:
            # Line Chart Dépenses
            df_sorted = df.sort_values('Date')
            df_sorted['Cumul_Euros'] = df_sorted['Cout_Euros'].cumsum()
            fig_line = px.area(df_sorted, x='Date', y='Cumul_Euros', 
                               title="Évolution des Dépenses (€)",
                               color_discrete_sequence=['#ff4b4b'])
            fig_line.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                font_color='#f0e6d2', font_family="Lato"
            )
            st.plotly_chart(fig_line, use_container_width=True)
        
        # Statistiques par classe (détaillées)
        st.markdown("### 📈 Performance Détaillée par Classe")
        class_detail = df.groupby('Classe').agg({
            'Victoires': ['sum', 'mean'],
            'Défaites': 'sum',
            'Rentabilite_Gold': 'sum'
        }).round(2)
        class_detail.columns = ['Total Victoires', 'Moy. Victoires', 'Total Défaites', 'Profit Gold']
        st.dataframe(class_detail, use_container_width=True)

    with tab2:
        st.markdown("### 📜 Historique Complet")
        
        # Export CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger l'historique (CSV)",
            data=csv,
            file_name=f'arena_history_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
        )
        
        # --- VERSION CORRIGÉE : SANS GRADIENT DE COULEUR ---
        st.dataframe(
            df.sort_values('Date', ascending=False),
            use_container_width=True
        )

    with tab3:
        st.markdown("### 📧 Générateur de Rapport")
        st.write("Génère un email pré-rempli avec tes stats du mois.")
        
        # Sélecteur de mois
        current_month = datetime.now().month
        runs_this_month = df[df['Date'].dt.month == current_month]
        
        if not runs_this_month.empty:
            m_depense = runs_this_month['Cout_Euros'].sum()
            m_gold = runs_this_month['Rec_Gold'].sum()
            m_dust = runs_this_month['Rec_Poussiere'].sum()
            m_wins = runs_this_month['Victoires'].mean()
            nb_runs = len(runs_this_month)
            
            # Meilleure run du mois
            best_run = runs_this_month.loc[runs_this_month['Victoires'].idxmax()]
            
            # Création du contenu du mail
            subject = f"Rapport Arena Hearthstone - {datetime.now().strftime('%B %Y')}"
            
            rapport_text = f"""Voici mon bilan Hearthstone pour ce mois :

🏆 Performance :
- Runs jouées : {nb_runs}
- Moyenne Victoires : {m_wins:.2f}
- Meilleure Run : {best_run['Victoires']} victoires ({best_run['Classe']})

💰 Bilan Comptable :
- Dépense Réelle : {m_depense:.2f} €
- Gold Gagnés : {m_gold:.0f}
- Poussière : {m_dust:.0f}

⚠️ Statut : {"🔴 DÉPENSIER" if m_depense > 10 else "🟢 RENTABLE"}"""
            
            st.text_area("Aperçu du texte :", value=rapport_text, height=250)
            
            # Création du lien "mailto"
            body_encoded = urllib.parse.quote(rapport_text)
            subject_encoded = urllib.parse.quote(subject)
            mailto_link = f"mailto:?subject={subject_encoded}&body={body_encoded}"
            
            st.markdown(f'<a href="{mailto_link}" target="_blank" class="mail-link">📧 Ouvrir mon client mail avec ce rapport</a>', unsafe_allow_html=True)
            
        else:
            st.info("Aucune run enregistrée ce mois-ci. Joue un peu avant de faire des rapports !")

    with tab4:
        st.markdown("### 🏆 Hall of Fame")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        
        with col_r1:
            st.markdown("#### 🥇 Meilleure Run")
            best = df.loc[df['Victoires'].idxmax()]
            st.metric("Victoires", best['Victoires'])
            st.write(f"**Classe :** {best['Classe']}")
            st.write(f"**Date :** {best['Date'].strftime('%d/%m/%Y')}")
        
        with col_r2:
            st.markdown("#### 💎 Plus Profitable")
            most_profit = df.loc[df['Rentabilite_Gold'].idxmax()]
            st.metric("Profit Gold", f"{most_profit['Rentabilite_Gold']:.0f}")
            st.write(f"**Classe :** {most_profit['Classe']}")
            st.write(f"**Victoires :** {most_profit['Victoires']}")
        
        with col_r3:
            st.markdown("#### 🌟 Classe Favorite")
            fav_class = df['Classe'].value_counts().idxmax()
            fav_count = df['Classe'].value_counts().max()
            st.metric("Classe", fav_class)
            st.write(f"**Jouée :** {fav_count} fois")
            st.write(f"**Icône :** {CLASSES_LOGOS[fav_class]}")

else:
    st.info("👋 Bienvenue Voyageur ! Utilise le menu à gauche pour commencer.")
    st.markdown("""
### Comment utiliser cette app ?

1. **📝 Enregistre tes runs** via le formulaire à gauche
2. **📊 Analyse tes statistiques** pour identifier tes meilleures classes
3. **💰 Surveille tes dépenses** avec le système d'alerte Kraken
4. **📥 Exporte tes données** pour les sauvegarder ailleurs

*Que la chance soit avec toi dans l'Arène !*
""")
