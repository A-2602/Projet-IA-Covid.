import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration de la page
st.set_page_config(page_title="Analyse COVID-19 Mexique", layout="wide", page_icon="📊")

st.title("📊 Tableau de Bord - Analyse Pandémie COVID-19")
st.markdown("Cette application analyse les facteurs de risque liés au COVID-19 à partir des données cliniques.")

# 1. Chargement des données
@st.cache_data # Optimisation : évite de recharger le CSV à chaque interaction
def load_data():
    # Nom de ton fichier mis à jour
    file_name = 'covid19_data_nettoye.csv'
    
    # Lecture du fichier
    if os.path.exists(file_name):
        df = pd.read_csv(file_name)
        # Création de la colonne DEATH si elle n'existe pas pour l'analyse
        if 'DATE_DIED' in df.columns:
            df['DEATH'] = (df['DATE_DIED'] != '9999-99-99').astype(int)
        return df
    else:
        st.error(f"Fichier '{file_name}' introuvable dans le dossier.")
        return None

df = load_data()

if df is not None:
    # 2. Barre latérale pour la navigation
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2785/2785831.png", width=100)
    menu = st.sidebar.selectbox("Navigation", ["Analyse Exploratoire", "Modèle de Prédiction"])

    if menu == "Analyse Exploratoire":
        st.header("🔍 Analyse des Données Cliniques")
        
        # Métriques rapides
        m1, m2, m3 = st.columns(3)
        m1.metric("Nombre total de patients", f"{len(df):,}")
        m2.metric("Âge Moyen", f"{df['AGE'].mean():.1f} ans")
        if 'DEATH' in df.columns:
            m3.metric("Taux de Mortalité", f"{(df['DEATH'].mean()*100):.1f}%")

        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Répartition par Genre")
            fig, ax = plt.subplots()
            sns.countplot(data=df, x='SEX', hue='SEX', palette='pastel', ax=ax, legend=False)
            ax.set_xticklabels(['Femme (1)', 'Homme (2)'])
            st.pyplot(fig)

        with col2:
            st.subheader("Distribution des Âges")
            fig, ax = plt.subplots()
            sns.histplot(df['AGE'], bins=30, kde=True, color="skyblue", ax=ax)
            st.pyplot(fig)

    elif menu == "Modèle de Prédiction":
        st.header("🤖 Prédire le Risque Patient")
        st.write("Entrez les informations du patient pour évaluer le niveau de risque.")
        
        # Formulaire de saisie
        with st.container():
            age = st.slider("Âge du patient", 0, 100, 30)
            sex = st.selectbox("Genre", ["Femme", "Homme"])
            
            c1, c2, c3 = st.columns(3)
            pneu = c1.checkbox("Pneumonie")
            diab = c2.checkbox("Diabète")
            hip = c3.checkbox("Hypertension")
           
            cardio = st.checkbox("Maladies cardiovasculaires ?")
            obe = st.checkbox("Obésité ?")
            renal = st.checkbox("Insuffisance rénale chronique ?")
            tab  = st.checkbox("Tabagisme ?")
            ast = st.checkbox("Asthme ?")
        
        st.divider()
        
        if st.button("Lancer la Prédiction du Risque"):
            # Logique simplifiée (tu pourras charger ton modèle .pkl ici plus tard)
            if age > 60 or pneu:
                st.error("⚠️ **Résultat : Ce patient est considéré à HAUT RISQUE.**")
                st.write("Une hospitalisation immédiate est suggérée pour surveillance.")
            else:
                st.success("✅ **Résultat : Ce patient est considéré à BAS RISQUE.**")
                st.write("Le patient présente des facteurs stables pour un suivi à domicile.")

else:

    st.warning("Veuillez placer le fichier 'covid19_data_nettoye.csv' dans le même dossier que ce script.")
