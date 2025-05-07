import requests
from bs4 import BeautifulSoup
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate

# LLM
llm = Ollama(
    model="mistral-nemo",
    base_url="http://localhost:11434"
)

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

def extract_trial_data(url):
    """Scrape une page d’essai clinique et extrait les infos via LLM"""
    try:
        print(f"Scraping essai : {url}")
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n")

        prompt = prompt_template.format(text=text)
        result = llm(prompt)

        return result

    except Exception as e:
        print(f"Erreur sur l’essai {url} : {e}")

if __name__ == "__main__":
    # Exemple d'URL d’essai clinique :
    url = "https://clinicaltrials.gov/study/NCT06952452?rank=1"

    trial_info = extract_trial_data(url)
    print(trial_info)