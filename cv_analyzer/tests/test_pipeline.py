"""
tests/test_pipeline.py
Tests unitaires pour chaque module du pipeline.
Lancement : pytest tests/ -v
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


# ══════════════════════════════════════════════════════════════════════════════
# INGESTION
# ══════════════════════════════════════════════════════════════════════════════

class TestExtractor:
    def test_txt_bytes(self):
        from ingestion.extractor import extract_text
        data = "Bonjour, je suis développeur Python.".encode("utf-8")
        result = extract_text(data, filename="cv.txt")
        assert "Python" in result

    def test_txt_file(self, tmp_path):
        from ingestion.extractor import extract_text
        f = tmp_path / "cv.txt"
        f.write_text("CV de test — compétences Python, NLP", encoding="utf-8")
        result = extract_text(f)
        assert "Python" in result

    def test_unsupported_format(self):
        from ingestion.extractor import extract_text
        with pytest.raises(ValueError, match="non supporté"):
            extract_text(b"data", filename="cv.xlsx")

    def test_magic_pdf_detection(self):
        """Teste la détection par magic bytes (sans extension)."""
        from ingestion.extractor import _guess_type
        assert _guess_type(b"%PDF-1.4 content") == ".pdf"

    def test_magic_docx_detection(self):
        from ingestion.extractor import _guess_type
        assert _guess_type(b"PK\x03\x04 content") == ".docx"


# ══════════════════════════════════════════════════════════════════════════════
# PREPROCESSING — CLEANER
# ══════════════════════════════════════════════════════════════════════════════

class TestCleaner:
    def test_removes_control_chars(self):
        from preprocessing.cleaner import clean_text
        dirty = "Bonjour\x00\x07 le monde\x1b"
        result = clean_text(dirty)
        assert "\x00" not in result
        assert "\x07" not in result

    def test_normalizes_unicode(self):
        from preprocessing.cleaner import clean_text
        # NFD → NFC
        import unicodedata
        nfd = unicodedata.normalize("NFD", "éàü")
        result = clean_text(nfd)
        assert result == unicodedata.normalize("NFC", "éàü")

    def test_reduces_blank_lines(self):
        from preprocessing.cleaner import clean_text
        text = "ligne1\n\n\n\n\nligne2"
        result = clean_text(text)
        assert "\n\n\n" not in result

    def test_lowercase_option(self):
        from preprocessing.cleaner import clean_text
        result = clean_text("Python NLP", lowercase=True)
        assert result == "python nlp"

    def test_extract_email(self):
        from preprocessing.cleaner import extract_contact_info
        info = extract_contact_info("Contactez-moi à jean.dupont@example.com pour plus d'infos.")
        assert "jean.dupont@example.com" in info["emails"]

    def test_extract_phone(self):
        from preprocessing.cleaner import extract_contact_info
        info = extract_contact_info("Tél : +33 6 12 34 56 78")
        assert len(info["phones"]) > 0


# ══════════════════════════════════════════════════════════════════════════════
# PREPROCESSING — SEGMENTER
# ══════════════════════════════════════════════════════════════════════════════

class TestSegmenter:
    CV_SAMPLE = """
Jean Dupont — Développeur Python

Compétences
Python, FastAPI, PostgreSQL, Docker, NLP

Expérience professionnelle
2022-2024 : Data Engineer chez Acme Corp
Conception de pipelines de données ETL.

Formation
Master Informatique — Université Paris-Saclay (2022)
"""

    def test_detects_competences(self):
        from preprocessing.segmenter import segment_cv
        sections = segment_cv(self.CV_SAMPLE)
        assert "competences" in sections

    def test_detects_experience(self):
        from preprocessing.segmenter import segment_cv
        sections = segment_cv(self.CV_SAMPLE)
        assert "experience" in sections

    def test_detects_formation(self):
        from preprocessing.segmenter import segment_cv
        sections = segment_cv(self.CV_SAMPLE)
        assert "formation" in sections

    def test_no_section_fallback(self):
        from preprocessing.segmenter import segment_cv
        text = "Bonjour je suis développeur sans structure particulière."
        sections = segment_cv(text)
        # Doit retourner au moins une section
        assert len(sections) >= 1

    def test_content_not_empty(self):
        from preprocessing.segmenter import segment_cv
        sections = segment_cv(self.CV_SAMPLE)
        for name, content in sections.items():
            assert isinstance(content, str), f"Section {name} n'est pas une string"


# ══════════════════════════════════════════════════════════════════════════════
# PREPROCESSING — NER
# ══════════════════════════════════════════════════════════════════════════════

class TestNER:
    TEXT = """
