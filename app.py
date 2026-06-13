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

st.set_page_config(page_title="BioPilot AI", page_icon="🧬", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }

/* ── Force dark everywhere ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
[data-testid="stMain"],
.main, .block-container,
[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
.stApp { background-color: #060b14 !important; color: #e2e8f0 !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu { visibility: hidden !important; }
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
footer { display: none !important; }
[data-testid="collapsedControl"] { background: #090e18 !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #090e18 !important;
    border-right: 1px solid #1e293b !important;
}
section[data-testid="stSidebar"] * { color: #94a3b8 !important; }
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 { color: #e2e8f0 !important; }

/* ── Hero ── */
.hero { text-align:center; padding: 1.8rem 0 1rem; }
.badge {
    display:inline-block; background:rgba(0,212,255,0.08);
    border:1px solid rgba(0,212,255,0.25); color:#00d4ff;
    font-size:.68rem; font-weight:700; letter-spacing:2px;
    text-transform:uppercase; padding:4px 16px; border-radius:20px; margin-bottom:.8rem;
}
.title {
    font-size:2.8rem; font-weight:800;
    background:linear-gradient(135deg,#00d4ff,#a78bfa,#f472b6);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    line-height:1.1; margin-bottom:.4rem;
}
.subtitle { color:#475569; font-size:1rem; }

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
    background:#0d1420 !important; border:1px solid #1e293b !important;
    color:#e2e8f0 !important; border-radius:8px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color:#00d4ff !important;
    box-shadow:0 0 0 2px rgba(0,212,255,.12) !important;
}
.stTextInput label, .stTextArea label { color:#64748b !important; font-size:.78rem !important; }

/* ── Selectbox ── */
.stSelectbox > div > div {
    background:#0d1420 !important; border:1px solid #1e293b !important;
    color:#e2e8f0 !important; border-radius:8px !important;
}

/* ── Quick example buttons — subtle style ── */
.stButton > button {
    background: #0d1420 !important;
    border: 1px solid #1e293b !important;
    color: #94a3b8 !important;
    border-radius: 8px !important;
    font-size: .82rem !important;
    font-weight: 500 !important;
    width: 100% !important;
    text-align: left !important;
    padding: .4rem .8rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    border-color: #00d4ff !important;
    color: #00d4ff !important;
    background: rgba(0,212,255,0.05) !important;
}

/* ── Run button override ── */
.run-btn > button {
    background: linear-gradient(135deg,#00d4ff,#7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: .95rem !important;
    padding: .7rem !important;
}

/* ── Agent diagram nodes ── */
.node {
    display:flex; align-items:center; gap:10px;
    padding:.45rem .8rem; border-radius:8px; margin-bottom:.25rem;
    border: 1px solid #1e293b;
}
.node-wait { background:#0a0f1a; opacity:0.45; }
.node-active { background:rgba(167,139,250,0.08); border-color:#a78bfa !important; opacity:1; }
.node-done { background:rgba(0,212,255,0.05); border-color:rgba(0,212,255,0.3) !important; opacity:1; }
.node-icon { font-size:.95rem; width:18px; }
.node-name { font-size:.75rem; font-weight:600; color:#64748b; }
.node-done .node-name { color:#00d4ff; }
.node-active .node-name { color:#a78bfa; }
.connector { width:1px; height:10px; background:#1e293b; margin:0 auto 0 2rem; }

/* ── Expander ── */
details { background:#0d1420 !important; border:1px solid #1e293b !important; border-radius:8px !important; }
summary { color:#94a3b8 !important; }

/* ── Diagram wrap ── */
.diagram-wrap {
    background:#0d1420; border:1px solid #1e293b;
    border-radius:12px; padding:1rem; margin-bottom:.8rem;
}
.diagram-label {
    font-size:.62rem; font-weight:700; letter-spacing:2px;
    text-transform:uppercase; color:#334155; text-align:center; margin-bottom:.8rem;
}

hr { border-color:#1e293b !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
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

    # ── Settings in expander ──
    with st.expander("⚙️ Settings", expanded=False):
        output_style = st.selectbox("Output Style", ["Detailed", "Concise", "Academic", "Clinical"], index=0)
        focus_area = st.selectbox("Research Focus", [
            "Biomarker Discovery", "Therapeutic Target",
            "Mechanistic Study", "Clinical Translation",
            "Drug Resistance", "Immunotherapy"
        ], index=0)
        hypothesis_count = st.slider("Number of Hypotheses", 1, 5, 3)
        include_timeline = st.checkbox("Include Research Timeline", value=True)
        include_journal = st.checkbox("Suggest Publication Journals", value=True)

    st.markdown("---")
    st.markdown("#### 📖 How to use")
    st.markdown("1. Enter gene + disease\n2. Adjust settings if needed\n3. Click **Run BioPilot**\n4. Watch 7 agents collaborate\n5. Download full report")

    st.markdown("---")
    st.markdown("#### ⚡ Quick Examples")
    ex1 = st.button("🧬 MALAT1 + LUAD", use_container_width=True)
    ex2 = st.button("🔬 TP53 + Breast Cancer", use_container_width=True)
    ex3 = st.button("💊 EGFR + Lung Cancer", use_container_width=True)
    ex4 = st.button("🦠 BRCA1 + Ovarian Cancer", use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🤖 Agent Pipeline")
    for icon, name in [("🧠","Orchestrator"),("🔬","Gene Intelligence"),
                       ("📚","Literature"),("🌐","Pathway & Network"),
                       ("💡","Hypothesis"),("🧪","Experiment"),("📝","Report")]:
        st.markdown(f"<span style='color:#334155'>{icon} {name}</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Built with GitHub Copilot · Powered by Groq + Llama3")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div class="badge">{APP_BADGE}</div>
  <div class="title">🧬 {APP_TITLE}</div>
  <div class="subtitle">{APP_SUBTITLE}</div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Quick example fill ────────────────────────────────────────────────────────
default_gene, default_disease = "", ""
if ex1: default_gene, default_disease = "MALAT1", "Lung Adenocarcinoma"
if ex2: default_gene, default_disease = "TP53", "Breast Cancer"
if ex3: default_gene, default_disease = "EGFR", "Lung Cancer"
if ex4: default_gene, default_disease = "BRCA1", "Ovarian Cancer"

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown("### 🔍 Research Query")
c1, c2 = st.columns(2)
with c1:
    gene = st.text_input("Gene / lncRNA / Protein", value=default_gene,
                         placeholder="e.g. MALAT1, BRCA1, TP53, HOTAIR")
with c2:
    disease = st.text_input("Disease / Condition", value=default_disease,
                            placeholder="e.g. Lung Adenocarcinoma, Breast Cancer")

custom = st.text_area("Custom Research Question (optional)",
    placeholder="e.g. I discovered MALAT1 upregulated in TCGA-LUAD. Help me design a complete study.",
    height=80)

st.markdown("")

# Run button with special class
st.markdown('<div class="run-btn">', unsafe_allow_html=True)
run_btn = st.button("🚀 Run BioPilot Analysis — Activate All Agents", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Pipeline ──────────────────────────────────────────────────────────────────
PIPELINE = [
    ("orchestrator", "🧠", "Research Orchestrator",  orchestrator),
    ("gene",         "🔬", "Gene Intelligence",       gene_agent),
    ("literature",   "📚", "Literature Intelligence", literature_agent),
    ("pathway",      "🌐", "Pathway & Network",       pathway_agent),
    ("hypothesis",   "💡", "Hypothesis Generator",    hypothesis_agent),
    ("experiment",   "🧪", "Experimental Design",     experiment_agent),
    ("report",       "📝", "Scientific Report",       report_agent),
]

def render_diagram(statuses):
    html = '<div class="diagram-wrap"><div class="diagram-label">⚡ Live Agent Pipeline</div>'
    for i, (key, icon, name, _) in enumerate(PIPELINE):
        s = statuses.get(key, "wait")
        si = "✅" if s=="done" else ("⏳" if s=="active" else icon)
        html += f'<div class="node node-{s}"><span class="node-icon">{si}</span><span class="node-name">{name}</span></div>'
        if i < len(PIPELINE)-1:
            html += '<div class="connector"></div>'
    html += '</div>'
    return html

if run_btn:
    if not api_key:
        st.error("⚠️ No API key found.")
        st.stop()
    if not gene:
        st.error("⚠️ Please enter a gene name.")
        st.stop()

    st.markdown("---")
    st.markdown(f"### 📋 Research Report: *{gene} in {disease}*")

    results = {}
    literature_out = ""
    statuses = {k: "wait" for k,*_ in PIPELINE}

    left_col, right_col = st.columns([1, 2])

    with left_col:
        diagram_ph = st.empty()
        # Architecture SVG
        st.markdown("""
<div style="background:#0d1420;border:1px solid #1e293b;border-radius:12px;padding:1rem;margin-top:.8rem;">
<div style="font-size:.6rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#334155;text-align:center;margin-bottom:.6rem;">🏗️ System Architecture</div>
<svg viewBox="0 0 200 330" xmlns="http://www.w3.org/2000/svg" style="width:100%">
  <defs>
    <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#00d4ff;stop-opacity:0.9"/>
      <stop offset="100%" style="stop-color:#a78bfa;stop-opacity:0.9"/>
    </linearGradient>
    <linearGradient id="g2" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#f472b6;stop-opacity:0.9"/>
      <stop offset="100%" style="stop-color:#a78bfa;stop-opacity:0.9"/>
    </linearGradient>
  </defs>
  <rect x="65" y="5" width="70" height="22" rx="6" fill="url(#g1)"/>
  <text x="100" y="20" text-anchor="middle" fill="white" font-size="8" font-weight="bold">👤 USER INPUT</text>
  <line x1="100" y1="27" x2="100" y2="40" stroke="#1e293b" stroke-width="1.5"/>
  <polygon points="100,43 96,38 104,38" fill="#00d4ff"/>
  <rect x="50" y="43" width="100" height="22" rx="6" fill="#0d1420" stroke="#00d4ff" stroke-width="1"/>
  <text x="100" y="58" text-anchor="middle" fill="#00d4ff" font-size="7.5" font-weight="bold">🧠 Orchestrator</text>
  <line x1="100" y1="65" x2="100" y2="75" stroke="#1e293b" stroke-width="1"/>
  <line x1="35" y1="75" x2="165" y2="75" stroke="#1e293b" stroke-width="1"/>
  <line x1="35" y1="75" x2="35" y2="85" stroke="#1e293b" stroke-width="1"/>
  <line x1="100" y1="75" x2="100" y2="85" stroke="#1e293b" stroke-width="1"/>
  <line x1="165" y1="75" x2="165" y2="85" stroke="#1e293b" stroke-width="1"/>
  <rect x="5" y="85" width="60" height="20" rx="5" fill="#0d1420" stroke="#a78bfa" stroke-width="1"/>
  <text x="35" y="98" text-anchor="middle" fill="#a78bfa" font-size="6">🔬 Gene</text>
  <rect x="70" y="85" width="60" height="20" rx="5" fill="#0d1420" stroke="#a78bfa" stroke-width="1"/>
  <text x="100" y="98" text-anchor="middle" fill="#a78bfa" font-size="6">📚 Literature</text>
  <rect x="135" y="85" width="60" height="20" rx="5" fill="#0d1420" stroke="#a78bfa" stroke-width="1"/>
  <text x="165" y="98" text-anchor="middle" fill="#a78bfa" font-size="6">🌐 Pathway</text>
  <line x1="35" y1="105" x2="35" y2="115" stroke="#1e293b" stroke-width="1"/>
  <line x1="100" y1="105" x2="100" y2="115" stroke="#1e293b" stroke-width="1"/>
  <line x1="165" y1="105" x2="165" y2="115" stroke="#1e293b" stroke-width="1"/>
  <line x1="35" y1="115" x2="165" y2="115" stroke="#1e293b" stroke-width="1"/>
  <line x1="100" y1="115" x2="100" y2="125" stroke="#00d4ff" stroke-width="1.5"/>
  <polygon points="100,128 96,123 104,123" fill="#00d4ff"/>
  <rect x="50" y="128" width="100" height="20" rx="5" fill="#0d1420" stroke="#f472b6" stroke-width="1"/>
  <text x="100" y="141" text-anchor="middle" fill="#f472b6" font-size="7">💡 Hypothesis</text>
  <line x1="100" y1="148" x2="100" y2="158" stroke="#f472b6" stroke-width="1.5"/>
  <polygon points="100,161 96,156 104,156" fill="#f472b6"/>
  <rect x="50" y="161" width="100" height="20" rx="5" fill="#0d1420" stroke="#f472b6" stroke-width="1"/>
  <text x="100" y="174" text-anchor="middle" fill="#f472b6" font-size="7">🧪 Experiment</text>
  <line x1="100" y1="181" x2="100" y2="191" stroke="#00d4ff" stroke-width="1.5"/>
  <polygon points="100,194 96,189 104,189" fill="#00d4ff"/>
  <rect x="50" y="194" width="100" height="20" rx="5" fill="#0d1420" stroke="#00d4ff" stroke-width="1"/>
  <text x="100" y="207" text-anchor="middle" fill="#00d4ff" font-size="7">📝 Report Generator</text>
  <line x1="100" y1="214" x2="100" y2="224" stroke="#00d4ff" stroke-width="1.5"/>
  <polygon points="100,227 96,222 104,222" fill="#00d4ff"/>
  <rect x="35" y="227" width="130" height="22" rx="6" fill="url(#g1)"/>
  <text x="100" y="242" text-anchor="middle" fill="white" font-size="7.5" font-weight="bold">📄 Research Proposal</text>
</svg>
</div>
""", unsafe_allow_html=True)

    with right_col:
        st.markdown("#### 🧬 Agent Outputs")
        card_phs = {key: st.empty() for key,*_ in PIPELINE}

    for key, icon, name, module in PIPELINE:
        statuses[key] = "active"
        diagram_ph.markdown(render_diagram(statuses), unsafe_allow_html=True)

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
        statuses[key] = "done"
        diagram_ph.markdown(render_diagram(statuses), unsafe_allow_html=True)

        with card_phs[key].container():
            with st.expander(f"{icon} {name}", expanded=(key in ["orchestrator","hypothesis","report"])):
                st.markdown(out)

    st.success("✅ BioPilot Analysis Complete!")
    st.balloons()

    st.markdown("---")
    st.markdown("### 📥 Download Full Report")
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