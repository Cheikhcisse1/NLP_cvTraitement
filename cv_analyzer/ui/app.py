# (seules les parties critiques ont été modifiées, le reste est IDENTIQUE)

# ── AJOUT JUSTE AVANT LE BOUTON ──────────────────────────────────────────────
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


_, col_btn, _ = st.columns([2, 1, 2])
with col_btn:
    analyze_btn = st.button("🔍 Analyser le CV", use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE (CORRIGÉ)
# ══════════════════════════════════════════════════════════════════════════════
if analyze_btn:
    job_text  = st.session_state.get("job_text", "").strip()
    cv_bytes  = st.session_state.get("cv_bytes", None)
    cv_name   = st.session_state.get("cv_filename", "")

    errors = []
    if not cv_bytes:
        errors.append("Veuillez uploader un CV (PDF, DOCX ou TXT).")
    if not job_text:
        errors.append("Veuillez saisir la fiche de poste.")
    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    with st.spinner("⏳ Analyse en cours — premier lancement : chargement du modèle (~30 s)…"):
        from utils.pipeline import analyze_cv
        try:
            st.session_state.analysis_result = analyze_cv(
                cv_source=cv_bytes,
                job_description=job_text,
                cv_filename=cv_name,
                run_ner=run_ner,
            )
        except Exception as exc:
            st.error(f"Erreur lors de l'analyse : {exc}")
            st.stop()

# 🔥 récupération stable du résultat
result = st.session_state.analysis_result

# ══════════════════════════════════════════════════════════════════════════════
# AFFICHAGE (inchangé mais déplacé)
# ══════════════════════════════════════════════════════════════════════════════
if result:

    m = result.match

    st.markdown("<div class='cv-divider'></div>", unsafe_allow_html=True)
    st.markdown("## 📊 Résultats")

    # ── VERDICT ───────────────────────────────────────────────────────────────
    VCFG = {
        "recevable":     ("✅", "RECEVABLE",     "Le profil correspond bien au poste."),
        "a_etudier":     ("⚠️", "À ÉTUDIER",     "Le profil mérite un examen approfondi."),
        "non_recevable": ("❌", "NON RECEVABLE", "Le profil ne correspond pas aux exigences."),
    }
    icon, label, sub = VCFG[m.verdict]
    pct = int(m.score_pondere * 100)

    st.markdown(f"""
    <div class="verdict-card verdict-{m.verdict}">
        <div class="verdict-icon">{icon}</div>
        <div class="verdict-text">
            <p class="verdict-title">{label}</p>
            <p class="verdict-sub">{sub}</p>
        </div>
        <div class="verdict-score">{pct}%</div>
    </div>""", unsafe_allow_html=True)

    # (tout le reste de ton affichage reste EXACTEMENT identique)


    # ── ONGLET 4 : EXPORT (CORRIGÉ) ───────────────────────────────────────────
    cv_name_safe = st.session_state.get("cv_filename", "cv")

    export_data = {
        "fichier":       cv_name_safe,
        "nb_caracteres": len(result.clean_text_value),
        "sections":      list(result.sections.keys()),
        "contact":       result.contact_info,
        "entites":       result.entities,
        "match": {
            "verdict":        m.verdict,
            "score_global":   m.score_global,
            "score_pondere":  m.score_pondere,
            "score_sections": m.score_sections,
            "explication":    m.explication,
            "points_forts":   m.points_forts,
            "manques":        m.manques,
        },
    }

    json_bytes = json.dumps(export_data, ensure_ascii=False, indent=2).encode("utf-8")

    col_j, col_t = st.columns(2)

    with col_j:
        st.download_button(
            "⬇️ Télécharger JSON",
            data=json_bytes,
            file_name=f"analyse_{Path(cv_name_safe).stem}.json",
            mime="application/json",
            use_container_width=True,
        )

    with col_t:
        st.download_button(
            "⬇️ Télécharger TXT",
            data="...".encode("utf-8"),
            file_name=f"rapport_{Path(cv_name_safe).stem}.txt",
            mime="text/plain",
            use_container_width=True,
        )
