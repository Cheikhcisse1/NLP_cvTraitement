from __future__ import annotations

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# ── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(page_title="CV Analyzer", page_icon="📄", layout="wide")

# ── SESSION STATE ────────────────────────────────────────────────────────────
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "cv_bytes" not in st.session_state:
    st.session_state.cv_bytes = None

if "cv_filename" not in st.session_state:
    st.session_state.cv_filename = ""

if "job_text" not in st.session_state:
    st.session_state.job_text = ""

# ── UI ───────────────────────────────────────────────────────────────────────
st.title("📄 CV Analyzer NLP")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload CV", type=["pdf", "docx", "txt"])
    if uploaded_file:
        st.session_state.cv_bytes = uploaded_file.getvalue()
        st.session_state.cv_filename = uploaded_file.name

with col2:
    job_text = st.text_area("Fiche de poste", key="job_text")

analyze_btn = st.button("🔍 Analyser")

# ── PIPELINE ─────────────────────────────────────────────────────────────────
if analyze_btn:
    if not st.session_state.cv_bytes or not st.session_state.job_text:
        st.error("CV + fiche de poste requis")
        st.stop()

    with st.spinner("Analyse en cours..."):
        from utils.pipeline import analyze_cv

        try:
            st.session_state.analysis_result = analyze_cv(
                cv_source=st.session_state.cv_bytes,
                job_description=st.session_state.job_text,
                cv_filename=st.session_state.cv_filename,
                run_ner=True,
            )
        except Exception as e:
            st.error(f"Erreur : {e}")
            st.stop()

# ── AFFICHAGE ────────────────────────────────────────────────────────────────
result = st.session_state.analysis_result

if result:

    m = result.match

    # ── VERDICT ──────────────────────────────────────────────────────────────
    with st.container():
        st.markdown(f"""
        <div style="padding:20px;border-radius:10px;background:#eef;">
            <h3>{m.verdict.upper()} — {int(m.score_pondere*100)}%</h3>
            <p>{m.explication}</p>
        </div>
        """, unsafe_allow_html=True)

    # ── GRAPHIQUE ────────────────────────────────────────────────────────────
    if m.score_sections:
        cats = list(m.score_sections.keys())
        vals = [v * 100 for v in m.score_sections.values()]

        fig = go.Figure(go.Bar(x=vals, y=cats, orientation="h"))

        st.plotly_chart(fig, use_container_width=True, key="bar_chart")

    # ── SKILLS ───────────────────────────────────────────────────────────────
    skills = result.entities.get("skills_tech", [])
    if skills:
        with st.container():
            tags = " ".join([f"<span style='padding:5px;background:#dfd;border-radius:5px'>{s}</span>" for s in skills])
            st.markdown(tags, unsafe_allow_html=True)

    # ── SECTIONS ─────────────────────────────────────────────────────────────
    for name, content in result.sections.items():
        exp = st.expander(name)
        with exp:
            st.write(content[:1000])

    # ── EXPORT ───────────────────────────────────────────────────────────────
    cv_name = st.session_state.cv_filename or "cv"

    data = {
        "verdict": m.verdict,
        "score": m.score_pondere,
        "skills": skills,
    }

    json_bytes = json.dumps(data).encode()

    st.download_button(
        "⬇️ Télécharger JSON",
        data=json_bytes,
        file_name=f"{cv_name}.json",
    )
