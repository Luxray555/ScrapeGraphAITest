from scrapegraphai.graphs import SmartScraperGraph
from pydantic import BaseModel, Field
from pymongo import MongoClient

graph_config = {
    "llm": {
        "model": "ollama/mistral-nemo",
        "temperature": 0,
        "format": "json",
    },
    "verbose": True,
    "headless": False,
}

class URLListSchema(BaseModel):
    urls: list[str] = Field(description="Liste des URLs des essais cliniques")

class ClinicalTrialSchema(BaseModel):
    title: str = Field(description="Titre de l'essai clinique")
    summary: str = Field(description="Résumé de l'essai clinique")
    eligibility_criteria: str = Field(description="Critères d'éligibilité de l'essai clinique")
    treatment_type: str = Field(description="Type de traitement utilisé dans l'essai")
    location: str = Field(description="Lieu ou pays de l'essai clinique")
    start_date: str = Field(description="Date de début de l'essai")
    end_date: str = Field(description="Date de fin prévue ou effective")
    status: str = Field(description="Statut actuel de l'essai (en cours, terminé, etc.)")
    sponsor: str = Field(description="Organisme sponsor ou promoteur")
    phase: str = Field(description="Phase de l'essai (I, II, III, etc.)")
    condition: str = Field(description="Pathologie ou condition ciblée")
    intervention: str = Field(description="Type d’intervention (médicament, chirurgie, etc.)")
    study_design: str = Field(description="Plan de l’étude (randomisée, en double aveugle, etc.)")
    clinical_trial_id: str = Field(description="Identifiant unique de l'essai clinique")

class ListClinicalTrialsSchema(BaseModel):
    clinical_trials: list[ClinicalTrialSchema] = Field(description="Liste des essais cliniques")

def scrape_all_pages(url: str):
    smart_scraper_graph = SmartScraperGraph(
        prompt="Lister toutes les URLs des essais cliniques sur cette page",
        source=url,
        config=graph_config,
        schema=URLListSchema,
    )
    result = smart_scraper_graph.run()
    return result

def scrape_clinical_trial(url: str):
    smart_scraper_graph = SmartScraperGraph(
        prompt="Extraire les informations des essais cliniques pour le cancer digestif",
        source=url,
        config=graph_config,
        schema=ListClinicalTrialsSchema,
    )
    result = smart_scraper_graph.run()
    return result


def scrape_clinical_trials(url : str) :
    all_trials = []

    trial_urls = scrape_all_pages(url)
    for trial_url in trial_urls:
        trial_data = scrape_clinical_trial(trial_url)
        all_trials.append(trial_data)

    return all_trials

client = MongoClient("mongodb://localhost:27017/")  # Modifier si tu utilises une URI distante
db = client["essais_cliniques"]
collection = db["cancer_digestif"]

urls = [
    "https://www.e-cancer.fr/Professionnels-de-sante/Le-registre-des-essais-cliniques",
    "https://www.ffcd.fr",
    "https://clinicaltrials.gov/ct2/home"
]


for url in urls:
    clinical_trials = scrape_clinical_trial(url)
    print(clinical_trials)
