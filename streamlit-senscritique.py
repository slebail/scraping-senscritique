
import streamlit as st
from scraping_functions import scraping_listes, dataframe_building

st.title("Scraping listes senscritique")

import streamlit as st

# Initialisation de la liste dans la session Streamlit
if "urls" not in st.session_state:
    st.session_state.urls = []

st.title("Ajouter des URLs à une liste")

# Barre d'input pour les URLs
url_input = st.text_input("Entrez une URL à ajouter à la liste :")

# Bouton pour ajouter l'URL
if st.button("Ajouter"):
    if url_input:
        st.session_state.urls.append(url_input)
        st.success(f"L'URL '{url_input}' a été ajoutée avec succès !")
    else:
        st.warning("Veuillez entrer une URL valide.")

# Affichage de la liste des URLs
if st.session_state.urls:
    st.subheader("Liste des URLs :")
    for idx, url in enumerate(st.session_state.urls, start=1):
        st.write(f"{idx}. {url}")
else:
    st.info("Aucune URL ajoutée pour le moment.")

if st.button("Construire le fichier excel"):
    scraping_listes(st.session_state.urls)
    dataframe = dataframe_building(scraping_listes)
    if 'dataframe' not in st.session_state:
        st.session_state.dataframe = dataframe

if st.session_state.dataframe:
    st.dataframe(st.session_state.dataframe)

