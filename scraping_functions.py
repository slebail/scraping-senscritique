from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import numpy as np
import pandas as pd


def scraping_listes(urls):

    urls_1 = [url[:-1] for url in urls]

    books_total=[]
    auteurs_total = []
    list_total = []
    notes_total = []

    driver = webdriver.Chrome()

    try:
        consent_clicked = False  # Flag pour indiquer si le bouton consentement a été cliqué

        for url in urls_1:
            # Extraire le nom de la liste depuis l'URL
            list_name_match = re.search(r"/liste/([^/]+)/", url)
            if list_name_match:
                list_name = list_name_match.group(1)
            else:
                list_name = "Unknown"

            for i in range(1, 101):  # On suppose un maximum de 100 pages
                # Charger la page
                driver.get(f"{url}{i}")

                # Gérer la pop-up de consentement uniquement sur la première page
                if not consent_clicked:
                    try:
                        consent_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
                        )
                        consent_button.click()
                        consent_clicked = True  # Marquer le bouton comme cliqué
                        print("Consent button clicked.")
                    except Exception as e:
                        print("Consent button not found or already clicked.")

                # Vérifier s'il y a du contenu sur la page (par exemple, vérifier s'il y a des livres)
                try:
                    book_author_containers = WebDriverWait(driver, 3).until(
                        EC.presence_of_all_elements_located(
                            (By.CLASS_NAME, 'sc-e6f263fc-0.sc-47f61275-0.fzmpxB.fyVVLV.sc-6b8f8da3-6.jLINWO')
                        )
                    )
                except Exception as e:
                    print(f"No content found on page {i}. Ending loop.")
                    break

                # Extraire les titres et auteurs
                for container in book_author_containers:
                    # Extraire les auteurs pour chaque livre
                    author_links = container.find_elements(By.CSS_SELECTOR, 'a[data-testid="link"]')
                    book_authors = [link.text for link in author_links]

                    # Ajouter à la liste des auteurs pour cette page
                    auteurs_total.append(book_authors[0] if len(book_authors) == 1 else book_authors)
                    list_total.append(list_name)  # Ajouter le nom de la liste

                # Extraire les titres des livres
                h3_elements = driver.find_elements(By.TAG_NAME, "h3")
                titles_list = [h3.text for h3 in h3_elements]
                books_total.extend(titles_list)
                
                # Extractions des notes
                books = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='poster']")
                
                for book in books:
                    try:
                        rating = book.find_element(By.CSS_SELECTOR, "div[data-testid='Rating']").text
                        notes_total.append(rating)
                    except:
                        notes_total.append(np.nan)

                

                print(f"Page {i} processed for list '{list_name}'. Found {len(titles_list)} books.")

    finally:
    
        # Fermer le driver à la fin
        driver.quit()
    
    return books_total, auteurs_total, list_total, notes_total

def dataframe_building(books_total, auteurs_total, list_total, notes_total):

    df = pd.DataFrame({'Titres':books_total,
                   'Auteur(s)':auteurs_total,
                  'Liste':list_total,
                  'Notes':notes_total})
    
    df2 = df.copy()

    # Convertir les listes d'auteurs en une chaîne séparée par des virgules
    df2["Auteur(s)"] = df2["Auteur(s)"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)


    # Compter les occurrences de chaque combinaison "Titres" et "Auteur(s)"
    df2["recensé"] = df2.groupby(['Titres', 'Auteur(s)'])['Titres'].transform('count')

    # Grouper par "Titres" et "Auteur(s)" pour combiner les listes et supprimer les doublons
    df_unique = df2.groupby(['Titres', 'Auteur(s)']).agg({
        'Liste': lambda x: ", ".join(sorted(set(x))),  # Combine les listes uniques, triées
        'recensé': 'first', # Conserve le nombre recensé
        'Notes': 'first'
    }).reset_index()

    # Afficher le DataFrame final

    df_final = df_unique.sort_values(['recensé', 'Notes'], ascending=False)
    return df_final
