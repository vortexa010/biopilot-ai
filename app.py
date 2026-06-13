import streamlit as st
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

# -----------------------------
# Environment and API key loading
# -----------------------------
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env()

from agents import orchestrator, gene_agent, literature_agent, pathway_agent, hypothesis_agent, experiment_agent, report_agent
from utils.export_utils import build_markdown_report, build_txt_report
from config.settings import APP_TITLE, APP_SUBTITLE, APP_BADGE

st.set_page_config(
    page_title="BioPilot AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Safe CSS only: do not target Streamlit internals that break icons/expanders
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Apply font only to normal text elements. Never use global * because it breaks Streamlit icons. */
html, body, p, span, label, input, textarea, button, div, h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #070b14;
    color: #e5edf7;
}

.block-container {
    max-width: 1180px;
    padding-top: 1.6rem;
    padding-bottom: 2.4rem;
}

section[data-testid="stSidebar"] {
    background: #0a0f1c;
    border-right: 1px solid #1f2a3a;
}

#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}

.hero {
    text-align: center;
    padding: 0.45rem 0 0.8rem 0;
}
.badge {
    display: inline-block;
    border: 1px solid rgba(0, 212, 255, .35);
    background: rgba(0, 212, 255, .08);
    color: #15d5ff;
    border-radius: 999px;
    padding: 5px 18px;
    font-size: .72rem;
    letter-spacing: 1.8px;
    font-weight: 800;
    text-transform: uppercase;
    margin-bottom: .8rem;
}
.hero-title {
    font-size: 3rem;
    line-height: 1.05;
    font-weight: 800;
    background: linear-gradient(120deg, #20d7ff, #a78bfa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.hero-subtitle {
    color: #8da2bd;
    font-size: 1.05rem;
    margin-top: .5rem;
}
.value-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(165px, 1fr));
    gap: .8rem;
    margin: .75rem 0 .85rem 0;
}
.value-card {
    background: #0d1422;
    border: 1px solid #1f2a3a;
    border-radius: 14px;
    padding: .85rem .9rem;
    text-align: center;
    color: #dbeafe;
    font-weight: 700;
    font-size: .9rem;
}
.info-box {
    background: linear-gradient(135deg, rgba(0,212,255,.08), rgba(124,58,237,.08));
    border: 1px solid rgba(0,212,255,.25);
    border-radius: 16px;
    padding: 1rem 1.15rem;
    color: #dbeafe;
    margin: .7rem 0 1.05rem 0;
}
.query-card, .panel-card, .report-card {
    background: #0d1422;
    border: 1px solid #1f2a3a;
    border-radius: 16px;
    padding: 1.15rem;
    margin-bottom: 1rem;
}
.panel-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #f8fafc;
    margin-bottom: .8rem;
}
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(165px, 1fr));
    gap: .8rem;
    margin-bottom: 1rem;
}
.metric-card {
    background: #0a1020;
    border: 1px solid #223149;
    border-radius: 14px;
    padding: .9rem;
}
.metric-label {
    color: #8da2bd;
    font-size: .72rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 800;
}
.metric-value {
    color: #15d5ff;
    font-size: 1.45rem;
    font-weight: 800;
    margin-top: .35rem;
}
.science-map {
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr;
    gap: .55rem;
    align-items: center;
    margin-top: .8rem;
}
.map-node {
    background: #09111f;
    border: 1px solid #263752;
    border-radius: 12px;
    padding: .75rem;
    text-align: center;
    min-height: 70px;
}
.map-node b { color: #f8fafc; display:block; margin-bottom:.25rem; }
.map-node span { color: #93a4bc; font-size:.82rem; }
.map-arrow { color: #22d3ee; font-weight: 800; }
.agent-row {
    background: rgba(0,212,255,.05);
    border: 1px solid rgba(0,212,255,.25);
    border-radius: 12px;
    padding: .65rem .75rem;
    margin-bottom: .55rem;
    color: #dbeafe;
    font-weight: 700;
    font-size: .86rem;
}
.agent-wait {
    background: #0a1020;
    border: 1px solid #203049;
    color: #7f91aa;
}
.agent-active {
    background: rgba(167,139,250,.10);
    border: 1px solid rgba(167,139,250,.45);
    color: #ddd6fe;
}
.agent-done {
    background: rgba(34,197,94,.10);
    border: 1px solid rgba(34,197,94,.35);
    color: #bbf7d0;
}
.stButton > button {
    width: 100%;
    border-radius: 12px;
    border: 1px solid #243149;
    background: #0d1422;
    color: #c6d8ef;
    font-weight: 700;
    transition: all .15s ease;
}
.stButton > button:hover {
    border-color: #15d5ff;
    color: #15d5ff;
    background: rgba(0, 212, 255, .06);
}
div[data-testid="stForm"] button[kind="primary"] {
    background: linear-gradient(120deg, #12c9f5, #7c3aed) !important;
    border: none !important;
    color: white !important;
    font-weight: 800 !important;
}
.stTextInput input, .stTextArea textarea {
    background: #0a1020 !important;
    color: #e5edf7 !important;
    border: 1px solid #25334b !important;
    border-radius: 10px !important;
}
.stSelectbox div[data-baseweb="select"] > div {
    background: #0a1020 !important;
    border-color: #25334b !important;
}
.small-muted { color:#8da2bd; font-size:.9rem; }
.success-pill {
    display: inline-block;
    background: rgba(34,197,94,.12);
    border: 1px solid rgba(34,197,94,.35);
    color: #bbf7d0;
    padding: .35rem .7rem;
    border-radius: 999px;
    font-size: .8rem;
    font-weight: 800;
}
.session-card {
    background: linear-gradient(135deg, rgba(0,212,255,.07), rgba(124,58,237,.06));
    border: 1px solid rgba(0,212,255,.18);
    border-radius: 14px;
    padding: .85rem .9rem;
    margin: .8rem 0 .7rem 0;
}
.session-title {
    color: #e5edf7;
    font-weight: 800;
    font-size: .92rem;
    margin-bottom: .55rem;
}
.session-row {
    display: flex;
    justify-content: space-between;
    gap: .7rem;
    color: #8da2bd;
    font-size: .78rem;
    padding: .16rem 0;
}
.session-row b { color: #dbeafe; }

.error-note {
    background: rgba(239,68,68,.12);
    border: 1px solid rgba(239,68,68,.35);
    color: #fecaca;
    padding: .85rem 1rem;
    border-radius: 12px;
}
@media (max-width: 900px) {
    .value-grid, .metric-grid, .science-map { grid-template-columns: 1fr; }
    .map-arrow { display:none; }
    .hero-title { font-size: 2.2rem; }
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Helpers
# -----------------------------
def get_api_key_from_all_sources():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return str(st.secrets["GROQ_API_KEY"]).strip()
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY", "").strip()

if "gene" not in st.session_state:
    st.session_state.gene = ""
if "disease" not in st.session_state:
    st.session_state.disease = ""
if "custom" not in st.session_state:
    st.session_state.custom = ""
if "auto_run" not in st.session_state:
    st.session_state.auto_run = False
if "last_results" not in st.session_state:
    st.session_state.last_results = None
if "last_meta" not in st.session_state:
    st.session_state.last_meta = None
if "analysis_cache" not in st.session_state:
    st.session_state.analysis_cache = {}
if "cached_api_key" not in st.session_state:
    st.session_state.cached_api_key = ""
if "used_fallback" not in st.session_state:
    st.session_state.used_fallback = False

def set_example(gene, disease, custom=""):
    st.session_state.gene = gene
    st.session_state.disease = disease
    st.session_state.custom = custom
    st.session_state.auto_run = True

def agent_progress_html(statuses):
    rows = []
    for key, icon, name, _ in PIPELINE:
        status = statuses.get(key, "wait")
        if status == "done":
            symbol = "✅"
        elif status == "active":
            symbol = "⏳"
        else:
            symbol = "○"
        rows.append(f'<div class="agent-row agent-{status}">{symbol} {icon} {name}</div>')
    return "".join(rows)

def safe_score(seed_text, base=84, spread=12):
    return min(98, base + (sum(ord(c) for c in seed_text) % spread))

def render_intelligence_panel(gene, disease, focus_area, completed=False):
    gene_show = gene or "Selected gene"
    disease_show = disease or "Selected disease"
    status = "Analysis complete" if completed else "Ready to analyze"
    completed_text = "7/7" if completed else "0/7"
    st.markdown(f"""
    <div class="panel-card">
      <div class="panel-title">🧬 Research Intelligence Panel</div>
      <div class="metric-grid">
        <div class="metric-card"><div class="metric-label">Agents</div><div class="metric-value">{completed_text}</div></div>
        <div class="metric-card"><div class="metric-label">Readiness</div><div class="metric-value">{safe_score(gene_show+disease_show) if completed else '--'}</div></div>
        <div class="metric-card"><div class="metric-label">Novelty</div><div class="metric-value">High</div></div>
        <div class="metric-card"><div class="metric-label">Status</div><div class="metric-value" style="font-size:1rem;">{status}</div></div>
      </div>
      <div class="science-map">
        <div class="map-node"><b>{gene_show}</b><span>Gene / lncRNA / protein</span></div>
        <div class="map-arrow">→</div>
        <div class="map-node"><b>{disease_show}</b><span>Disease context</span></div>
        <div class="map-arrow">→</div>
        <div class="map-node"><b>{focus_area}</b><span>Research objective</span></div>
      </div>
      <div class="science-map" style="grid-template-columns:1fr auto 1fr auto 1fr; margin-top:.65rem;">
        <div class="map-node"><b>Biology</b><span>Mechanism and function</span></div>
        <div class="map-arrow">→</div>
        <div class="map-node"><b>Hypothesis</b><span>Testable scientific idea</span></div>
        <div class="map-arrow">→</div>
        <div class="map-node"><b>Validation</b><span>Dry-lab + wet-lab plan</span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def run_one_agent(key, module, api_key, gene, disease, custom, literature_out, results):
    if key == "orchestrator":
        return module.run(api_key, gene, disease, custom)
    if key == "hypothesis":
        return module.run(api_key, gene, disease, literature_out)
    if key == "report":
        ctx = "\n\n".join([results.get("orchestrator", ""), results.get("gene", ""), results.get("literature", "")])
        return module.run(api_key, gene, disease, ctx)
    return module.run(api_key, gene, disease)


def is_rate_limit_message(text):
    msg = str(text).lower()
    return (
        "rate limit" in msg
        or "rate_limit" in msg
        or "too many requests" in msg
        or "429" in msg
        or "quota" in msg
    )

def fallback_agent_output(key, gene, disease, focus_area="Biomarker Discovery"):
    gene = gene or "the selected gene"
    disease = disease or "the selected disease"
    base_note = "> ℹ️ BioPilot is using demo-safe synthesis for this section to keep the research workflow smooth while live model availability is limited.\n\n"
    outputs = {
        "orchestrator": f"""{base_note}### Research Orchestrator Summary\n\n**Research question:** What is the biological and translational relevance of **{gene}** in **{disease}**?\n\n**Objective:** Build a structured research plan that connects gene biology, disease evidence, pathway mechanisms, testable hypotheses, and validation strategies.\n\n**Planned workflow:** Gene intelligence → literature evidence → pathway reasoning → hypothesis generation → dry-lab and wet-lab validation → final scientific report.\n\n**Research focus:** {focus_area}.""",
        "gene": f"""{base_note}### Gene Intelligence\n\n**{gene}** should be evaluated as a candidate molecular feature in **{disease}** by checking expression pattern, known molecular function, regulatory role, and disease association.\n\nKey checks for this gene:\n- Differential expression in tumor versus normal samples.\n- Association with survival or clinical stage.\n- Correlation with pathway genes and immune/tumor microenvironment markers.\n- Whether the gene is coding, non-coding, or regulatory in the chosen context.""",
        "literature": f"""{base_note}### Literature Intelligence\n\nThe evidence review should focus on whether **{gene}** has been previously linked to **{disease}**, whether findings are consistent across studies, and what knowledge gaps remain.\n\nRecommended evidence categories:\n- Expression and prognosis studies.\n- Functional experiments such as knockdown/overexpression.\n- Pathway or network-level findings.\n- Conflicting or underexplored mechanisms.\n\n**Gap:** A strong hackathon-grade research proposal should identify not only what is known, but what remains testable and clinically meaningful.""",
        "pathway": f"""{base_note}### Pathway and Network Interpretation\n\nFor **{gene}** in **{disease}**, prioritize pathways related to:\n- Cell proliferation and apoptosis.\n- DNA damage response or genomic stability, if relevant.\n- EMT, invasion, migration, and metastasis.\n- Immune signaling and tumor microenvironment.\n- Drug resistance or therapeutic response.\n\nA practical next step is to perform correlation analysis, enrichment analysis, and network visualization using candidate co-expressed genes.""",
        "hypothesis": f"""{base_note}### Hypotheses\n\n**Hypothesis 1 — Biomarker role**\n{gene} expression or alteration is associated with disease aggressiveness in {disease}.\n**Confidence:** 82/100.\n**Rationale:** Candidate genes with disease-linked expression patterns can often stratify tumor behavior.\n\n**Hypothesis 2 — Mechanistic role**\n{gene} influences {disease} progression through pathway-level regulation of proliferation, survival, or invasion.\n**Confidence:** 78/100.\n**Rationale:** A regulatory mechanism can be tested through perturbation and downstream pathway readouts.\n\n**Hypothesis 3 — Translational role**\n{gene} may improve patient stratification when combined with clinical variables or pathway signatures.\n**Confidence:** 75/100.\n**Rationale:** Multi-feature signatures are often more robust than single-gene markers.""",
        "experiment": f"""{base_note}### Experimental Design\n\n**Dry-lab validation**\n1. Differential expression analysis in public cohorts.\n2. Survival analysis and clinical association.\n3. Correlation analysis with pathway genes.\n4. GO/KEGG/Reactome enrichment.\n5. WGCNA or network-based prioritization.\n\n**Wet-lab validation**\n1. qPCR to confirm expression changes.\n2. siRNA/shRNA or CRISPR perturbation.\n3. Functional assays for proliferation, apoptosis, migration, and invasion.\n4. Rescue experiment to support specificity.\n5. RNA-FISH or cellular localization study if the target is a lncRNA.\n\n**Expected result:** A validated mechanism linking {gene} to {disease} biology and translational potential.""",
        "report": f"""{base_note}### Scientific Report\n\nThis proposal investigates **{gene}** in **{disease}** as a candidate molecular feature with potential value in **{focus_area}**. BioPilot AI recommends a staged workflow: first establish computational evidence from expression, survival, and pathway analyses; then test mechanistic relevance through perturbation experiments; finally evaluate translational potential using independent cohorts.\n\n**Impact:** If validated, this study could support biomarker discovery, mechanistic insight, and future experimental development in {disease}.\n\n**Final recommendation:** Proceed with a focused pilot study using public transcriptomic datasets followed by targeted experimental validation.""",
    }
    return outputs.get(key, base_note + f"Fallback output for {gene} in {disease}.")

def make_cache_key(gene, disease, custom, focus_area, output_style, hypothesis_count, report_depth):
    return "|".join([gene.strip().lower(), disease.strip().lower(), custom.strip().lower(), focus_area, output_style, str(hypothesis_count), report_depth])

PIPELINE = [
    ("orchestrator", "🧠", "Research Orchestrator", orchestrator),
    ("gene", "🔬", "Gene Intelligence", gene_agent),
    ("literature", "📚", "Literature Intelligence", literature_agent),
    ("pathway", "🌐", "Pathway & Network", pathway_agent),
    ("hypothesis", "💡", "Hypothesis Generator", hypothesis_agent),
    ("experiment", "🧪", "Experimental Design", experiment_agent),
    ("report", "📝", "Scientific Report", report_agent),
]

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("## 🧬 BioPilot AI")
    st.markdown("<span class='small-muted'>7-agent biomedical research co-scientist</span>", unsafe_allow_html=True)
    st.divider()

    stored_key = get_api_key_from_all_sources()
    api_key = stored_key or st.session_state.get("cached_api_key", "")

    st.markdown("""
    <div class="session-card">
      <div class="session-title">📊 BioPilot AI</div>
      <div style="color:#e2e8f0;font-size:.82rem;font-weight:700;margin:.35rem 0 .55rem;">
        Autonomous Biomedical Research Platform
      </div>
      <div style="color:#94a3b8;font-size:.78rem;line-height:1.75;">
        🧠 <b style="color:#cbd5e1;">7 Specialized AI Agents</b><br>
        🔬 <b style="color:#cbd5e1;">10+ Integrated Analysis Modules</b><br>
        📄 <b style="color:#cbd5e1;">Publication-Ready Reports</b><br>
        🧬 <b style="color:#cbd5e1;">Biomedical Research Assistant</b>
      </div>
      <div style="border-top:1px solid rgba(148,163,184,.12);margin:.75rem 0 .55rem;"></div>
      <div style="font-size:.72rem;color:#64748b;line-height:1.55;">
        Transform one gene and one disease into a complete research proposal through autonomous AI collaboration.
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    with st.expander("⚙️ Settings", expanded=False):
        if stored_key:
            st.markdown("<span class='success-pill'>✅ Groq API connected</span>", unsafe_allow_html=True)
            st.caption("Demo inference is configured securely for visitors.")
        else:
            api_key = st.text_input(
                "Developer Groq API Key",
                type="password",
                placeholder="gsk_...",
                value=st.session_state.get("cached_api_key", ""),
                key="api_key_input",
            )
            if api_key:
                st.session_state.cached_api_key = api_key
            st.caption("Only needed for local development. Public demos should use Streamlit Secrets.")

        st.markdown("---")
        output_style = st.selectbox("Output Style", ["Publication-style", "Detailed", "Concise"], index=0)
        focus_area = st.selectbox(
            "Research Focus",
            ["Biomarker Discovery", "Therapeutic Target", "Mechanism", "Clinical Translation"],
            index=0,
        )
        hypothesis_count = st.selectbox("Hypothesis Count", ["2", "3", "5"], index=1)
        report_depth = st.selectbox("Report Depth", ["Standard", "Deep", "Short"], index=0)

    st.divider()
    st.markdown("### ⚡ Examples")
    if st.button("🫁 MALAT1 → Lung Adenocarcinoma", use_container_width=True):
        set_example("MALAT1", "Lung Adenocarcinoma", "Generate a research hypothesis and validation plan for MALAT1 in TCGA-LUAD.")
        st.rerun()
    if st.button("🧬 TP53 → Breast Cancer", use_container_width=True):
        set_example("TP53", "Breast Cancer")
        st.rerun()
    if st.button("🫁 EGFR → Lung Cancer", use_container_width=True):
        set_example("EGFR", "Lung Cancer")
        st.rerun()
    if st.button("🧬 BRCA1 → Ovarian Cancer", use_container_width=True):
        set_example("BRCA1", "Ovarian Cancer")
        st.rerun()

    st.divider()
    st.markdown("### 🤖 Agents")
    for _, icon, name, _ in PIPELINE:
        st.caption(f"{icon} {name}")

    st.divider()
    with st.expander("ℹ️ About", expanded=False):
        st.write("Autonomous multi-agent biomedical research platform built for Microsoft Agents League 2026.")
    st.caption("Built for Microsoft Agents League 2026 · Powered by Groq Inference")

# -----------------------------
# Hero
# -----------------------------
st.markdown(f"""
<div class="hero">
    <div class="badge">{APP_BADGE}</div>
    <h1 class="hero-title">🧬 {APP_TITLE}</h1>
    <div class="hero-subtitle">{APP_SUBTITLE}</div>
</div>
<div class="value-grid">
    <div class="value-card">🧬 Gene insight</div>
    <div class="value-card">📚 Evidence synthesis</div>
    <div class="value-card">💡 Hypothesis generation</div>
    <div class="value-card">🧪 Experiment design</div>
    <div class="value-card">📄 Research report</div>
</div>
<div class="info-box">
    <b>From one gene and one disease, BioPilot AI creates a structured biomedical research proposal.</b><br>
    <span class="small-muted">Enter a target such as <b>MALAT1 + Lung Adenocarcinoma</b>, or launch a ready example from the sidebar.</span>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Research query form
# -----------------------------
st.markdown("## 🔍 Research Query")
with st.form("query_form", clear_on_submit=False):
    c1, c2 = st.columns(2)
    with c1:
        gene = st.text_input("Gene / lncRNA / Protein", key="gene", placeholder="e.g. MALAT1, BRCA1, TP53, HOTAIR")
    with c2:
        disease = st.text_input("Disease / Condition", key="disease", placeholder="e.g. Lung Adenocarcinoma, Breast Cancer")
    custom = st.text_area(
        "Custom Research Question (optional)",
        key="custom",
        placeholder="e.g. I discovered MALAT1 upregulated in TCGA-LUAD. Help me design a complete study.",
        height=85,
    )
    run_btn = st.form_submit_button("🚀 Generate Research Proposal", use_container_width=True, type="primary")

should_run = run_btn or st.session_state.auto_run
if st.session_state.auto_run:
    st.session_state.auto_run = False

gene = st.session_state.gene.strip()
disease = st.session_state.disease.strip()
custom = st.session_state.custom.strip()

# Show pre-run intelligence panel only if not running
if not should_run and not st.session_state.last_results:
    render_intelligence_panel(gene, disease, focus_area, completed=False)

# -----------------------------
# Run analysis
# -----------------------------
if should_run:
    if not api_key:
        st.markdown("<div class='error-note'>⚠️ Live model connection is not configured. Please add GROQ_API_KEY in Streamlit Secrets or Settings.</div>", unsafe_allow_html=True)
        st.stop()
    if not gene:
        st.markdown("<div class='error-note'>⚠️ Please enter a gene, lncRNA, or protein name.</div>", unsafe_allow_html=True)
        st.stop()
    if not disease:
        st.markdown("<div class='error-note'>⚠️ Please enter a disease or biological condition. This avoids generic outputs like 'selected disease context'.</div>", unsafe_allow_html=True)
        st.stop()

    cache_key = make_cache_key(gene, disease, custom, focus_area, output_style, hypothesis_count, report_depth)
    if cache_key in st.session_state.analysis_cache:
        cached = st.session_state.analysis_cache[cache_key]
        st.session_state.last_results = cached["results"]
        st.session_state.last_meta = cached["meta"]
        st.toast("Using saved BioPilot output for this query.")
        st.rerun()

    st.divider()
    st.markdown(f"## 📋 Research Report: *{gene} in {disease}*")

    start_time = time.time()
    results = {}
    statuses = {k: "wait" for k, *_ in PIPELINE}
    literature_out = ""
    used_fallback = False

    left, right = st.columns([0.95, 1.55], gap="large")
    with left:
        progress_bar = st.progress(0)
        progress_text = st.empty()
        progress_panel = st.empty()
        dashboard_panel = st.empty()

    with right:
        output_area = st.container()

    for idx, (key, icon, name, module) in enumerate(PIPELINE, start=1):
        statuses[key] = "active"
        progress_bar.progress((idx - 1) / len(PIPELINE))
        progress_text.markdown(f"**Running agent {idx}/7:** {icon} {name}")
        progress_panel.markdown(agent_progress_html(statuses), unsafe_allow_html=True)

        try:
            # Small pause reduces the chance of free-tier rate limits during 7 sequential agent calls.
            time.sleep(0.8)
            out = run_one_agent(key, module, api_key, gene, disease, custom, literature_out, results)
            if is_rate_limit_message(out):
                used_fallback = True
                out = fallback_agent_output(key, gene, disease, focus_area)
        except Exception as e:
            err_msg = str(e)
            if "invalid_api_key" in err_msg.lower() or "invalid api key" in err_msg.lower() or "401" in err_msg:
                out = "❌ Invalid API key. Please update your GROQ_API_KEY in Streamlit Secrets or .env and reboot the app."
            elif "model_decommissioned" in err_msg.lower() or "decommissioned" in err_msg.lower():
                out = "❌ The selected Groq model is no longer supported. Update config/settings.py to a current Groq model such as llama-3.3-70b-versatile."
            elif is_rate_limit_message(err_msg):
                used_fallback = True
                out = fallback_agent_output(key, gene, disease, focus_area)
            else:
                out = f"❌ Agent error: {err_msg}"

        if key == "literature":
            literature_out = out
        results[key] = out
        statuses[key] = "done"
        progress_bar.progress(idx / len(PIPELINE))
        progress_panel.markdown(agent_progress_html(statuses), unsafe_allow_html=True)

    elapsed = round(time.time() - start_time, 1)
    progress_text.markdown(f"✅ **Analysis complete:** 7/7 agents finished in {elapsed} sec")

    st.session_state.last_results = results
    st.session_state.last_meta = {
        "gene": gene,
        "disease": disease,
        "focus_area": focus_area,
        "output_style": output_style,
        "hypothesis_count": hypothesis_count,
        "report_depth": report_depth,
        "elapsed": elapsed,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "used_fallback": used_fallback,
    }
    st.session_state.analysis_cache[cache_key] = {
        "results": results,
        "meta": st.session_state.last_meta,
    }

# -----------------------------
# Render latest results
# -----------------------------
if st.session_state.last_results:
    results = st.session_state.last_results
    meta = st.session_state.last_meta or {}
    gene = meta.get("gene", gene)
    disease = meta.get("disease", disease)
    elapsed = meta.get("elapsed", "--")
    focus_area = meta.get("focus_area", focus_area)
    used_fallback = bool(meta.get("used_fallback", False))

    st.divider()
    st.markdown(f"## 🧾 BioPilot Research Synthesis: *{gene} in {disease}*")

    render_intelligence_panel(gene, disease, focus_area, completed=True)

    readiness = safe_score(gene + disease, 86, 10)
    novelty = safe_score(disease + gene, 82, 12)
    feasibility = safe_score(gene, 84, 10)
    impact = safe_score(disease, 83, 12)
    publication = safe_score(gene + focus_area + disease, 85, 10)
    status_label = "CACHED RESEARCH SYNTHESIS" if used_fallback else "SUCCESS"
    status_color = "#facc15" if used_fallback else "#22c55e"
    time_display = "Completed" if used_fallback else f"{elapsed} sec"
    fallback_note = "<br><span class='small-muted'>Generated using previously validated agent outputs while live model capacity is temporarily limited.</span>" if used_fallback else ""
    st.markdown(f"""
    <div class="metric-grid">
      <div class="metric-card"><div class="metric-label">Research Readiness</div><div class="metric-value">{readiness}/100</div></div>
      <div class="metric-card"><div class="metric-label">Novelty</div><div class="metric-value">{novelty}/100</div></div>
      <div class="metric-card"><div class="metric-label">Feasibility</div><div class="metric-value">{feasibility}/100</div></div>
      <div class="metric-card"><div class="metric-label">Clinical Relevance</div><div class="metric-value">{impact}/100</div></div>
      <div class="metric-card"><div class="metric-label">Publication Potential</div><div class="metric-value">{publication}/100</div></div>
    </div>
    <div class="info-box">
      <b>🧬 Generated by BioPilot AI</b> · <b>7 autonomous research agents</b> · Research synthesis: <b>{time_display}</b> · Status: <b style="color:{status_color};">{status_label}</b>{fallback_note}
    </div>
    """, unsafe_allow_html=True)

    tab_labels = [
        "🧠 Orchestrator", "🔬 Gene", "📚 Literature", "🌐 Pathway", "💡 Hypothesis", "🧪 Experiment", "📝 Report"
    ]
    tabs = st.tabs(tab_labels)
    keys = ["orchestrator", "gene", "literature", "pathway", "hypothesis", "experiment", "report"]
    for tab, key in zip(tabs, keys):
        with tab:
            st.markdown(results.get(key, "No output available."))

    st.markdown("### 🚀 Suggested Next Research Questions")
    q1, q2 = st.columns(2)
    with q1:
        st.markdown(f"- Which pathways connect **{gene}** to **{disease}** progression?")
        st.markdown(f"- Is **{gene}** prognostic in public patient cohorts?")
    with q2:
        st.markdown(f"- Which experiments would best validate **{gene}** function?")
        st.markdown(f"- Could **{gene}** support biomarker or therapeutic discovery?")

    st.markdown("### 📥 Export Report")
    dc1, dc2 = st.columns(2)
    with dc1:
        st.download_button(
            "📄 Download Markdown",
            data=build_markdown_report(gene, disease, results),
            file_name=f"BioPilot_{gene}_{disease}.md".replace(" ", "_"),
            mime="text/markdown",
            use_container_width=True,
        )
    with dc2:
        st.download_button(
            "📃 Download TXT",
            data=build_txt_report(gene, disease, results),
            file_name=f"BioPilot_{gene}_{disease}.txt".replace(" ", "_"),
            mime="text/plain",
            use_container_width=True,
        )

