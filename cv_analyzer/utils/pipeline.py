"""
utils/pipeline.py
Orchestre le pipeline complet : extraction → preprocessing → embedding → scoring.
C'est la fonction principale appelée par l'API et l'UI.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Union

from loguru import logger

from ingestion.extractor import extract_text
from preprocessing.cleaner import clean_text, extract_contact_info
from preprocessing.segmenter import segment_cv
from preprocessing.ner import extract_entities
from matching.scorer import score_cv, MatchResult


@dataclass
class CVAnalysisResult:
    # Infos brutes
    raw_text: str
    clean_text_value: str
    # Preprocessing
    sections: dict[str, str]
    contact_info: dict
    entities: dict
    # Scoring
    match: MatchResult


def analyze_cv(
    cv_source: Union[str, Path, bytes],
    job_description: str,
    cv_filename: str = "",
    run_ner: bool = True,
) -> CVAnalysisResult:
    """
    Pipeline complet d'analyse d'un CV par rapport à une fiche de poste.

    Args:
        cv_source       : chemin, bytes ou Path du fichier CV
        job_description : texte libre de la fiche de poste
        cv_filename     : nom du fichier (pour détecter le type si bytes)
        run_ner         : active l'extraction d'entités (peut être lent)

    Returns:
        CVAnalysisResult avec toutes les informations extraites et le score
    """
    # ── Étape 1 : Extraction ─────────────────────────────────────────────────
    logger.info("Étape 1/4 — Extraction du texte")
    raw = extract_text(cv_source, filename=cv_filename)

    # ── Étape 2 : Nettoyage ──────────────────────────────────────────────────
    logger.info("Étape 2/4 — Nettoyage")
    cleaned  = clean_text(raw)
    contacts = extract_contact_info(raw)

    # ── Étape 3 : Preprocessing ──────────────────────────────────────────────
    logger.info("Étape 3/4 — Segmentation + NER")
    sections = segment_cv(cleaned)
    entities = extract_entities(cleaned) if run_ner else {}

    # ── Étape 4 : Scoring ────────────────────────────────────────────────────
    logger.info("Étape 4/4 — Scoring")
    job_clean = clean_text(job_description)
    match     = score_cv(cleaned, job_clean, cv_sections=sections)

    logger.success(f"Analyse terminée — verdict={match.verdict} | score={match.score_pondere:.3f}")

    return CVAnalysisResult(
        raw_text=raw,
        clean_text_value=cleaned,
        sections=sections,
        contact_info=contacts,
        entities=entities,
        match=match,
    )
