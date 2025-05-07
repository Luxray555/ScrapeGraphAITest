import json

import requests
from bs4 import BeautifulSoup
from mistralai import Mistral

# Configuration de l'API Mistral (remplace par ton endpoint et clé)
MISTRAL_API_KEY = "WQkBHs4Mqg9dl5HXamD6dhFceQgmNz37"

client = Mistral(api_key=MISTRAL_API_KEY)

base_urls = [
    "https://www.e-cancer.fr/Professionnels-de-sante/Le-registre-des-essais-cliniques",
    "https://www.ffcd.fr/index.php/recherche/essais-therapeutiques",
    "https://clinicaltrials.gov/search"
]

def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return text

def ask_mistral_all_clinical_trial_urls(page):
    chat_response = client.chat.complete(
        model="open-mistral-nemo",
        messages=[
            {
            "role": "system",
            "content": """
                Tu es un assistant qui extrait des informations sur les essais cliniques à partir de pages web sans les analyser et sans ecrire de commentaires.
                Tu dois extraire les informations suivantes :
                - urls : Liste des URLs des essais cliniques trouvées sur la page sinon liste vide, c'est à dire les liens qui mènent vers des pages individuelles d’essais cliniques.
                Assure-toi que les informations sont bien structurées et au format JSON.
                """,
            },
            {
                "role": "user",
                "content": f"Voici le texte de la page : {page}"
            }
        ]
    )
    return chat_response

def ask_mistral_clinical_trial_info(page):
    chat_response = client.chat.complete(
        model="open-mistral-nemo",
        messages=[
            {
            "role": "system",
                "content": """
                Tu es un assistant qui extrait des informations sur les essais cliniques à partir de pages web.
                Tu dois extraire les informations suivantes :
                - title : Titre de l’essai clinique
                - summary : Résumé (description) de l’essai clinique
                - eligibility_criteria : Critères d’éligibilité {
                    - inclusion : Critères d'inclusion
                    - exclusion : Critères d'exclusion
                }
                - treatment_type : Type de traitement (médicament, chirurgie, etc.)
                - locations : Liste des lieux ou pays où l’essai clinique est mené (hôpital, pays, etc.) sinon liste vide
                - start_date : Date de début (format : JJ/MM/AAAA)
                - end_date : Date de fin (format : JJ/MM/AAAA)
                - status : Statut (en cours, terminé)
                - sponsor : Sponsor (organisme sponsor)
                - phase : Phase (I, II, III, etc.)
                - pathology : Pathologie ciblée (cancer, maladie rare, etc.)
                - intervention : Type d’intervention (médicament, chirurgie, etc.)
                - study_design : Plan de l’étude (randomisée, en double aveugle, etc.)
                - clinical_trial_id : Identifiant de l’essai clinique
                Assure-toi que les informations sont bien structurées et au format JSON, sans commentaires ni analyses.
                """
            },
            {
                "role": "user",
                "content": f"Voici le texte de la page : {page}"
            }
        ],
    )
    return chat_response

def extract_all_clinical_trial_urls(url):
    html_text = extract_text_from_url(url)

    response = ask_mistral_all_clinical_trial_urls(html_text)
    return json.loads(response.choices[0].message.content.strip().removeprefix("```json").removesuffix("```").strip()).get("urls", [])

def extract_clinical_trial_info(url):
    html_text = extract_text_from_url(url)

    response = ask_mistral_clinical_trial_info(html_text)
    print(response.choices[0].message.content)
    return json.loads(response.choices[0].message.content.strip().removeprefix("```json").removesuffix("```").strip())

if __name__ == "__main__":
    # Exemple d'URL d’essai clinique :
    url = "https://clinicaltrials.gov/study/NCT06952452?rank=1"

    data = extract_clinical_trial_info(url)

    print(data)