"""
matching/scorer.py
Calcule un score de correspondance entre un CV et une fiche de poste.
Deux modes :
  - score global (embedding CV entier vs fiche entière)
  - score pondéré par section
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Optional

from config import SCORE_RECEVABLE, SCORE_LIMITE, SECTION_WEIGHTS
from embedding.encoder import encode, encode_sections


@dataclass
class MatchResult:
    score_global: float                   # 0.0 – 1.0
    score_sections: dict[str, float]      # score par section
    score_pondere: float                  # moyenne pondérée
    verdict: str                          # "recevable" | "a_etudier" | "non_recevable"
    explication: str                      # phrase résumée
    manques: list[str]                    # sections faibles
    points_forts: list[str]               # sections fortes


def score_cv(
    cv_text: str,
    job_text: str,
    cv_sections: Optional[dict[str, str]] = None,
) -> MatchResult:
    """
    Calcule la correspondance entre un CV et une fiche de poste.

    Args:
        cv_text      : texte complet du CV
        job_text     : texte de la fiche de poste
        cv_sections  : sections segmentées du CV (optionnel)

    Returns:
        MatchResult avec tous les scores et le verdict
    """
    # ── 1. Score global ───────────────────────────────────────────────────────
    cv_emb  = encode(cv_text)
    job_emb = encode(job_text)
    score_global = float(_cosine(cv_emb, job_emb))

    # ── 2. Score par section ──────────────────────────────────────────────────
    score_sections: dict[str, float] = {}
    if cv_sections:
        for section_name, content in cv_sections.items():
            if content.strip():
                sec_emb = encode(content)
                score_sections[section_name] = float(_cosine(sec_emb, job_emb))

    # ── 3. Score pondéré ──────────────────────────────────────────────────────
    score_pondere = _weighted_score(score_sections) if score_sections else score_global

    # Score final = combinaison global + pondéré
    score_final = 0.4 * score_global + 0.6 * score_pondere if score_sections else score_global
    score_final = min(max(score_final, 0.0), 1.0)

    # ── 4. Verdict ────────────────────────────────────────────────────────────
    verdict = _verdict(score_final)

    # ── 5. Points forts / manques ─────────────────────────────────────────────
    points_forts, manques = _analyse_sections(score_sections)

    # ── 6. Explication textuelle ──────────────────────────────────────────────
    explication = _build_explanation(score_final, verdict, points_forts, manques)

    return MatchResult(
        score_global=round(score_global, 4),
        score_sections={k: round(v, 4) for k, v in score_sections.items()},
        score_pondere=round(score_pondere, 4),
        verdict=verdict,
        explication=explication,
        manques=manques,
        points_forts=points_forts,
    )


# ── Helpers ────────────────────────────────────────────────────────────────────

def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Similarité cosine entre deux vecteurs L2-normalisés → simple produit scalaire."""
    return float(np.dot(a, b))


def _weighted_score(section_scores: dict[str, float]) -> float:
    """Moyenne pondérée selon SECTION_WEIGHTS (config)."""
    total_w, total_s = 0.0, 0.0
    for section, score in section_scores.items():
        w = SECTION_WEIGHTS.get(section, 0.05)
        total_s += score * w
        total_w += w
    return (total_s / total_w) if total_w > 0 else 0.0


def _verdict(score: float) -> str:
    if score >= SCORE_RECEVABLE:
        return "recevable"
    elif score >= SCORE_LIMITE:
        return "a_etudier"
    else:
        return "non_recevable"


def _analyse_sections(section_scores: dict[str, float]) -> tuple[list[str], list[str]]:
    forts, faibles = [], []
    for section, score in section_scores.items():
        if score >= 0.60:
            forts.append(section)
        elif score < 0.45:
            faibles.append(section)
    return forts, faibles


def _build_explanation(score: float, verdict: str, forts: list[str], manques: list[str]) -> str:
    pct = int(score * 100)
    labels = {"recevable": "✅ Recevable", "a_etudier": "⚠️ À étudier", "non_recevable": "❌ Non recevable"}
    label = labels[verdict]

    parts = [f"{label} — score de correspondance : {pct}%."]

    if forts:
        parts.append(f"Points forts : {', '.join(forts)}.")
    if manques:
        parts.append(f"Sections insuffisantes : {', '.join(manques)}.")

    if verdict == "recevable":
        parts.append("Le profil correspond bien au poste proposé.")
    elif verdict == "a_etudier":
        parts.append("Le profil mérite un examen plus approfondi.")
    else:
        parts.append("Le profil ne correspond pas aux exigences du poste.")

    return " ".join(parts)
