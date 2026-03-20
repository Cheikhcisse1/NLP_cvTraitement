"""
api/main.py
API REST FastAPI — expose le pipeline d'analyse de CV.

Endpoints :
  POST /analyze   — upload d'un CV + fiche de poste → verdict
  GET  /health    — santé de l'API
  GET  /docs      — Swagger UI (automatique)
"""
from __future__ import annotations

import sys
from pathlib import Path

# Permet d'importer les modules du projet depuis n'importe où
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from api.schemas import AnalysisResponse, ContactInfo, EntitiesInfo, MatchResponse, ErrorResponse
from utils.pipeline import analyze_cv


# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="CV Analyzer API",
    description="Analyse de CV par NLP (sentence-transformers + spaCy). "
                "Retourne un verdict recevable / à étudier / non recevable.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Infra"])
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    tags=["Analyse"],
    summary="Analyser un CV par rapport à une fiche de poste",
)
async def analyze(
    cv_file: UploadFile = File(..., description="Fichier CV (PDF, DOCX ou TXT)"),
    job_description: str = Form(..., description="Texte de la fiche de poste"),
    run_ner: bool = Form(default=True, description="Active la NER spaCy"),
):
    """
    Upload un CV et une fiche de poste.
    Retourne le verdict + les scores de correspondance.
    """
    allowed = {".pdf", ".docx", ".doc", ".txt", ".md"}
    suffix = Path(cv_file.filename or "").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(400, f"Format non supporté : {suffix}. Formats acceptés : {allowed}")

    if not job_description.strip():
        raise HTTPException(400, "La fiche de poste est vide.")

    try:
        data = await cv_file.read()
        result = analyze_cv(
            cv_source=data,
            job_description=job_description,
            cv_filename=cv_file.filename or "",
            run_ner=run_ner,
        )
    except Exception as e:
        logger.exception(f"Erreur pipeline : {e}")
        raise HTTPException(500, f"Erreur lors de l'analyse : {str(e)}")

    m = result.match

    return AnalysisResponse(
        filename=cv_file.filename or "inconnu",
        nb_chars=len(result.clean_text_value),
        sections_found=list(result.sections.keys()),
        contact_info=ContactInfo(**result.contact_info),
        entities=EntitiesInfo(**result.entities) if result.entities else EntitiesInfo(
            persons=[], organizations=[], locations=[], dates=[], skills_tech=[]
        ),
        match=MatchResponse(
            verdict=m.verdict,
            score_global=m.score_global,
            score_pondere=m.score_pondere,
            score_sections=m.score_sections,
            explication=m.explication,
            points_forts=m.points_forts,
            manques=m.manques,
        ),
    )


# ── Lancement direct ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
