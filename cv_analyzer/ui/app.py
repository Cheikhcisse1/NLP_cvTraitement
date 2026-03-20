"""
ui/app.py
Interface Streamlit complète — CV Analyzer NLP
Design : épuré, professionnel, dark sidebar
"""
from __future__ import annotations

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# ── Config page ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CV Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

[data-testid="stSidebar"] {
    background: #0f1117;
    border-right: 1px solid #1e2130;
}
[data-testid="stSidebar"] * { color: #c9d1e0 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #ffffff !important; }

.main { background: #f8f9fb; }

.cv-hero {
    background: linear-gradient(135deg, #1a1f36 0%, #2d3561 100%);
    color: white;
    padding: 2.5rem 2rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.cv-hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: rgba(99,102,241,0.15);
}
.cv-hero h1 { font-size: 2rem; font-weight: 600; margin: 0 0 .4rem; }
.cv-hero p  { font-size: 1rem; opacity: .75; margin: 0; }

.verdict-card {
    border-radius: 14px;
    padding: 1.6rem 2rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    margin-bottom: 1.5rem;
}
.verdict-recevable     { background: #ecfdf5; border: 2px solid #10b981; }
.verdict-a_etudier     { background: #fffbeb; border: 2px solid #f59e0b; }
.verdict-non_recevable { background: #fef2f2; border: 2px solid #ef4444; }

.verdict-icon  { font-size: 2.8rem; }
.verdict-text  { flex: 1; }
.verdict-title { font-size: 1.3rem; font-weight: 600; margin: 0 0 .2rem; }
.verdict-sub   { font-size: .9rem; opacity: .75; margin: 0; }
.verdict-recevable     .verdict-title { color: #065f46; }
.verdict-a_etudier     .verdict-title { color: #92400e; }
.verdict-non_recevable .verdict-title { color: #991b1b; }

.verdict-score { font-size: 2.6rem; font-weight: 700; font-family: 'DM Mono', monospace; }
.verdict-recevable     .verdict-score { color: #10b981; }
.verdict-a_etudier     .verdict-score { color: #f59e0b; }
.verdict-non_recevable .verdict-score { color: #ef4444; }

.metric-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    flex: 1;
    min-width: 140px;
    border: 1px solid #e8eaf0;
    box-shadow: 0 1px 4px rgba(0,0,0,.05);
}
.metric-label { font-size: .78rem; font-weight: 500; color: #6b7280; text-transform: uppercase; letter-spacing: .06em; margin-bottom: .3rem; }
.metric-value { font-size: 1.8rem; font-weight: 600; font-family: 'DM Mono', monospace; color: #1a1f36; }
.metric-unit  { font-size: 1rem; color: #6b7280; }

.tag-row { display: flex; flex-wrap: wrap; gap: .5rem; margin: .5rem 0 1rem; }
.tag       { background: #eef2ff; color: #4f46e5; font-size: .78rem; font-weight: 500; padding: .25rem .75rem; border-radius: 99px; }
.tag-skill { background: #f0fdf4; color: #16a34a; font-size: .78rem; padding: .25rem .75rem; border-radius: 99px; }
.tag-org   { background: #fdf4ff; color: #9333ea; font-size: .78rem; padding: .25rem .75rem; border-radius: 99px; }

.section-box {
    background: white;
    border: 1px solid #e8eaf0;
    border-left: 4px solid #6366f1;
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.2rem;
    margin-bottom: .8rem;
    font-size: .88rem;
    color: #374151;
    line-height: 1.6;
    font-family: 'DM Mono', monospace;
    white-space: pre-wrap;
}
.cv-divider { height: 1px; background: #e5e7eb; margin: 1.5rem 0; }

[data-testid="stFileUploader"] > div {
    border: 2px dashed #c7d2fe !important;
    border-radius: 12px !important;
    background: #f5f7ff !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: .5rem;
    background: transparent;
    border-bottom: 2px solid #e5e7eb;
}
.stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0 !important; font-weight: 500; color: #6b7280; }
.stTabs [aria-selected="true"] { background: white !important; color: #4f46e5 !important; border-bottom: 2px solid #4f46e5 !important; }

.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #6366f1) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
    padding: .65rem 1.5rem !important;
    transition: opacity .2s !important;
}
.stButton > button:hover { opacity: .88 !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")
    run_ner      = st.toggle("🧠 Extraction d'entités (NER)", value=True,
                             help="Active spaCy pour extraire noms, organisations, compétences.")
    show_sections = st.toggle("🗂 Afficher les sections",     value=True)
    show_raw      = st.toggle("📃 Texte brut extrait",        value=False)

    st.markdown("---")
    st.markdown("### 🎯 Seuils de décision")
    st.markdown("""
    <div style="font-size:.85rem;line-height:2.1">
    ✅ <b>Recevable</b> ≥ 65 %<br>
    ⚠️ <b>À étudier</b> 50 – 65 %<br>
    ❌ <b>Non recevable</b> &lt; 50 %
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📦 Stack")
    st.markdown("""
    <div style="font-size:.82rem;line-height:2;font-family:'DM Mono',monospace;color:#8892a4">
    sentence-transformers<br>spaCy fr_core_news_lg<br>pdfplumber · python-docx<br>FastAPI · Plotly
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="cv-hero">
    <h1>📄 CV Analyzer — NLP</h1>
    <p>Analyse automatique de la correspondance entre un CV et une fiche de poste<br>
    via sentence-transformers &amp; spaCy</p>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# INPUTS
# ══════════════════════════════════════════════════════════════════════════════
col_cv, col_job = st.columns([1, 1], gap="large")

with col_cv:
    st.markdown("### 1. 📎 Déposer le CV")
    uploaded_file = st.file_uploader(
        "PDF, DOCX ou TXT", type=["pdf", "docx", "doc", "txt"],
        label_visibility="collapsed",
        key="cv_uploader",
    )
    # Persiste les bytes du CV dans session_state pour survivre au re-run
    if uploaded_file is not None:
        st.session_state["cv_bytes"]    = uploaded_file.getvalue()
        st.session_state["cv_filename"] = uploaded_file.name
    if "cv_filename" in st.session_state:
        sz = len(st.session_state["cv_bytes"])
        st.caption(f"✔ `{st.session_state['cv_filename']}` — {sz/1024:.1f} Ko")

with col_job:
    st.markdown("### 2. 📋 Fiche de poste")
    if "job_text" not in st.session_state:
        st.session_state["job_text"] = ""
    job_text = st.text_area(
        "Fiche de poste", height=190,
        placeholder="Exemples : Nous recherchons un Data Scientist avec 3+ ans d'expérience en Python, NLP, transformers (BERT, CamemBERT), déploiement Docker…",
        label_visibility="collapsed",
        key="job_text",
    )
    if job_text:
        st.caption(f"✔ {len(job_text)} caractères saisis")

st.markdown("")
_, col_btn, _ = st.columns([2, 1, 2])
with col_btn:
    analyze_btn = st.button("🔍 Analyser le CV", use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE
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
        for e in errors: st.error(e)
        st.stop()

    with st.spinner("⏳ Analyse en cours — premier lancement : chargement du modèle (~30 s)…"):
        from utils.pipeline import analyze_cv
        try:
            result = analyze_cv(
                cv_source=cv_bytes,
                job_description=job_text,
                cv_filename=cv_name,
                run_ner=run_ner,
            )
        except Exception as exc:
            st.error(f"Erreur lors de l'analyse : {exc}")
            st.stop()

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

    # ── MÉTRIQUES ─────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-label">Score global</div>
            <div class="metric-value">{m.score_global*100:.1f}<span class="metric-unit">%</span></div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Score pondéré</div>
            <div class="metric-value">{m.score_pondere*100:.1f}<span class="metric-unit">%</span></div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Sections</div>
            <div class="metric-value">{len(result.sections)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Compétences tech.</div>
            <div class="metric-value">{len(result.entities.get('skills_tech', []))}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Longueur CV</div>
            <div class="metric-value">{len(result.clean_text_value)}<span class="metric-unit"> car.</span></div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLETS
    # ══════════════════════════════════════════════════════════════════════════
    tab_scores, tab_ner, tab_sections, tab_export = st.tabs([
        "📈 Scores & Graphiques",
        "🧠 Entités & Compétences",
        "🗂 Sections du CV",
        "📥 Export",
    ])

    # ── ONGLET 1 : SCORES ─────────────────────────────────────────────────────
    with tab_scores:
        if m.score_sections:
            col_radar, col_bar = st.columns([1, 1], gap="large")

            with col_radar:
                st.markdown("#### Radar — correspondance par section")
                cats   = list(m.score_sections.keys())
                values = [round(v * 100, 1) for v in m.score_sections.values()]
                cats_r   = cats + [cats[0]]
                values_r = values + [values[0]]

                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=values_r, theta=cats_r, fill="toself",
                    fillcolor="rgba(99,102,241,0.18)",
                    line=dict(color="#6366f1", width=2),
                    marker=dict(color="#6366f1", size=7),
                    name="Score",
                ))
                fig_radar.add_trace(go.Scatterpolar(
                    r=[65]*len(cats_r), theta=cats_r, mode="lines",
                    line=dict(color="#10b981", width=1.5, dash="dot"),
                    name="Seuil 65%",
                ))
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100],
                                        tickfont=dict(size=10), gridcolor="#e5e7eb"),
                        angularaxis=dict(tickfont=dict(size=11)),
                        bgcolor="white",
                    ),
                    showlegend=True,
                    legend=dict(font=dict(size=11)),
                    margin=dict(t=30, b=30, l=50, r=50),
                    height=340,
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_radar, use_container_width=True)

            with col_bar:
                st.markdown("#### Score par section")
                colors = [
                    "#10b981" if v >= 60 else ("#f59e0b" if v >= 45 else "#ef4444")
                    for v in values
                ]
                fig_bar = go.Figure(go.Bar(
                    x=values, y=[c.capitalize() for c in cats],
                    orientation="h", marker_color=colors,
                    text=[f"{v:.1f}%" for v in values],
                    textposition="outside",
                    textfont=dict(size=12, family="DM Mono"),
                ))
                fig_bar.add_vline(x=65, line_color="#10b981", line_dash="dot",
                                  annotation_text="Seuil", annotation_position="top")
                fig_bar.add_vline(x=50, line_color="#f59e0b", line_dash="dot",
                                  annotation_text="Limite", annotation_position="top")
                fig_bar.update_layout(
                    xaxis=dict(range=[0, 110], showgrid=True, gridcolor="#f0f0f0",
                               title="Score (%)", ticksuffix="%"),
                    yaxis=dict(autorange="reversed"),
                    plot_bgcolor="white",
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=30, b=30, l=10, r=60),
                    height=340, showlegend=False,
                )
                st.plotly_chart(fig_bar, use_container_width=True)

        # Points forts / manques
        col_f, col_m = st.columns(2)
        with col_f:
            if m.points_forts:
                st.success("**✔ Points forts**\n\n" + "\n".join(f"• {p.capitalize()}" for p in m.points_forts))
            else:
                st.info("Aucun point fort clairement identifié.")
        with col_m:
            if m.manques:
                st.warning("**✘ Sections insuffisantes**\n\n" + "\n".join(f"• {p.capitalize()}" for p in m.manques))
            else:
                st.success("Toutes les sections évaluées sont satisfaisantes.")

        st.markdown("---")
        st.markdown(f"**💬 Analyse :** {m.explication}")

        # Jauge globale
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=round(m.score_pondere * 100, 1),
            title=dict(text="Score pondéré global", font=dict(size=14)),
            number=dict(suffix="%", font=dict(size=32, family="DM Mono")),
            delta=dict(reference=65, suffix="%",
                       increasing=dict(color="#10b981"),
                       decreasing=dict(color="#ef4444")),
            gauge=dict(
                axis=dict(range=[0, 100], tickwidth=1, tickcolor="#e5e7eb"),
                bar=dict(color="#6366f1"),
                bgcolor="white",
                borderwidth=1, bordercolor="#e5e7eb",
                steps=[
                    dict(range=[0,  50], color="#fef2f2"),
                    dict(range=[50, 65], color="#fffbeb"),
                    dict(range=[65,100], color="#ecfdf5"),
                ],
                threshold=dict(line=dict(color="#6366f1", width=3),
                               thickness=.75, value=65),
            ),
        ))
        fig_gauge.update_layout(
            height=260,
            margin=dict(t=40, b=20, l=40, r=40),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    # ── ONGLET 2 : NER ────────────────────────────────────────────────────────
    with tab_ner:
        ent = result.entities
        c   = result.contact_info

        if any([c.get("emails"), c.get("phones"), c.get("urls")]):
            st.markdown("#### 📬 Coordonnées")
            col_e, col_p, col_u = st.columns(3)
            with col_e:
                if c.get("emails"):
                    st.markdown("**Email**")
                    for e in c["emails"]: st.code(e)
            with col_p:
                if c.get("phones"):
                    st.markdown("**Téléphone**")
                    for p in c["phones"]: st.code(p)
            with col_u:
                if c.get("urls"):
                    st.markdown("**URLs**")
                    for u in c["urls"][:3]: st.code(u)

        if not run_ner or not ent:
            st.info("NER désactivée. Activez-la dans la sidebar pour extraire les entités.")
        else:
            if ent.get("skills_tech"):
                st.markdown("#### 🛠️ Compétences techniques détectées")
                tags_html = "".join(f'<span class="tag-skill">{s}</span>'
                                    for s in sorted(ent["skills_tech"]))
                st.markdown(f'<div class="tag-row">{tags_html}</div>', unsafe_allow_html=True)

                skills = sorted(ent["skills_tech"])[:18]
                if len(skills) >= 3:
                    fig_sk = go.Figure(go.Bar(
                        y=skills, x=[1]*len(skills), orientation="h",
                        marker_color=px.colors.qualitative.Set3[:len(skills)],
                        text=skills, textposition="inside",
                        textfont=dict(size=11),
                    ))
                    fig_sk.update_layout(
                        showlegend=False,
                        xaxis=dict(visible=False),
                        yaxis=dict(visible=False),
                        plot_bgcolor="white",
                        paper_bgcolor="rgba(0,0,0,0)",
                        margin=dict(t=10, b=10, l=10, r=10),
                        height=max(30 * len(skills) + 40, 150),
                    )
                    st.plotly_chart(fig_sk, use_container_width=True)

            col_orgs, col_locs = st.columns(2)
            with col_orgs:
                if ent.get("organizations"):
                    st.markdown("#### 🏢 Organisations")
                    html = "".join(f'<span class="tag-org">{o}</span>'
                                   for o in ent["organizations"][:12])
                    st.markdown(f'<div class="tag-row">{html}</div>', unsafe_allow_html=True)
            with col_locs:
                if ent.get("locations"):
                    st.markdown("#### 📍 Lieux")
                    html = "".join(f'<span class="tag">{l}</span>'
                                   for l in ent["locations"][:10])
                    st.markdown(f'<div class="tag-row">{html}</div>', unsafe_allow_html=True)

            if ent.get("dates"):
                st.markdown("#### 📅 Dates / périodes")
                html = "".join(f'<span class="tag">{d}</span>' for d in ent["dates"][:15])
                st.markdown(f'<div class="tag-row">{html}</div>', unsafe_allow_html=True)

    # ── ONGLET 3 : SECTIONS ───────────────────────────────────────────────────
    with tab_sections:
        if not show_sections:
            st.info("Activez 'Afficher les sections' dans la sidebar.")
        elif not result.sections:
            st.warning("Aucune section détectée dans ce CV.")
        else:
            st.markdown(f"**{len(result.sections)} section(s) détectée(s)**")
            sec_tags = "".join(f'<span class="tag">{s.capitalize()}</span>'
                               for s in result.sections)
            st.markdown(f'<div class="tag-row">{sec_tags}</div>', unsafe_allow_html=True)

            for name, content in result.sections.items():
                score_str = ""
                if name in m.score_sections:
                    sc = m.score_sections[name] * 100
                    color = "#10b981" if sc >= 60 else ("#f59e0b" if sc >= 45 else "#ef4444")
                    score_str = f' <span style="color:{color};font-weight:600;font-size:.85rem">({sc:.1f}%)</span>'
                with st.expander(f"**{name.capitalize()}**  —  {len(content)} car."):
                    st.markdown(
                        f'<div class="section-box">{content[:1200]}{"…" if len(content) > 1200 else ""}</div>',
                        unsafe_allow_html=True,
                    )

        if show_raw:
            st.markdown("---")
            st.markdown("#### 📃 Texte brut nettoyé")
            st.text_area("", result.clean_text_value[:4000], height=250,
                         label_visibility="collapsed")

    # ── ONGLET 4 : EXPORT ─────────────────────────────────────────────────────
    with tab_export:
        st.markdown("#### 📥 Exporter le rapport")

        export_data = {
            "fichier":       uploaded_file.name,
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

        # Rapport texte
        VLABELS = {"recevable": "✅ RECEVABLE", "a_etudier": "⚠️  À ÉTUDIER",
                   "non_recevable": "❌ NON RECEVABLE"}
        lines = [
            "═" * 60,
            "  RAPPORT D'ANALYSE — CV ANALYZER NLP",
            "═" * 60,
            f"  Fichier    : {uploaded_file.name}",
            f"  Longueur   : {len(result.clean_text_value)} caractères",
            "",
            f"  VERDICT    : {VLABELS[m.verdict]}",
            f"  Score global   : {m.score_global*100:.1f}%",
            f"  Score pondéré  : {m.score_pondere*100:.1f}%",
            "",
            "  Scores par section :",
        ]
        for sec, sc in m.score_sections.items():
            bar = "█" * int(sc * 20) + "░" * (20 - int(sc * 20))
            lines.append(f"    {sec:<15} {bar} {sc*100:.1f}%")
        lines += ["", f"  Analyse : {m.explication}", ""]
        if m.points_forts:
            lines.append(f"  Points forts : {', '.join(m.points_forts)}")
        if m.manques:
            lines.append(f"  Manques      : {', '.join(m.manques)}")
        if result.entities.get("skills_tech"):
            lines.append(f"  Compétences  : {', '.join(sorted(result.entities['skills_tech'])[:15])}")
        lines.append("═" * 60)
        txt_report = "\n".join(lines)

        col_j, col_t = st.columns(2)
        with col_j:
            st.download_button(
                "⬇️ Télécharger JSON", data=json_bytes,
                file_name=f"analyse_{Path(uploaded_file.name).stem}.json",
                mime="application/json", use_container_width=True,
            )
        with col_t:
            st.download_button(
                "⬇️ Télécharger TXT", data=txt_report.encode("utf-8"),
                file_name=f"rapport_{Path(uploaded_file.name).stem}.txt",
                mime="text/plain", use_container_width=True,
            )

        st.markdown("---")
        st.markdown("**Aperçu du rapport**")
        st.code(txt_report, language=None)
