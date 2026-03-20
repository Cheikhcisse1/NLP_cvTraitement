"""
preprocessing/segmenter.py
Segmente un CV en sections nommées (expérience, formation, compétences…).
Utilise des patterns regex pour détecter les titres de sections.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from config import SECTION_PATTERNS


@dataclass
class CVSection:
    name: str
    raw_title: str
    content: str
    char_start: int
    char_end: int


def segment_cv(text: str) -> dict[str, str]:
    """
    Retourne un dict {nom_section: texte_contenu}.
    Les sections non détectées sont regroupées sous "autre".
    """
    sections: dict[str, str] = {}
    boundaries = _find_boundaries(text)

    if not boundaries:
        # Aucune section détectée → tout sous "resume"
        return {"resume": text}

    for i, (start, label, title) in enumerate(boundaries):
        end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(text)
        content = text[start + len(title):end].strip()
        # Fusionne si la même section apparaît plusieurs fois
        if label in sections:
            sections[label] += "\n" + content
        else:
            sections[label] = content

    return sections


def _find_boundaries(text: str) -> list[tuple[int, str, str]]:
    """
    Trouve les positions des titres de sections dans le texte.
    Renvoie une liste triée de (position, label, titre_brut).
    """
    compiled = {
        label: re.compile(pattern, re.IGNORECASE | re.UNICODE)
        for label, pattern in SECTION_PATTERNS.items()
    }

    hits: list[tuple[int, str, str]] = []
    # Parcourt chaque ligne pour trouver les titres
    for match in re.finditer(r"^(.{1,60})$", text, re.MULTILINE):
        line = match.group(1).strip()
        if not line:
            continue
        for label, pattern in compiled.items():
            if pattern.search(line):
                hits.append((match.start(), label, line))
                break  # une ligne = une section

    # Supprime les doublons proches (< 20 chars d'écart)
    hits.sort(key=lambda x: x[0])
    filtered: list[tuple[int, str, str]] = []
    prev_pos = -100
    for h in hits:
        if h[0] - prev_pos > 20:
            filtered.append(h)
            prev_pos = h[0]

    return filtered
