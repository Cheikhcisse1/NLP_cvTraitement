"""
preprocessing/cleaner.py
Nettoyage du texte brut extrait : normalisation Unicode, suppression
des artefacts PDF, mise en minuscules optionnelle.
"""
from __future__ import annotations

import re
import unicodedata


_MULTI_SPACE = re.compile(r"[ \t]{2,}")
_MULTI_NL    = re.compile(r"\n{3,}")
_URL         = re.compile(r"https?://\S+|www\.\S+")
_EMAIL       = re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}")
_PHONE       = re.compile(r"(\+?\d[\d\s\-().]{7,}\d)")


def clean_text(text: str, lowercase: bool = False) -> str:
    """
    Nettoie le texte brut :
    - Normalise Unicode (NFD → NFC)
    - Supprime les caractères de contrôle
    - Réduit les espaces/sauts de ligne excessifs
    """
    # Normalisation Unicode
    text = unicodedata.normalize("NFC", text)

    # Supprime les caractères de contrôle sauf \n et \t
    text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C"
                   or ch in "\n\t")

    # Remplace les tabulations par des espaces
    text = text.replace("\t", " ")

    # Réduit les espaces multiples
    text = _MULTI_SPACE.sub(" ", text)

    # Réduit les sauts de ligne multiples
    text = _MULTI_NL.sub("\n\n", text)

    # Trim global
    text = text.strip()

    if lowercase:
        text = text.lower()

    return text


def extract_contact_info(text: str) -> dict:
    """
    Extrait les infos de contact (email, téléphone, URLs).
    Renvoie un dict sans modifier le texte original.
    """
    emails = _EMAIL.findall(text)
    phones = _PHONE.findall(text)
    urls   = _URL.findall(text)
    return {
        "emails": list(set(emails)),
        "phones": list(set(phones)),
        "urls":   list(set(urls)),
    }
