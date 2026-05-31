import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re

st.set_page_config(page_title="Metrodoku Clan", page_icon="🚇")
st.title("🏆 Championnat Metrodoku (Google Sheets)")

# 🔗 COPIE LE LIEN DE TON GOOGLE SHEET ICI
URL_DU_SHEET = https://docs.google.com/spreadsheets/d/1p7uGUSLNS-C4iVgSFHSWc-75-yEwr1xvoCkl-4yI0Lg/edit?usp=sharing

# Connexion automatique au Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

def charger_donnees():
    """Lit les données en direct depuis Google Sheets."""
    # On force le rafraîchissement (ttl=0) pour avoir les vrais scores à chaque seconde
    return conn.read(spreadsheet=URL_DU_SHEET, ttl=0)

def sauvegarder_donnees(df):
    """Met à jour le Google Sheet avec le nouveau tableau."""
    # GSheetsConnection permet d'écrire directement dans le tableau
    conn.update(spreadsheet=URL_DU_SHEET, data=df)

def extraire_score_du_texte(texte):
    match = re.search(r"(\d+)\s*/\s*900", texte)
    if match: return int(match.group(1))
    return None

# --- CHARGEMENT ---
try:
    df_scores = charger_donnees()
except Exception:
    st.error("Impossible de se connecter au Google Sheet. Vérifie le lien et le partage public.")
    df_scores = pd.DataFrame(columns=["Joueur", "Score_Total"])

# --- INTERFACE DE SAISIE ---
st.sidebar.header("Enregistrer un résultat")
with st.sidebar.form("form_metrodoku"):
    nom = st.text_input("Ton Prénom").strip().capitalize()
    texte_partage = st.text_area("Colle ton partage Metrodoku ici")
    valider = st.form_submit_button("Ajouter au classement")

if valider and nom:
    score_detecte = extraire_score_du_texte(texte_partage)
    
    if score_detecte is not None:
        # Si le joueur existe déjà
        if nom in df_scores["Joueur"].values:
            idx = df_scores.index[df_scores["Joueur"] == nom][0]
            # Attention, on s'assure que le score actuel est bien traité comme un nombre
            df_scores.at[idx, "Score_Total"] = int(df_scores.at[idx, "Score_Total"]) + score_detecte
        else:
            nouveau = pd.DataFrame({"Joueur": [nom], "Score_Total": [score_detecte]})
            df_scores = pd.concat([df_scores, nouveau], ignore_index=True)
        
        # Envoi immédiat vers Google Sheets !
        sauvegarder_donnees(df_scores)
        st.sidebar.success(f"Score ajouté pour {nom} !")
        st.rerun()
    else:
        st.sidebar.error("Score introuvable dans le texte.")

# --- AFFICHAGE ---
st.header("📊 Classement Général")

if not df_scores.empty:
    # On s'assure que la colonne des scores contient des nombres pour bien trier
    df_scores["Score_Total"] = pd.to_numeric(df_scores["Score_Total"])
    df_sorted = df_scores.sort_values(by="Score_Total", ascending=False).reset_index(drop=True)
    st.table(df_sorted)
else:
    st.info("Le tableau est vide.")
