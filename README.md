# CV Analyzer — NLP Pipeline

Analyse automatique de CV par rapport à une fiche de poste.
Retourne un verdict **Recevable / À étudier / Non recevable** avec des scores de correspondance.

## Architecture

```
cv_analyzer/
├── ingestion/          # Extraction de texte (PDF, DOCX, TXT)
│   └── extractor.py
├── preprocessing/      # Nettoyage, segmentation, NER
│   ├── cleaner.py
│   ├── segmenter.py
│   └── ner.py
├── embedding/          # Vectorisation avec sentence-transformers
│   └── encoder.py
├── matching/           # Scoring cosine + verdict
│   └── scorer.py
├── utils/              # Orchestration du pipeline
│   └── pipeline.py
├── api/                # API REST FastAPI
│   ├── main.py
│   └── schemas.py
├── ui/                 # Interface Streamlit
│   └── app.py
├── tests/              # Tests unitaires pytest
│   └── test_pipeline.py
├── data/sample_cvs/    # CV et offres d'emploi exemples
├── main.py             # CLI
├── config.py           # Configuration centrale
└── requirements.txt
```

## Installation

```bash
# 1. Cloner / créer le dossier
cd cv_analyzer

# 2. Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Télécharger le modèle spaCy français
python -m spacy download fr_core_news_lg
```

> **Note** : Le modèle sentence-transformers (~420 Mo) se télécharge
> automatiquement au premier lancement.

## Utilisation

### CLI (le plus rapide pour tester)

```bash
# CV correspondant
python main.py \
  --cv data/sample_cvs/cv_data_scientist.txt \
  --job data/sample_cvs/job_data_scientist.txt

# CV non correspondant
python main.py \
  --cv data/sample_cvs/cv_non_matching.txt \
  --job data/sample_cvs/job_data_scientist.txt

# Sortie JSON
python main.py --cv mon_cv.pdf --job offre.txt --json

# Sans NER (plus rapide)
python main.py --cv mon_cv.pdf --job offre.txt --no-ner
```

### Interface Streamlit

```bash
streamlit run ui/app.py
# Ouvre http://localhost:8501
```

### API REST (FastAPI)

```bash
uvicorn api.main:app --reload
# Ouvre http://localhost:8000/docs pour le Swagger UI
```

#### Exemple de requête curl

```bash
curl -X POST http://localhost:8000/analyze \
  -F "cv_file=@mon_cv.pdf" \
  -F "job_description=Nous recrutons un Data Scientist Python NLP..." \
  -F "run_ner=true"
```

#### Exemple de réponse

```json
{
  "filename": "mon_cv.pdf",
  "nb_chars": 2847,
  "sections_found": ["competences", "experience", "formation"],
  "contact_info": {
    "emails": ["jean.dupont@email.com"],
    "phones": ["+33 6 12 34 56 78"],
    "urls": []
  },
  "entities": {
    "persons": ["Jean Dupont"],
    "organizations": ["Université Paris-Saclay"],
    "locations": ["Paris"],
    "dates": ["2022", "2024"],
    "skills_tech": ["python", "bert", "docker", "fastapi"]
  },
  "match": {
    "verdict": "recevable",
    "score_global": 0.7823,
    "score_pondere": 0.7541,
    "score_sections": {
      "competences": 0.8102,
      "experience": 0.7234,
      "formation": 0.6841
    },
    "explication": "✅ Recevable — score de correspondance : 75%. Points forts : competences, experience.",
    "points_forts": ["competences", "experience"],
    "manques": []
  }
}
```

### Tests unitaires

```bash
# Tous les tests
pytest tests/ -v

# Tests rapides (sans NER, sans modèle lourd)
pytest tests/ -v -k "not TestPipeline"

# Avec rapport de couverture
pytest tests/ --cov=. --cov-report=html
```

## Pipeline détaillé

```
Fichier CV (PDF/DOCX/TXT)
        │
        ▼
[1. Ingestion]  ──  pdfplumber / python-docx
        │            Extraction texte brut
        ▼
[2. Nettoyage]  ──  Normalisation Unicode
        │            Suppression artefacts
        │            Extraction contacts
        ▼
[3. Segmentation] ─  Détection sections par regex
        │            (compétences, expérience, formation…)
        ▼
[4. NER]        ──  spaCy fr_core_news_lg
        │            Personnes, orgs, dates
        │          + regex compétences techniques
        ▼
[5. Embedding]  ──  sentence-transformers
        │            paraphrase-multilingual-mpnet-base-v2
        │            Vecteurs L2-normalisés
        ▼
[6. Scoring]    ──  Similarité cosine
        │            Score global + pondéré par section
        │            Verdict + explication
        ▼
    Résultat JSON / UI / API
```

## Configuration (`config.py`)

| Paramètre | Valeur par défaut | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `paraphrase-multilingual-mpnet-base-v2` | Modèle sentence-transformers |
| `SPACY_MODEL` | `fr_core_news_lg` | Modèle spaCy |
| `SCORE_RECEVABLE` | `0.65` | Seuil recevable |
| `SCORE_LIMITE` | `0.50` | Seuil à étudier |
| `SECTION_WEIGHTS` | voir config | Pondérations par section |

## Évolutions possibles

- **Fine-tuning supervisé** : entraîner un classificateur binaire sur des CV labelisés
- **Batch mode** : traiter un dossier entier de CV vs une offre
- **Base de données** : stocker les résultats dans PostgreSQL
- **Auth API** : ajouter JWT sur l'endpoint `/analyze`
- **Modèle plus puissant** : remplacer par CamemBERT ou un LLM local (Mistral)
