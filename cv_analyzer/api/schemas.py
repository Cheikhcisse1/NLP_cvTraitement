"""
api/schemas.py
Schémas Pydantic pour les requêtes et réponses de l'API REST.
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class JobDescriptionBody(BaseModel):
    job_description: str = Field(
        ...,
        min_length=20,
        description="Texte de la fiche de poste (obligatoire)",
        examples=["Nous recherchons un data scientist expérimenté en Python et NLP."],
    )
    run_ner: bool = Field(
        default=True,
        description="Active l'extraction d'entités nommées (plus lent)",
    )


class SectionScore(BaseModel):
    name: str
    score: float
    label: str  # "fort" | "moyen" | "faible"


class MatchResponse(BaseModel):
    verdict: str           # "recevable" | "a_etudier" | "non_recevable"
    score_global: float
    score_pondere: float
    score_sections: dict[str, float]
    explication: str
    points_forts: list[str]
    manques: list[str]


class ContactInfo(BaseModel):
    emails: list[str]
    phones: list[str]
    urls:   list[str]


class EntitiesInfo(BaseModel):
    persons:       list[str]
    organizations: list[str]
    locations:     list[str]
    dates:         list[str]
    skills_tech:   list[str]


class AnalysisResponse(BaseModel):
    filename:     str
    nb_chars:     int
    sections_found: list[str]
    contact_info: ContactInfo
    entities:     EntitiesInfo
    match:        MatchResponse


class ErrorResponse(BaseModel):
    detail: str
