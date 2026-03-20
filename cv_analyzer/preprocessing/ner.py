"""
preprocessing/ner.py
Extraction d'entités nommées depuis le texte d'un CV avec spaCy.
Identifie : personnes, organisations, lieux, dates, compétences (règles custom).
"""
from __future__ import annotations

import re
from functools import lru_cache
from typing import Optional

from loguru import logger


# ── Chargement paresseux du modèle ───────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_nlp():
    try:
        import spacy
        nlp = spacy.load("fr_core_news_lg")
        logger.info("Modèle spaCy fr_core_news_lg chargé")
        return nlp
    except OSError:
        logger.warning("fr_core_news_lg non trouvé — NER désactivée")
        return None


# ── Patterns compétences techniques (règles custom) ─────────────────────────

_TECH_PATTERN = re.compile(
    r"\b(Python|Java(?:Script)?|TypeScript|C\+\+|C#|Go|Rust|PHP|Ruby|Swift|Kotlin"
    r"|React|Angular|Vue|Node\.js|Django|Flask|FastAPI|Spring|Laravel"
    r"|TensorFlow|PyTorch|scikit.learn|Keras|HuggingFace|BERT|GPT"
    r"|SQL|PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch|Cassandra"
    r"|Docker|Kubernetes|Terraform|Ansible|Jenkins|GitLab CI|GitHub Actions"
    r"|AWS|Azure|GCP|Linux|Git|REST|GraphQL|gRPC"
    r"|NLP|ML|Deep Learning|Machine Learning|Data Science|LLM)\b",
    re.IGNORECASE
)


def extract_entities(text: str) -> dict:
    """
    Extrait toutes les entités utiles d'un CV.
    Retourne un dict avec :
      - persons       : noms détectés
      - organizations : entreprises / écoles
      - locations     : villes / pays
      - dates         : périodes / années
      - skills_tech   : compétences techniques (regex)
    """
    entities: dict = {
        "persons":       [],
        "organizations": [],
        "locations":     [],
        "dates":         [],
        "skills_tech":   [],
    }

    # Compétences techniques via regex (plus fiable que NER pour les sigles)
    tech = _TECH_PATTERN.findall(text)
    entities["skills_tech"] = list({t.lower() for t in tech})

    # NER spaCy
    nlp = _get_nlp()
    if nlp is None:
        return entities

    doc = nlp(text[:50_000])  # limite pour la RAM
    for ent in doc.ents:
        val = ent.text.strip()
        if not val or len(val) < 2:
            continue
        if ent.label_ == "PER":
            entities["persons"].append(val)
        elif ent.label_ == "ORG":
            entities["organizations"].append(val)
        elif ent.label_ == "LOC":
            entities["locations"].append(val)
        elif ent.label_ in ("DATE", "TIME"):
            entities["dates"].append(val)

    # Déduplique
    for key in entities:
        if isinstance(entities[key], list):
            entities[key] = list(dict.fromkeys(entities[key]))

    return entities
