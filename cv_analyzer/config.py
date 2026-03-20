"""
config.py — Configuration centrale du projet
"""
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent

# ── Modèles ──────────────────────────────────────────────────────────────────
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
SPACY_MODEL = "fr_core_news_sm"

# ── Seuils de décision ────────────────────────────────────────────────────────
SCORE_RECEVABLE = 0.65       # score cosine >= 0.65 → recevable
SCORE_LIMITE    = 0.50       # 0.50–0.65 → à étudier

# ── Pondérations des sections ─────────────────────────────────────────────────
SECTION_WEIGHTS = {
    "competences": 0.35,
    "experience":  0.30,
    "formation":   0.20,
    "resume":      0.10,
    "langues":     0.05,
}

# ── Patterns de sections (regex) ─────────────────────────────────────────────
SECTION_PATTERNS = {
    "resume":      r"(résumé|profil|objectif|à propos|about|summary)",
    "experience":  r"(expérience|experience|emploi|poste|parcours professionnel|career)",
    "formation":   r"(formation|éducation|education|diplôme|études|scolarité|cursus)",
    "competences": r"(compétences?|skills?|technologies?|outils?|maîtrise|savoir.faire)",
    "langues":     r"(langues?|languages?|linguistique)",
    "projets":     r"(projets?|projects?|réalisations?)",
    "certifications": r"(certifications?|accréditations?|licences?)",
}

# ── Chemins ───────────────────────────────────────────────────────────────────
DATA_DIR        = BASE_DIR / "data"
MODELS_DIR      = BASE_DIR / "models"
SAMPLE_CVS_DIR  = DATA_DIR / "sample_cvs"
