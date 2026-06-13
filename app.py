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

# Force dark theme always
st.markdown("""
<style>
/* ── Force dark mode ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"],
.main, .block-container { background-color: #060b14 !important; color: #e2e8f0 !important; }

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }

/* ── Hero ── */
.hero { text-align:center; padding: 1.5rem 0 1rem; }
.badge {
    display:inline-block; background:rgba(0,212,255,0.08);
    border:1px solid rgba(0,212,255,0.25); color:#00d4ff;
    font-size:.7rem; font-weight:700; letter-spacing:2px;
    text-transform:uppercase; padding:4px 16px; border-radius:20px; margin-bottom:.8rem;
}
.title {
    font-size:2.8rem; font-weight:800;
    background:linear-gradient(135deg,#00d4ff,#a78bfa,#f472b6);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    line-height:1.1; margin-bottom:.4rem;
}
.subtitle { color:#64748b; font-size:1rem; }

/* ── Agent diagram ── */
.diagram-wrap {
    background: linear-gradient(135deg, #0d1420, #111827);
    border: 1px solid #1e293b; border-radius: 14px;
    padding: 1.2rem; margin-bottom: 1rem;
}
.diagram-title {
    font-size:.7rem; font-weight:700; letter-spacing:2px;
    text-transform:uppercase; color:#00d4ff; margin-bottom:1rem; text-align:center;
}
.node {
    display:flex; align-items:center; gap:10px;
    padding:.5rem .8rem; border-radius:8px; margin-bottom:.3rem;
    border: 1px solid #1e293b; transition: all 0.3s;
}
.node-wait { background:#0d1420; opacity:0.4; }
.node-active { background:rgba(167,139,250,0.1); border-color:#a78bfa !important; opacity:1; }
.node-done { background:rgba(0,212,255,0.06); border-color:#00d4ff !important; opacity:1; }
.node-icon { font-size:1rem; width:20px; }
.node-name { font-size:.78rem; font-weight:600; color:#94a3b8; }
.node-done .node-name { color:#00d4ff; }
.node-active .node-name { color:#a78bfa; }
.connector {
    width:2px; height:12px; background:linear-gradient(#1e293b,#00d4ff22);
    margin: 0 auto 0 1.8rem;
}

/* ── Agent output cards ── */
.agent-card {
    background:linear-gradient(135deg,#0d1420,#111827);
    border:1px solid #1e293b; border-radius:14px;
    padding:1.4rem 1.6rem; margin-bottom:1rem;
    position:relative; overflow:hidden;
}
.agent-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg,#00d4ff,#a78bfa);
}
.agent-tag {
    font-size:.65rem; font-weight:700; letter-spacing:2px;
    text-transform:uppercase; color:#00d4ff; margin-bottom:.5rem;
}

/* ── Settings panel ── */
.settings-card {
    background:#0d1420; border:1px solid #1e293b;
    border-radius:10px; padding:1rem; margin-top:.5rem;
}
.settings-title {
    font-size:.68rem; font-weight:700; letter-spacing:2px;
    text-transform:uppercase; color:#64748b; margin-bottom:.8rem;
}

/* ── Buttons ── */
.stButton>button {
    background:linear-gradient(135deg,#00d4ff,#7c3aed) !important;
    color:white !important; border:none !important; border-radius:10px !important;
    font-weight:700 !important; font-size:.92rem !important; width:100% !important;
}
.stButton>button:hover { opacity:0.85 !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background:#090e18 !important;
    border-right:1px solid #1e293b !important;
}
section[data-testid="stSidebar"] * { color:#94a3b8 !important; }
section[data-testid="stSidebar"] .stSuccess { color:#00d4ff !important; }

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background:#0d1420 !important; border:1px solid #1e293b !important;
    color:#e2e8f0 !important; border-radius:8px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color:#00d4ff !important;
    box-shadow:0 0 0 2px rgba(0,212,255,.12) !important;
}
label { color:#94a3b8 !important; font-size:.8rem !important; }
hr { border-color:#1e293b !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background:#0d1420 !important; border:1px solid #1e293b !important;
    border-radius:8px !important; color:#e2e8f0 !important;
}
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

    # ── Settings ──
    st.markdown("#### ⚙️ Settings")
    output_style = st.selectbox("Output Style", ["Detailed", "Concise", "Academic"], index=0)
    focus_area = st.selectbox("Research Focus", ["Biomarker Discovery", "Therapeutic Target", "Mechanistic Study", "Clinical Translation"], index=0)

    st.markdown("---")
    st.markdown("#### 📖 How to use")
    st.markdown("1. Enter gene + disease\n2. Click **Run BioPilot**\n3. Watch 7 agents collaborate\n4. Download full report")

    st.markdown("---")
    st.markdown("#### ⚡ Quick Examples")
    ex1 = st.button("🧬 MALAT1 + LUAD", use_container_width=True)
    ex2 = st.button("🔬 TP53 + Breast Cancer", use_container_width=True)
    ex3 = st.button("💊 EGFR + Lung Cancer", use_container_width=True)
    ex4 = st.button("🦠 BRCA1 + Ovarian Cancer", use_container_width=True)

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
run_btn = st.button("🚀 Run BioPilot Analysis — Activate All Agents", use_container_width=True)

# ── Pipeline definition ───────────────────────────────────────────────────────
PIPELINE = [
    ("orchestrator", "🧠", "Research Orchestrator",  orchestrator),
    ("gene",         "🔬", "Gene Intelligence",       gene_agent),
    ("literature",   "📚", "Literature Intelligence", literature_agent),
    ("pathway",      "🌐", "Pathway & Network",       pathway_agent),
    ("hypothesis",   "💡", "Hypothesis Generator",    hypothesis_agent),
    ("experiment",   "🧪", "Experimental Design",     experiment_agent),
    ("report",       "📝", "Scientific Report",       report_agent),
]

def render_diagram(statuses: dict):
    """Render the agent pipeline diagram with live status."""
    html = '<div class="diagram-wrap"><div class="diagram-title">⚡ Agent Pipeline</div>'
    for i, (key, icon, name, _) in enumerate(PIPELINE):
        status = statuses.get(key, "wait")
        css = f"node node-{status}"
        status_icon = "✅" if status == "done" else ("⏳" if status == "active" else icon)
        html += f'<div class="{css}"><span class="node-icon">{status_icon}</span><span class="node-name">{name}</span></div>'
        if i < len(PIPELINE) - 1:
            html += '<div class="connector"></div>'
    html += '</div>'
    return html

# ── Run ───────────────────────────────────────────────────────────────────────
if run_btn:
    if not api_key:
        st.error("⚠️ No API key found. Add GROQ_API_KEY to .env or paste in sidebar.")
        st.stop()
    if not gene:
        st.error("⚠️ Please enter a gene name.")
        st.stop()

    query = custom if custom else f"{gene} in {disease}"

    st.markdown("---")
    st.markdown(f"### 📋 Research Report: *{gene} in {disease}*")

    results = {}
    literature_out = ""
    statuses = {key: "wait" for key, *_ in PIPELINE}

    left_col, right_col = st.columns([1, 2])

    with left_col:
        diagram_placeholder = st.empty()
        # Architecture SVG
        st.markdown("""
<div style="background:linear-gradient(135deg,#0d1420,#111827);border:1px solid #1e293b;
border-radius:14px;padding:1.2rem;margin-top:1rem;">
<div style="font-size:.68rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;
color:#64748b;margin-bottom:.8rem;text-align:center;">🏗️ System Architecture</div>
<svg viewBox="0 0 200 320" xmlns="http://www.w3.org/2000/svg" style="width:100%">
  <defs>
    <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#00d4ff"/>
      <stop offset="100%" style="stop-color:#a78bfa"/>
    </linearGradient>
  </defs>
  <!-- User -->
  <rect x="70" y="5" width="60" height="22" rx="6" fill="url(#g1)" opacity="0.9"/>
  <text x="100" y="20" text-anchor="middle" fill="white" font-size="8" font-weight="bold">👤 USER</text>
  <!-- Arrow down -->
  <line x1="100" y1="27" x2="100" y2="42" stroke="#00d4ff" stroke-width="1.5"/>
  <polygon points="100,45 96,40 104,40" fill="#00d4ff"/>
  <!-- Orchestrator -->
  <rect x="55" y="45" width="90" height="22" rx="6" fill="#1e293b" stroke="#00d4ff" stroke-width="1"/>
  <text x="100" y="60" text-anchor="middle" fill="#00d4ff" font-size="7.5" font-weight="bold">🧠 Orchestrator</text>
  <!-- Three branches -->
  <line x1="100" y1="67" x2="100" y2="77" stroke="#1e293b" stroke-width="1"/>
  <line x1="40" y1="77" x2="160" y2="77" stroke="#1e293b" stroke-width="1"/>
  <line x1="40" y1="77" x2="40" y2="87" stroke="#1e293b" stroke-width="1"/>
  <line x1="100" y1="77" x2="100" y2="87" stroke="#1e293b" stroke-width="1"/>
  <line x1="160" y1="77" x2="160" y2="87" stroke="#1e293b" stroke-width="1"/>
  <!-- Gene agent -->
  <rect x="10" y="87" width="60" height="20" rx="5" fill="#1e293b" stroke="#a78bfa" stroke-width="1"/>
  <text x="40" y="100" text-anchor="middle" fill="#a78bfa" font-size="6.5">🔬 Gene</text>
  <!-- Literature agent -->
  <rect x="70" y="87" width="60" height="20" rx="5" fill="#1e293b" stroke="#a78bfa" stroke-width="1"/>
  <text x="100" y="100" text-anchor="middle" fill="#a78bfa" font-size="6.5">📚 Literature</text>
  <!-- Pathway agent -->
  <rect x="130" y="87" width="60" height="20" rx="5" fill="#1e293b" stroke="#a78bfa" stroke-width="1"/>
  <text x="160" y="100" text-anchor="middle" fill="#a78bfa" font-size="6.5">🌐 Pathway</text>
  <!-- Merge lines -->
  <line x1="40" y1="107" x2="40" y2="117" stroke="#1e293b" stroke-width="1"/>
  <line x1="100" y1="107" x2="100" y2="117" stroke="#1e293b" stroke-width="1"/>
  <line x1="160" y1="107" x2="160" y2="117" stroke="#1e293b" stroke-width="1"/>
  <line x1="40" y1="117" x2="160" y2="117" stroke="#1e293b" stroke-width="1"/>
  <line x1="100" y1="117" x2="100" y2="127" stroke="#00d4ff" stroke-width="1.5"/>
  <polygon points="100,130 96,125 104,125" fill="#00d4ff"/>
  <!-- Hypothesis -->
  <rect x="55" y="130" width="90" height="20" rx="5" fill="#1e293b" stroke="#f472b6" stroke-width="1"/>
  <text x="100" y="143" text-anchor="middle" fill="#f472b6" font-size="7">💡 Hypothesis</text>
  <line x1="100" y1="150" x2="100" y2="160" stroke="#f472b6" stroke-width="1.5"/>
  <polygon points="100,163 96,158 104,158" fill="#f472b6"/>
  <!-- Experiment -->
  <rect x="55" y="163" width="90" height="20" rx="5" fill="#1e293b" stroke="#f472b6" stroke-width="1"/>
  <text x="100" y="176" text-anchor="middle" fill="#f472b6" font-size="7">🧪 Experiment</text>
  <line x1="100" y1="183" x2="100" y2="193" stroke="#00d4ff" stroke-width="1.5"/>
  <polygon points="100,196 96,191 104,191" fill="#00d4ff"/>
  <!-- Report -->
  <rect x="55" y="196" width="90" height="20" rx="5" fill="#1e293b" stroke="#00d4ff" stroke-width="1"/>
  <text x="100" y="209" text-anchor="middle" fill="#00d4ff" font-size="7">📝 Report Generator</text>
  <line x1="100" y1="216" x2="100" y2="226" stroke="#00d4ff" stroke-width="1.5"/>
  <polygon points="100,229 96,224 104,224" fill="#00d4ff"/>
  <!-- Final output -->
  <rect x="40" y="229" width="120" height="22" rx="6" fill="url(#g1)" opacity="0.9"/>
  <text x="100" y="244" text-anchor="middle" fill="white" font-size="7.5" font-weight="bold">📄 Research Proposal</text>
</svg>
</div>
""", unsafe_allow_html=True)

    with right_col:
        st.markdown("#### 🧬 Agent Outputs")
        card_placeholders = {}
        for key, icon, name, _ in PIPELINE:
            card_placeholders[key] = st.empty()

    # ── Run agents ──
    for key, icon, name, module in PIPELINE:
        statuses[key] = "active"
        diagram_placeholder.markdown(render_diagram(statuses), unsafe_allow_html=True)

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
        diagram_placeholder.markdown(render_diagram(statuses), unsafe_allow_html=True)

        with card_placeholders[key].container():
            with st.expander(f"{icon} {name}", expanded=(key in ["orchestrator","hypothesis","report"])):
                st.markdown(out)

    st.success("✅ BioPilot Analysis Complete! Your research report is ready.")
    st.balloons()

    # ── Downloads ──
    st.markdown("---")
    st.markdown("### 📥 Download Full Report")
    dc1, dc2 = st.columns(2)
    with dc1:
        st.download_button("📄 Download Markdown (.md)",
            data=build_markdown_report(gene, disease, results),
            file_name=f"BioPilot_{gene}_{disease}.md",
            mime="text/markdown", use_container_width=True)
    with dc2:
        st.download_button("📃 Download Text (.txt)",
            data=build_txt_report(gene, disease, results),
            file_name=f"BioPilot_{gene}_{disease}.txt",
            mime="text/plain", use_container_width=True)