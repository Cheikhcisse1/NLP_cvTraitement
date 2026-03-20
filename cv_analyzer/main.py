"""
main.py
Point d'entrée CLI pour tester le pipeline rapidement sans l'UI.

Usage :
    python main.py --cv data/sample_cvs/cv_data_scientist.txt \
                   --job data/sample_cvs/job_data_scientist.txt

    python main.py --cv mon_cv.pdf \
                   --job "Nous recrutons un data scientist Python NLP..."
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from loguru import logger

# Configure loguru : niveau INFO par défaut
logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyse un CV par rapport à une fiche de poste",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--cv",  required=True, help="Chemin vers le CV (PDF, DOCX, TXT)")
    parser.add_argument("--job", required=True, help="Chemin vers la fiche de poste (TXT) ou texte direct")
    parser.add_argument("--no-ner", action="store_true", help="Désactive la NER spaCy (plus rapide)")
    parser.add_argument("--json", action="store_true", help="Affiche le résultat en JSON")
    args = parser.parse_args()

    # Lecture de la fiche de poste (fichier ou texte direct)
    job_path = Path(args.job)
    if job_path.exists():
        job_text = job_path.read_text(encoding="utf-8")
    else:
        job_text = args.job  # texte passé directement

    # Pipeline
    from utils.pipeline import analyze_cv

    result = analyze_cv(
        cv_source=Path(args.cv),
        job_description=job_text,
        run_ner=not args.no_ner,
    )

    m = result.match

    if args.json:
        output = {
            "verdict":        m.verdict,
            "score_global":   m.score_global,
            "score_pondere":  m.score_pondere,
            "score_sections": m.score_sections,
            "explication":    m.explication,
            "points_forts":   m.points_forts,
            "manques":        m.manques,
            "sections":       list(result.sections.keys()),
            "contact":        result.contact_info,
            "entities":       result.entities,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    # Affichage lisible
    ICONS = {"recevable": "✅", "a_etudier": "⚠️ ", "non_recevable": "❌"}
    icon = ICONS.get(m.verdict, "?")

    print("\n" + "═" * 60)
    print(f"  {icon}  VERDICT : {m.verdict.upper().replace('_', ' ')}")
    print("═" * 60)
    print(f"  Score global    : {m.score_global * 100:.1f}%")
    print(f"  Score pondéré   : {m.score_pondere * 100:.1f}%")
    print()

    if m.score_sections:
        print("  Scores par section :")
        for section, score in m.score_sections.items():
            bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
            print(f"    {section:<15} {bar} {score * 100:.1f}%")
    print()

    print(f"  💬 {m.explication}")

    if m.points_forts:
        print(f"\n  ✔  Points forts : {', '.join(m.points_forts)}")
    if m.manques:
        print(f"  ✘  Manques      : {', '.join(m.manques)}")

    if result.entities.get("skills_tech"):
        skills = ", ".join(sorted(result.entities["skills_tech"])[:15])
        print(f"\n  🛠  Compétences détectées : {skills}")

    if result.contact_info.get("emails"):
        print(f"  📧 Email : {result.contact_info['emails'][0]}")

    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
