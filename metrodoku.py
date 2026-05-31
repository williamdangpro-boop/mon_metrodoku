import streamlit as st
import pandas as pd
import os

# Nom du fichier où seront stockés les scores
DB_FILE = "scores_metrodoku.csv"

st.set_page_config(page_title="Metrodoku Clan", page_icon="🚇")
st.title("🏆 Championnat Metrodoku")

# --- FONCTIONS DE GESTION DES DONNÉES ---

def charger_donnees():
    """Charge les scores depuis le fichier CSV ou crée un tableau vide."""
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Joueur", "Score_Total"])

def sauvegarder_donnees(df):
    """Enregistre le tableau dans le fichier CSV."""
    df.to_csv(DB_FILE, index=False)

# --- LOGIQUE PRINCIPALE ---

df_scores = charger_donnees()

# Formulaire dans la barre latérale
st.sidebar.header("Enregistrer le score du jour")
with st.sidebar.form("form_score"):
    nom = st.text_input("Prénom du joueur").strip().capitalize()
    score_du_jour = st.number_input("Score obtenu aujourd'hui", min_value=0, max_value=900)
    valider = st.form_submit_button("Ajouter les points")

if valider and nom:
    # Si le joueur existe déjà, on additionne
    if nom in df_scores["Joueur"].values:
        index = df_scores.index[df_scores["Joueur"] == nom][0]
        df_scores.at[index, "Score_Total"] += score_du_jour
    # Sinon, on crée le joueur
    else:
        nouvel_utilisateur = pd.DataFrame({"Joueur": [nom], "Score_Total": [score_du_jour]})
        df_scores = pd.concat([df_scores, nouvel_utilisateur], ignore_index=True)
    
    sauvegarder_donnees(df_scores)
    st.sidebar.success(f"Points ajoutés pour {nom} !")
    st.rerun() # Rafraîchit la page pour voir le changement

# --- AFFICHAGE ---

st.header("📊 Classement Général")

if not df_scores.empty:
    # On trie pour avoir le premier en haut
    df_sorted = df_scores.sort_values(by="Score_Total", ascending=False).reset_index(drop=True)
    
    # On affiche un beau tableau
    st.dataframe(df_sorted, use_container_width=True)
    
    # Petit bonus : un graphique pour voir qui domine
    st.bar_chart(data=df_sorted, x="Joueur", y="Score_Total")
else:
    st.info("Aucun score enregistré. Commencez la compétition !")