"""
preprocessing/ner.py
Extraction d'entités nommées depuis le texte d'un CV avec spaCy.
Compatible fr_core_news_sm (Streamlit Cloud) et fr_core_news_sm (local).
"""
from __future__ import annotations

import re
from loguru import logger
from typing import Optional, Dict, List, Any


# ── Patterns compétences techniques (regex pur Python — sans spaCy REGEX) ────

_TECH_PATTERN: re.Pattern = re.compile(
    r"\b(Python|JavaScript|TypeScript|Java|C\+\+|Go|Rust|PHP|Ruby|Swift|Kotlin"
    r"|React|Angular|Vue|NodeJS|Node\.js|Django|Flask|FastAPI|Spring|Laravel"
    r"|TensorFlow|PyTorch|Scikit.learn|Keras|HuggingFace|BERT|GPT|LLM"
    r"|SQL|PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch|Cassandra"
    r"|Docker|Kubernetes|Terraform|Ansible|Jenkins|Git"
    r"|AWS|Azure|GCP|Linux|REST|GraphQL|gRPC"
    r"|NLP|Machine Learning|Deep Learning|Data Science|MLOps)\b",
    re.IGNORECASE,
)


# ── Chargement du modèle spaCy (essaie sm puis lg) ───────────────────────────

_nlp_cache: Optional[Any] = None

def _get_nlp() -> Optional[Any]:
    global _nlp_cache
    if _nlp_cache is not None:
        return _nlp_cache

    import spacy

    for model in ("fr_core_news_sm", "fr_core_news_md", "fr_core_news_lg"):
        try:
            _nlp_cache = spacy.load(model)
            logger.info(f"Modèle spaCy chargé : {model}")
            return _nlp_cache
        except OSError:
            continue

    logger.warning("Aucun modèle spaCy français trouvé — NER désactivée")
    return None


# ── Extraction ────────────────────────────────────────────────────────────────

def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extrait les entités d'un CV.
    - skills_tech   : regex Python (toujours actif, indépendant de spaCy)
    - persons / organizations / locations / dates : spaCy NER
    """
    entities: Dict[str, List[str]] = {
        "persons":       [],
        "organizations": [],
        "locations":     [],
        "dates":         [],
        "skills_tech":   [],
    }

    # Compétences techniques via regex pur (fiable, rapide, sans spaCy)
    matches = _TECH_PATTERN.findall(text)
    entities["skills_tech"] = sorted({m.lower() for m in matches})

    # NER spaCy pour personnes / orgs / lieux / dates
    nlp = _get_nlp()
    if nlp is None:
        return entities

    try:
        doc = nlp(text[:40_000])   # limite mémoire pour Streamlit Cloud
    except Exception as e:
        logger.warning(f"spaCy NER échouée : {e}")
        return entities

    for ent in doc.ents:
        val = ent.text.strip()
        if not val or len(val) < 2:
            continue
        if ent.label_ == "PER":
            entities["persons"].append(val)
        elif ent.label_ == "ORG":
            entities["organizations"].append(val)
        elif ent.label_ in ("LOC", "GPE"):
            entities["locations"].append(val)
        elif ent.label_ in ("DATE", "TIME"):
            entities["dates"].append(val)

    # Déduplique chaque liste
    for key in entities:
        entities[key] = list(dict.fromkeys(entities[key]))

    return entities