Marie Curie travaille chez TechCorp à Paris depuis 2020.
Ses compétences incluent Python, Docker, TensorFlow et Kubernetes.
Elle a travaillé sur des projets de Machine Learning et NLP.
"""

    def test_tech_skills_extracted(self):
        from preprocessing.ner import extract_entities
        ents = extract_entities(self.TEXT)
        techs = [t.lower() for t in ents["skills_tech"]]
        assert "python" in techs
        assert "docker" in techs

    def test_returns_all_keys(self):
        from preprocessing.ner import extract_entities
        ents = extract_entities(self.TEXT)
        for key in ["persons", "organizations", "locations", "dates", "skills_tech"]:
            assert key in ents, f"Clé manquante : {key}"

    def test_no_duplicate_skills(self):
        from preprocessing.ner import extract_entities
        text = "Python Python Python Docker Docker"
        ents = extract_entities(text)
        techs = [t.lower() for t in ents["skills_tech"]]
        assert len(techs) == len(set(techs))


# ══════════════════════════════════════════════════════════════════════════════
# EMBEDDING
# ══════════════════════════════════════════════════════════════════════════════

class TestEncoder:
    def test_encode_single_string(self):
        from embedding.encoder import encode
        import numpy as np
        vec = encode("Bonjour le monde")
        assert isinstance(vec, np.ndarray)
        assert vec.ndim == 1
        assert vec.shape[0] > 0

    def test_encode_list(self):
        from embedding.encoder import encode
        import numpy as np
        vecs = encode(["texte 1", "texte 2", "texte 3"])
        assert vecs.shape[0] == 3

    def test_normalized_embeddings(self):
        """Les embeddings doivent être L2-normalisés (norme ≈ 1.0)."""
        from embedding.encoder import encode
        import numpy as np
        vec = encode("test de normalisation")
        norm = np.linalg.norm(vec)
        assert abs(norm - 1.0) < 1e-3, f"Norme attendue ≈ 1.0, obtenue {norm:.4f}"

    def test_similar_texts_close(self):
        """Deux textes similaires doivent avoir une similarité élevée."""
        from embedding.encoder import encode
        import numpy as np
        v1 = encode("Développeur Python spécialisé en NLP")
        v2 = encode("Ingénieur logiciel expert Python et traitement du langage")
        sim = float(np.dot(v1, v2))
        assert sim > 0.5, f"Similarité trop faible : {sim:.3f}"

    def test_different_texts_far(self):
        """Deux textes très différents doivent avoir une similarité faible."""
        from embedding.encoder import encode
        import numpy as np
        v1 = encode("Développeur Python NLP Machine Learning")
        v2 = encode("Plombier chauffagiste installation de tuyaux")
        sim = float(np.dot(v1, v2))
        assert sim < 0.7, f"Similarité trop haute pour des textes différents : {sim:.3f}"

    def test_encode_sections(self):
        from embedding.encoder import encode_sections
        sections = {"competences": "Python Docker", "experience": "5 ans chez Acme"}
        result = encode_sections(sections)
        assert "competences" in result
        assert "experience" in result


# ══════════════════════════════════════════════════════════════════════════════
# MATCHING — SCORER
# ══════════════════════════════════════════════════════════════════════════════

class TestScorer:
    CV_MATCHING = """
    Data Scientist — 5 ans d'expérience
    Compétences : Python, scikit-learn, TensorFlow, NLP, BERT, SQL, Docker
    Expérience : NLP engineer chez DataCorp. Développement de modèles de classification de texte.
    Formation : Master Data Science, Paris.
    """

    CV_NON_MATCHING = """
    Plombier — 10 ans d'expérience
    Compétences : Installation de tuyaux, soudure, chauffage, sanitaires.
    Expérience : Rénovation de salles de bain, dépannage urgence.
    Formation : CAP Plomberie.
    """

    JOB = """
    Nous recrutons un Data Scientist senior.
    Profil requis : expertise Python, NLP, Machine Learning, deep learning, BERT, scikit-learn.
    Minimum 3 ans d'expérience en traitement du langage naturel.
    """

    def test_matching_cv_higher_score(self):
        from matching.scorer import score_cv
        r_match = score_cv(self.CV_MATCHING, self.JOB)
        r_nomatch = score_cv(self.CV_NON_MATCHING, self.JOB)
        assert r_match.score_global > r_nomatch.score_global

    def test_matching_cv_recevable(self):
        from matching.scorer import score_cv
        result = score_cv(self.CV_MATCHING, self.JOB)
        assert result.verdict in ("recevable", "a_etudier"), \
            f"CV correspondant devrait être recevable/a_etudier, obtenu : {result.verdict}"

    def test_non_matching_cv_non_recevable(self):
        from matching.scorer import score_cv
        result = score_cv(self.CV_NON_MATCHING, self.JOB)
        assert result.verdict == "non_recevable", \
            f"CV non correspondant devrait être non_recevable, obtenu : {result.verdict}"

    def test_result_has_all_fields(self):
        from matching.scorer import score_cv
        result = score_cv(self.CV_MATCHING, self.JOB)
        assert hasattr(result, "score_global")
        assert hasattr(result, "score_pondere")
        assert hasattr(result, "verdict")
        assert hasattr(result, "explication")
        assert hasattr(result, "points_forts")
        assert hasattr(result, "manques")

    def test_score_in_range(self):
        from matching.scorer import score_cv
        result = score_cv(self.CV_MATCHING, self.JOB)
        assert 0.0 <= result.score_global <= 1.0
        assert 0.0 <= result.score_pondere <= 1.0

    def test_with_sections(self):
        from matching.scorer import score_cv
        sections = {
            "competences": "Python NLP Machine Learning BERT",
            "experience": "NLP engineer 5 ans",
            "formation": "Master Data Science",
        }
        result = score_cv(self.CV_MATCHING, self.JOB, cv_sections=sections)
        assert len(result.score_sections) == len(sections)
        for s in sections:
            assert s in result.score_sections

    def test_explication_contains_verdict(self):
        from matching.scorer import score_cv
        result = score_cv(self.CV_MATCHING, self.JOB)
        # L'explication doit mentionner un verdict lisible
        keywords = ["Recevable", "étudier", "Non recevable"]
        assert any(kw in result.explication for kw in keywords)


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE COMPLET
# ══════════════════════════════════════════════════════════════════════════════

class TestPipeline:
    CV_TEXT = b"""
