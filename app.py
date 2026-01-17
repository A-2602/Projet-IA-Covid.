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
            # On considère comme décédé si la date n'est pas la valeur par défaut 9999-99-99
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
        st.header("🔍 Analyse Descriptive Complète")
        
        # Métriques rapides
        m1, m2, m3 = st.columns(3)
        m1.metric("Nombre total de patients", f"{len(df):,}")
        m2.metric("Âge Moyen", f"{df['AGE'].mean():.1f} ans")
        if 'DEATH' in df.columns:
            m3.metric("Taux de Mortalité", f"{(df['DEATH'].mean()*100):.1f}%")

        st.divider()
        
        # --- PREMIÈRE LIGNE : GENRE ET ÂGE ---
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("1. Répartition par Genre")
            fig1, ax1 = plt.subplots()
            sns.countplot(data=df, x='SEX', hue='SEX', palette='pastel', ax=ax1, legend=False)
            ax1.set_xticklabels(['Femme (1)', 'Homme (2)'])
            st.pyplot(fig1)
            st.caption("Distribution globale des patients par sexe.")

        with col2:
            st.subheader("2. Distribution des Âges")
            fig2, ax2 = plt.subplots()
            sns.histplot(df['AGE'], bins=30, kde=True, color="skyblue", ax=ax2)
            st.pyplot(fig2)
            st.caption("La majorité des patients se situe entre 30 et 60 ans.")

        st.divider()

        # --- DEUXIÈME LIGNE : COMORBIDITÉS ET INSTITUTIONS ---
        col3, col4 = st.columns(2)

        with col3:
            st.subheader("3. Comorbidités (Cas Décédés)")
            # Filtrage des cas critiques (décès)
            critiques = df[df['DEATH'] == 1]
            
            # Calcul des fréquences pour chaque pathologie (on vérifie si la valeur est 1 = Oui)
            com_data = {
                'Pneumonie': (critiques['PNEUMONIA'] == 1).sum(),
                'Diabète': (critiques['DIABETES'] == 1).sum(),
                'Hypertension': (critiques['HIPERTENSION'] == 1).sum(),
                'Obésité': (critiques['OBESITY'] == 1).sum()
            }
            
            com_df = pd.DataFrame(list(com_data.items()), columns=['Maladie', 'Nombre'])
            com_df = com_df.sort_values(by='Nombre', ascending=False)

            fig3, ax3 = plt.subplots()
            sns.barplot(data=com_df, x='Nombre', y='Maladie', palette='Reds_r', ax=ax3)
            st.pyplot(fig3)
            st.caption("La pneumonie est le facteur le plus fréquent chez les cas critiques.")

        with col4:
            st.subheader("4. Survie par Institution")
            # Mapping des noms d'institutions (selon le dictionnaire officiel du dataset)
            medical_unit_names = {
                1: "SANTÉ LOCALE", 2: "SANTÉ NAT.", 3: "IMSS", 
                4: "ISSSTE", 12: "PRIVÉ", 13: "AUTRES"
            }
            df['UNIT_NAME'] = df['MEDICAL_UNIT'].map(medical_unit_names).fillna("AUTRES")
            
            # Calcul du taux de survie (1 - moyenne de décès) * 100
            survie_stats = df.groupby('UNIT_NAME')['DEATH'].apply(lambda x: (1 - x.mean()) * 100).sort_values()

            fig4, ax4 = plt.subplots()
            survie_stats.plot(kind='barh', color='lightgreen', ax=ax4)
            ax4.set_xlabel("Taux de Survie (%)")
            st.pyplot(fig4)
            st.caption("Comparaison de la performance de survie entre les types d'unités.")

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
            
            c4, c5, c6 = st.columns(3)
            cardio = c4.checkbox("Maladies cardiovasculaires")
            obe = c5.checkbox("Obésité")
            renal = c6.checkbox("Insuffisance rénale chronique")
            
            c7, c8 = st.columns(2)
            tab = c7.checkbox("Tabagisme")
            ast = c8.checkbox("Asthme")
        
        st.divider()
        
        if st.button("Lancer la Prédiction du Risque"):
            # Logique simplifiée (Logique métier de base)
            # Un score de risque basé sur les facteurs aggravants connus
            score_risque = 0
            if age > 60: score_risque += 2
            if pneu: score_risque += 3
            if diab: score_risque += 1
            if hip: score_risque += 1
            if renal: score_risque += 2

            if score_risque >= 3:
                st.error(f"🚨 **RÉSULTAT : Patient à HAUT RISQUE (Score: {score_risque})**")
                st.write("Une hospitalisation immédiate ou une surveillance étroite est suggérée.")
            else:
                st.success(f"✅ **RÉSULTAT : Patient à BAS RISQUE (Score: {score_risque})**")
                st.write("Le patient présente des facteurs stables. Un suivi à domicile peut être envisagé.")

else:
    st.warning("Veuillez placer le fichier 'covid19_data_nettoye.csv' dans le même dossier que ce script.")
