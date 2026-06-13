import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()
load_env()

from agents import orchestrator, gene_agent, literature_agent, pathway_agent, hypothesis_agent, experiment_agent, report_agent
from utils.export_utils import build_markdown_report, build_txt_report
from config.settings import APP_TITLE, APP_SUBTITLE, APP_BADGE

st.set_page_config(page_title="BioPilot AI", page_icon="🧬", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
*, html, body { font-family: 'Inter', sans-serif; }
.stApp { background: #060b14; color: #e2e8f0; }
.hero { text-align:center; padding: 2rem 0 1rem; }
.badge {
    display:inline-block; background:rgba(0,212,255,0.08);
    border:1px solid rgba(0,212,255,0.25); color:#00d4ff;
    font-size:.7rem; font-weight:700; letter-spacing:2px;
    text-transform:uppercase; padding:4px 16px; border-radius:20px; margin-bottom:.8rem;
}
.title {
    font-size:3rem; font-weight:800;
    background:linear-gradient(135deg,#00d4ff,#a78bfa,#f472b6);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    line-height:1.1; margin-bottom:.4rem;
}
.subtitle { color:#64748b; font-size:1.05rem; }
.agent-card {
    background:linear-gradient(135deg,#0d1420,#111827);
    border:1px solid #1e293b; border-radius:14px;
    padding:1.4rem 1.6rem; margin-bottom:1rem; position:relative; overflow:hidden;
}
.agent-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg,#00d4ff,#a78bfa);
}
.agent-tag {
    font-size:.68rem; font-weight:700; letter-spacing:2px;
    text-transform:uppercase; color:#00d4ff; margin-bottom:.6rem;
}
.step-row {
    display:flex; align-items:center; gap:12px;
    padding:.5rem .8rem; border-radius:8px; margin-bottom:.3rem;
}
.step-done { background:rgba(0,212,255,0.06); }
.step-active { background:rgba(167,139,250,0.08); }
.step-wait { opacity:.35; }
.step-icon { font-size:1.1rem; width:24px; }
.step-name { font-size:.83rem; font-weight:600; color:#94a3b8; }
.stButton>button {
    background:linear-gradient(135deg,#00d4ff,#7c3aed) !important;
    color:white !important; border:none !important; border-radius:10px !important;
    font-weight:700 !important; font-size:.95rem !important; width:100% !important;
}
section[data-testid="stSidebar"] { background:#090e18 !important; border-right:1px solid #1e293b !important; }
.stTextInput input, .stTextArea textarea {
    background:#0d1420 !important; border:1px solid #1e293b !important;
    color:#e2e8f0 !important; border-radius:8px !important;
}
hr { border-color:#1e293b !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🧬 BioPilot AI")
    st.markdown("---")
    env_key = os.environ.get("GROQ_API_KEY", "")
    if env_key:
        st.success("✅ Groq API Key loaded")
        api_key = env_key
    else:
        api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    st.markdown("---")
    st.markdown("#### 📖 How to use")
    st.markdown("1. Enter gene + disease\n2. Click **Run BioPilot**\n3. Watch 7 agents collaborate\n4. Download full report")
    st.markdown("---")
    st.markdown("#### 🤖 Agent Pipeline")
    for icon, name in [("🧠","Orchestrator"),("🔬","Gene Intelligence"),("📚","Literature"),("🌐","Pathway & Network"),("💡","Hypothesis"),("🧪","Experiment Design"),("📝","Report Generator")]:
        st.markdown(f"{icon} **{name}**")
    st.markdown("---")
    st.markdown("#### ⚡ Quick Examples")
    ex1 = st.button("MALAT1 + LUAD", use_container_width=True)
    ex2 = st.button("TP53 + Breast Cancer", use_container_width=True)
    ex3 = st.button("EGFR + Lung Cancer", use_container_width=True)
    st.markdown("---")
    st.caption("Built with GitHub Copilot · Powered by Groq + Llama3")

st.markdown(f"""
<div class="hero">
  <div class="badge">{APP_BADGE}</div>
  <div class="title">🧬 {APP_TITLE}</div>
  <div class="subtitle">{APP_SUBTITLE}</div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

default_gene, default_disease = "", ""
if ex1: default_gene, default_disease = "MALAT1", "Lung Adenocarcinoma"
if ex2: default_gene, default_disease = "TP53", "Breast Cancer"
if ex3: default_gene, default_disease = "EGFR", "Lung Cancer"

st.markdown("### 🔍 Research Query")
c1, c2 = st.columns(2)
with c1:
    gene = st.text_input("Gene / lncRNA / Protein", value=default_gene, placeholder="e.g. MALAT1, BRCA1, TP53")
with c2:
    disease = st.text_input("Disease / Condition", value=default_disease, placeholder="e.g. Lung Adenocarcinoma")

custom = st.text_area("Custom Research Question (optional)",
    placeholder="e.g. I discovered MALAT1 upregulated in TCGA-LUAD. Help me design a complete study.",
    height=80)

st.markdown("")
run_btn = st.button("🚀 Run BioPilot Analysis — Activate All Agents", use_container_width=True)

PIPELINE = [
    ("orchestrator", "🧠", "Research Orchestrator",  orchestrator),
    ("gene",         "🔬", "Gene Intelligence Agent", gene_agent),
    ("literature",   "📚", "Literature Intelligence", literature_agent),
    ("pathway",      "🌐", "Pathway & Network Agent", pathway_agent),
    ("hypothesis",   "💡", "Hypothesis Generator",    hypothesis_agent),
    ("experiment",   "🧪", "Experimental Design",     experiment_agent),
    ("report",       "📝", "Scientific Report",       report_agent),
]

if run_btn:
    if not api_key:
        st.error("⚠️ No API key found. Add GROQ_API_KEY to .env file.")
        st.stop()
    if not gene:
        st.error("⚠️ Please enter a gene name.")
        st.stop()

    st.markdown("---")
    st.markdown(f"### 📋 Research Report: *{gene} in {disease}*")

    results = {}
    literature_out = ""

    progress_col, report_col = st.columns([1, 2])

    with progress_col:
        st.markdown("#### ⚡ Agent Pipeline")
        step_placeholders = {}
        for key, icon, name, _ in PIPELINE:
            step_placeholders[key] = st.empty()
            step_placeholders[key].markdown(
                f'<div class="step-row step-wait"><span class="step-icon">{icon}</span><span class="step-name">{name}</span></div>',
                unsafe_allow_html=True)

    with report_col:
        st.markdown("#### 🧬 Agent Outputs")
        card_placeholders = {}
        for key, icon, name, _ in PIPELINE:
            card_placeholders[key] = st.empty()

    for key, icon, name, module in PIPELINE:
        step_placeholders[key].markdown(
            f'<div class="step-row step-active"><span class="step-icon">⏳</span><span class="step-name">{name} — analyzing...</span></div>',
            unsafe_allow_html=True)

        if key == "orchestrator":
            out = module.run(api_key, gene, disease, custom)
        elif key == "hypothesis":
            out = module.run(api_key, gene, disease, literature_out)
        elif key == "report":
            ctx = "\n".join(list(results.values())[:3])
            out = module.run(api_key, gene, disease, ctx)
        else:
            out = module.run(api_key, gene, disease)

        if key == "literature":
            literature_out = out

        results[key] = out

        step_placeholders[key].markdown(
            f'<div class="step-row step-done"><span class="step-icon">✅</span><span class="step-name">{name}</span></div>',
            unsafe_allow_html=True)

        with card_placeholders[key].container():
            with st.expander(f"{icon} {name}", expanded=(key in ["orchestrator","hypothesis","report"])):
                st.markdown(out)

    st.success("✅ BioPilot Analysis Complete!")
    st.balloons()

    st.markdown("---")
    st.markdown("### 📥 Download Report")
    dc1, dc2 = st.columns(2)
    with dc1:
        st.download_button("📄 Download Markdown",
            data=build_markdown_report(gene, disease, results),
            file_name=f"BioPilot_{gene}_{disease}.md",
            mime="text/markdown", use_container_width=True)
    with dc2:
        st.download_button("📃 Download Text",
            data=build_txt_report(gene, disease, results),
            file_name=f"BioPilot_{gene}_{disease}.txt",
            mime="text/plain", use_container_width=True)