Data Scientist - Jean Martin

Competences
Python, TensorFlow, PyTorch, NLP, BERT, scikit-learn, Docker, SQL

Experience
2021-2024 : NLP Engineer chez AI Solutions
  - Développement de modèles de classification de texte
  - Fine-tuning de modèles BERT pour la détection d'intentions
  - Mise en production avec FastAPI et Docker

Formation
Master Intelligence Artificielle - Université Paris-Saclay (2021)
"""

    JOB_TEXT = """
Nous recherchons un Data Scientist / NLP Engineer confirmé.
Compétences requises : Python, NLP, transformers, BERT, PyTorch ou TensorFlow.
Expérience minimum 2 ans sur des projets de traitement du langage naturel.
Bonne connaissance du déploiement de modèles (Docker, API REST).
"""

    def test_full_pipeline_returns_result(self):
        from utils.pipeline import analyze_cv
        result = analyze_cv(
            cv_source=self.CV_TEXT,
            job_description=self.JOB_TEXT,
            cv_filename="cv_test.txt",
            run_ner=False,  # NER désactivée pour accélérer le test
        )
        assert result is not None
        assert result.match is not None

    def test_pipeline_verdict_valid(self):
        from utils.pipeline import analyze_cv
        result = analyze_cv(
            cv_source=self.CV_TEXT,
            job_description=self.JOB_TEXT,
            cv_filename="cv_test.txt",
            run_ner=False,
        )
        assert result.match.verdict in ("recevable", "a_etudier", "non_recevable")

    def test_pipeline_sections_extracted(self):
        from utils.pipeline import analyze_cv
        result = analyze_cv(
            cv_source=self.CV_TEXT,
            job_description=self.JOB_TEXT,
            cv_filename="cv_test.txt",
            run_ner=False,
        )
        assert len(result.sections) > 0

    def test_pipeline_contact_info(self):
        from utils.pipeline import analyze_cv
        cv_with_email = self.CV_TEXT + b"\nContact : jean.martin@example.com"
        result = analyze_cv(
            cv_source=cv_with_email,
            job_description=self.JOB_TEXT,
            cv_filename="cv_test.txt",
            run_ner=False,
        )
        assert "jean.martin@example.com" in result.contact_info.get("emails", [])
