"""
embedding/encoder.py
Encode du texte en vecteurs denses via sentence-transformers.
Utilise st.cache_resource quand Streamlit est disponible,
sinon lru_cache — compatible CLI, API et Streamlit Cloud.
"""
from __future__ import annotations

import numpy as np
from loguru import logger

from config import EMBEDDING_MODEL


def _get_model():
    from sentence_transformers import SentenceTransformer
    logger.info(f"Chargement du modèle d'embedding : {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    logger.info("Modèle prêt.")
    return model


def _get_model_cached():
    """
    Retourne le modèle avec le bon système de cache :
    - st.cache_resource si Streamlit tourne (évite le rechargement entre requêtes)
    - lru_cache sinon (CLI / API)
    """
    try:
        import streamlit as st

        # Enregistre la fonction cachée une seule fois
        if "_st_model_loader" not in st.session_state:
            @st.cache_resource(show_spinner="⏳ Chargement du modèle NLP…")
            def _loader():
                return _get_model()
            st.session_state["_st_model_loader"] = _loader

        return st.session_state["_st_model_loader"]()

    except Exception:
        # Hors Streamlit : fallback lru_cache
        from functools import lru_cache

        @lru_cache(maxsize=1)
        def _loader():
            return _get_model()

        return _loader()


def encode(texts: list[str] | str, batch_size: int = 32) -> np.ndarray:
    single = isinstance(texts, str)
    if single:
        texts = [texts]

    model = _get_model_cached()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    return embeddings[0] if single else embeddings


def encode_sections(sections: dict[str, str]) -> dict[str, np.ndarray]:
    result = {}
    for name, content in sections.items():
        if content.strip():
            result[name] = encode(content)
    return result
