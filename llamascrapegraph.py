import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pymongo import MongoClient
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate

# LLM
llm = Ollama(
    model="mistral",
    base_url="http://localhost:11434"
)

# MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["essais_cliniques"]
collection = db["cancer_digestif"]

# URLs à scraper (pages listant des essais)
base_urls = [
    "https://www.e-cancer.fr/Professionnels-de-sante/Le-registre-des-essais-cliniques",
    "https://www.ffcd.fr/index.php/recherche/essais-therapeutiques",
    "https://clinicaltrials.gov/search"
]

# Prompt Langchain
prompt_template = PromptTemplate.from_template("""
Tu es un expert en extraction d'information médicale.
Voici le contenu d'une page web concernant un essai clinique sur le cancer digestif :

"{text}"

Extrait un JSON structuré contenant les champs suivants :
- title
- summary
- eligibility_criteria
- treatment_type
- location
- start_date
- end_date
- status
- sponsor
- phase
- condition
- intervention
- study_design
- clinical_trial_id

Réponds uniquement avec du JSON, sans texte autour.
""")

def get_trial_links(page_url):
    """Récupère toutes les URLs d’essais cliniques trouvées sur une page liste"""
    print(f"Recherche des liens sur : {page_url}")
    try:
        response = requests.get(page_url, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        links = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            # Heuristique simple : liens contenant "essai", "trial", etc.
            if any(keyword in href.lower() for keyword in ["essai", "trial", "study", "fiche"]):
                full_url = urljoin(page_url, href)
                links.append(full_url)

        return links

    except Exception as e:
        print(f"Erreur lors de la récupération des liens sur {page_url} : {e}")
        return []

def extract_trial_data(url):
    """Scrape une page d’essai clinique et extrait les infos via LLM"""
    try:
        print(f"Scraping essai : {url}")
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n")
        chunk = text[:4000]

        prompt = prompt_template.format(text=chunk)
        result = llm(prompt)

        print(result)

    except Exception as e:
        print(f"Erreur sur l’essai {url} : {e}")

# --------- PIPELINE PRINCIPALE ---------

for base_url in base_urls:
    trial_urls = get_trial_links(base_url)

    for trial_url in trial_urls:
        extract_trial_data(trial_url)