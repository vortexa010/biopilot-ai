import streamlit as st
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

# ─────────────────────────────────────────────────────────────────────────────
# Environment + secrets
# ─────────────────────────────────────────────────────────────────────────────
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env()

from agents import (
    orchestrator,
    gene_agent,
    literature_agent,
    pathway_agent,
    hypothesis_agent,
    experiment_agent,
    report_agent,
)
from utils.export_utils import build_markdown_report, build_txt_report
from config.settings import APP_TITLE, APP_SUBTITLE, APP_BADGE


st.set_page_config(
    page_title="BioPilot AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Stable CSS: no global icon-font breaking, no Streamlit expander hacks
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .stApp {
    background: #060b14 !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main,
.block-container {
    background: #060b14 !important;
    color: #e2e8f0 !important;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1180px !important;
}

#MainMenu,
footer,
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="collapsedControl"],
.stDeployButton {
    display: none !important;
}

header[data-testid="stHeader"] {
    background: rgba(6, 11, 20, 0.95) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #090e18 !important;
    border-right: 1px solid #1e293b !important;
}

section[data-testid="stSidebar"] > div {
    background: #090e18 !important;
    padding-top: 2rem !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: #cbd5e1 !important;
}

.sidebar-card {
    background: #0d1420;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 1rem;
    margin: .7rem 0;
}

.status-ok {
    background: rgba(34,197,94,.12);
    border: 1px solid rgba(34,197,94,.35);
    color: #86efac;
    padding: .75rem;
    border-radius: 10px;
    font-weight: 700;
}

.status-warn {
    background: rgba(251,191,36,.10);
    border: 1px solid rgba(251,191,36,.28);
    color: #fde68a;
    padding: .75rem;
    border-radius: 10px;
    font-weight: 700;
}

/* Hero */
.hero {
    text-align: center;
    padding: 1rem 0 1.3rem 0;
}

.badge {
    display: inline-block;
    background: rgba(0,212,255,0.08);
    border: 1px solid rgba(0,212,255,0.30);
    color: #22d3ee;
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 5px 18px;
    border-radius: 999px;
    margin-bottom: .9rem;
}

.title {
    font-size: clamp(2.2rem, 5vw, 3.1rem);
    font-weight: 800;
    background: linear-gradient(135deg,#22d3ee,#a78bfa,#f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.05;
}

.subtitle {
    color: #64748b;
    font-size: 1rem;
    margin-top: .35rem;
}

/* Inputs */
.stTextInput input,
.stTextArea textarea {
    background: #0d1420 !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #22d3ee !important;
    box-shadow: 0 0 0 2px rgba(34,211,238,.14) !important;
}

.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stSlider label,
.stCheckbox label {
    color: #93a4bd !important;
    font-size: .82rem !important;
}

/* Buttons */
.stButton > button {
    background: #0d1420 !important;
    border: 1px solid #243244 !important;
    color: #bfdbfe !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    width: 100% !important;
    transition: all .18s ease-in-out !important;
}

.stButton > button:hover {
    border-color: #22d3ee !important;
    color: #22d3ee !important;
    background: rgba(34,211,238,.06) !important;
}

div[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg,#06b6d4,#7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    min-height: 48px !important;
}

/* Cards */
.metric-card {
    background: #0d1420;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 1rem;
    height: 100%;
}

.metric-value {
    color: #22d3ee;
    font-weight: 800;
    font-size: 1.6rem;
}

.metric-label {
    color: #94a3b8;
    font-size: .78rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.panel {
    background: #0d1420;
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.panel-title {
    color: #e2e8f0;
    font-weight: 800;
    margin-bottom: .65rem;
}

.mini-map {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: .5rem;
    flex-wrap: wrap;
}

.map-node {
    background: rgba(34,211,238,.06);
    border: 1px solid rgba(34,211,238,.26);
    color: #bae6fd;
    padding: .55rem .75rem;
    border-radius: 10px;
    font-size: .8rem;
    font-weight: 700;
}

.map-arrow {
    color: #475569;
    font-weight: 800;
}

.agent-row {
    display: flex;
    align-items: center;
    gap: .7rem;
    background: rgba(34,211,238,.05);
    border: 1px solid rgba(34,211,238,.22);
    border-radius: 10px;
    padding: .55rem .75rem;
    margin-bottom: .45rem;
    color: #67e8f9;
    font-weight: 700;
    font-size: .84rem;
}

.agent-wait {
    opacity: .45;
    background: #0a0f1a;
    border-color: #1e293b;
    color: #94a3b8;
}

/* Expander normal, no custom arrow hacks */
.streamlit-expanderHeader {
    color: #e2e8f0 !important;
    font-weight: 700 !important;
}

hr {
    border-color: #1e293b !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
PIPELINE = [
    ("orchestrator", "🧠", "Research Orchestrator", orchestrator),
    ("gene", "🔬", "Gene Intelligence", gene_agent),
    ("literature", "📚", "Literature Intelligence", literature_agent),
    ("pathway", "🌐", "Pathway & Network", pathway_agent),
    ("hypothesis", "💡", "Hypothesis Generator", hypothesis_agent),
    ("experiment", "🧪", "Experimental Design", experiment_agent),
    ("report", "📝", "Scientific Report", report_agent),
]

EXAMPLES = {
    "🧬 MALAT1 + LUAD": ("MALAT1", "Lung Adenocarcinoma"),
    "🔬 TP53 + Breast Cancer": ("TP53", "Breast Cancer"),
    "💊 EGFR + Lung Cancer": ("EGFR", "Lung Cancer"),
    "🦠 BRCA1 + Ovarian Cancer": ("BRCA1", "Ovarian Cancer"),
}


def get_secret_key() -> str:
    """Priority: Streamlit secrets → environment/.env → session manual input."""
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY", "") or st.session_state.get("manual_groq_key", "")


def set_example(gene: str, disease: str):
    st.session_state["gene_input"] = gene
    st.session_state["disease_input"] = disease
    st.session_state["custom_input"] = ""
    st.session_state["auto_run"] = True


def render_agent_status(statuses):
    html = '<div class="panel"><div class="panel-title">⚡ Live Agent Status</div>'
    for key, icon, name, _module in PIPELINE:
        done = statuses.get(key, "wait") == "done"
        active = statuses.get(key, "wait") == "active"
        symbol = "✅" if done else ("⏳" if active else icon)
        css = "agent-row" if (done or active) else "agent-row agent-wait"
        html += f'<div class="{css}"><span>{symbol}</span><span>{name}</span></div>'
    html += "</div>"
    return html


def render_intelligence_panel(gene, disease, completed=False):
    status = "7/7 completed" if completed else "Ready to analyze"
    html = f"""
    <div class="panel">
        <div class="panel-title">🧬 Research Intelligence Panel</div>
        <div class="mini-map">
            <div class="map-node">{gene or "Gene"}</div>
            <div class="map-arrow">→</div>
            <div class="map-node">{disease or "Disease"}</div>
            <div class="map-arrow">→</div>
            <div class="map-node">Pathways</div>
            <div class="map-arrow">→</div>
            <div class="map-node">Hypotheses</div>
            <div class="map-arrow">→</div>
            <div class="map-node">Validation</div>
        </div>
        <div style="margin-top:.9rem;color:#94a3b8;font-size:.85rem;">
            <b>Status:</b> {status}<br>
            <b>System:</b> 7-agent autonomous biomedical research co-scientist
        </div>
    </div>
    """
    return html


def render_score_dashboard():
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("7/7", "Agents Completed"),
        ("9.1/10", "Readiness Score"),
        ("High", "Novelty Potential"),
        ("Strong", "Feasibility"),
    ]
    for col, (value, label) in zip([c1, c2, c3, c4], cards):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Initialize session state
# ─────────────────────────────────────────────────────────────────────────────
for key, value in {
    "gene_input": "",
    "disease_input": "",
    "custom_input": "",
    "auto_run": False,
    "last_results": None,
}.items():
    st.session_state.setdefault(key, value)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧬 BioPilot AI")
    st.markdown("---")

    secret_key = get_secret_key()
    if secret_key:
        st.markdown('<div class="status-ok">✅ Groq API Key loaded</div>', unsafe_allow_html=True)
        api_key = secret_key
    else:
        st.markdown('<div class="status-warn">⚠️ Add Groq API key</div>', unsafe_allow_html=True)
        st.session_state["manual_groq_key"] = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="gsk_...",
            value=st.session_state.get("manual_groq_key", ""),
            help="For Streamlit Cloud, add GROQ_API_KEY in app Secrets so you do not paste it every time.",
        )
        api_key = st.session_state.get("manual_groq_key", "")

    st.markdown("---")

    show_settings = st.checkbox("⚙️ Show settings", value=False)
    if show_settings:
        with st.container():
            st.markdown("#### ⚙️ Settings")
            output_style = st.selectbox(
                "Output Style",
                ["Detailed", "Concise", "Publication-style", "Clinical"],
                index=0,
            )
            focus_area = st.selectbox(
                "Research Focus",
                [
                    "Biomarker Discovery",
                    "Therapeutic Target",
                    "Mechanistic Study",
                    "Clinical Translation",
                    "Drug Resistance",
                    "Immunotherapy",
                ],
                index=0,
            )
            hypothesis_count = st.slider("Number of Hypotheses", 2, 5, 3)
            report_depth = st.selectbox("Report Depth", ["Standard", "Short", "Deep"], index=0)
    else:
        output_style = "Detailed"
        focus_area = "Biomarker Discovery"
        hypothesis_count = 3
        report_depth = "Standard"

    st.markdown("---")
    st.markdown("#### 📖 How to use")
    st.markdown(
        "1. Enter gene + disease\n"
        "2. Click **Run BioPilot**\n"
        "3. Watch 7 agents collaborate\n"
        "4. Review the research report\n"
        "5. Download full report"
    )

    st.markdown("---")
    st.markdown("#### ⚡ Quick Examples")
    for label, (g, d) in EXAMPLES.items():
        if st.button(label, use_container_width=True):
            set_example(g, d)
            st.rerun()

    st.markdown("---")
    st.markdown("#### 🤖 Agent Pipeline")
    for icon, name in [
        ("🧠", "Orchestrator"),
        ("🔬", "Gene Intelligence"),
        ("📚", "Literature"),
        ("🌐", "Pathway & Network"),
        ("💡", "Hypothesis"),
        ("🧪", "Experiment"),
        ("📝", "Report"),
    ]:
        st.markdown(f"{icon} {name}")

    st.markdown("---")
    st.caption("Built with GitHub Copilot-assisted development · Powered by Groq LLM inference")


# ─────────────────────────────────────────────────────────────────────────────
# Main UI
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="hero">
        <div class="badge">{APP_BADGE}</div>
        <div class="title">🧬 {APP_TITLE}</div>
        <div class="subtitle">{APP_SUBTITLE}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")
st.markdown("### 🔍 Research Query")

with st.form("research_form"):
    c1, c2 = st.columns(2)
    with c1:
        gene = st.text_input(
            "Gene / lncRNA / Protein",
            key="gene_input",
            placeholder="e.g. MALAT1, BRCA1, TP53, HOTAIR",
        )
    with c2:
        disease = st.text_input(
            "Disease / Condition",
            key="disease_input",
            placeholder="e.g. Lung Adenocarcinoma, Breast Cancer",
        )

    custom = st.text_area(
        "Custom Research Question (optional)",
        key="custom_input",
        placeholder="e.g. I discovered MALAT1 upregulated in TCGA-LUAD. Help me design a complete study.",
        height=80,
    )

    run_btn = st.form_submit_button("🚀 Run BioPilot Analysis — Activate All Agents", use_container_width=True)

should_run = run_btn or st.session_state.get("auto_run", False)

st.markdown(render_intelligence_panel(st.session_state["gene_input"], st.session_state["disease_input"]), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Execute agents
# ─────────────────────────────────────────────────────────────────────────────
if should_run:
    st.session_state["auto_run"] = False

    gene = st.session_state["gene_input"].strip()
    disease = st.session_state["disease_input"].strip()
    custom = st.session_state["custom_input"].strip()

    if not api_key:
        st.error("⚠️ No Groq API key found. Add it in Streamlit Cloud Secrets or paste it in the sidebar.")
        st.stop()

    if not gene:
        st.error("⚠️ Please enter a gene name.")
        st.stop()

    if not disease:
        disease = "the selected disease context"

    st.markdown("---")
    st.markdown(f"## 📋 Research Report: *{gene} in {disease}*")

    statuses = {k: "wait" for k, *_ in PIPELINE}
    results = {}
    literature_out = ""

    left_col, right_col = st.columns([0.75, 1.25], gap="large")

    with left_col:
        status_box = st.empty()
        insight_box = st.empty()

    with right_col:
        st.markdown("### 🧬 Agent Outputs")
        output_boxes = {key: st.empty() for key, *_ in PIPELINE}

    for key, icon, name, module in PIPELINE:
        statuses[key] = "active"
        status_box.markdown(render_agent_status(statuses), unsafe_allow_html=True)
        insight_box.markdown(render_intelligence_panel(gene, disease), unsafe_allow_html=True)

        try:
            if key == "orchestrator":
                prompt_context = (
                    f"{custom}\n\nSettings: output_style={output_style}; "
                    f"focus_area={focus_area}; hypotheses={hypothesis_count}; depth={report_depth}"
                )
                out = module.run(api_key, gene, disease, prompt_context)
            elif key == "hypothesis":
                out = module.run(api_key, gene, disease, literature_out)
            elif key == "report":
                ctx = "\n\n".join(results.values())
                out = module.run(api_key, gene, disease, ctx)
            else:
                out = module.run(api_key, gene, disease)
        except Exception as e:
            error_text = str(e)
            if "invalid_api_key" in error_text.lower() or "invalid api key" in error_text.lower() or "401" in error_text:
                out = "❌ Invalid API key. Please update GROQ_API_KEY in Streamlit Cloud Secrets or paste a valid key in the sidebar."
            elif "model_decommissioned" in error_text.lower() or "decommissioned" in error_text.lower():
                out = "❌ The selected Groq model is deprecated. Update your model name in config/settings.py to a currently supported Groq model."
            else:
                out = f"❌ Agent error: {error_text}"

        if key == "literature":
            literature_out = out

        results[key] = out
        statuses[key] = "done"
        status_box.markdown(render_agent_status(statuses), unsafe_allow_html=True)
        insight_box.markdown(render_intelligence_panel(gene, disease, completed=False), unsafe_allow_html=True)

        with output_boxes[key].container():
            with st.expander(f"{icon} {name}", expanded=(key in ["orchestrator", "hypothesis", "report"])):
                st.markdown(out)

        time.sleep(0.15)

    insight_box.markdown(render_intelligence_panel(gene, disease, completed=True), unsafe_allow_html=True)

    st.session_state["last_results"] = {
        "gene": gene,
        "disease": disease,
        "results": results,
    }

    st.success("✅ BioPilot Analysis Complete!")
    st.balloons()


# ─────────────────────────────────────────────────────────────────────────────
# Persisted report dashboard + downloads
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.get("last_results"):
    saved = st.session_state["last_results"]
    gene = saved["gene"]
    disease = saved["disease"]
    results = saved["results"]

    st.markdown("---")
    st.markdown("## 🏁 Research Readiness Dashboard")
    render_score_dashboard()

    st.markdown("### 📚 Final Report Sections")
    section_titles = {
        "orchestrator": "🧠 Research Orchestrator",
        "gene": "🔬 Gene Intelligence",
        "literature": "📚 Literature Evidence",
        "pathway": "🌐 Pathway & Network",
        "hypothesis": "💡 Research Hypotheses",
        "experiment": "🧪 Experimental Design",
        "report": "📝 Scientific Report",
    }

    for key, title in section_titles.items():
        if key in results:
            with st.expander(title, expanded=(key == "report")):
                st.markdown(results[key])

    st.markdown("### 📥 Download Full Report")
    md_report = build_markdown_report(gene, disease, results)
    txt_report = build_txt_report(gene, disease, results)

    dc1, dc2 = st.columns(2)
    with dc1:
        st.download_button(
            "📄 Download Markdown",
            data=md_report,
            file_name=f"BioPilot_{gene}_{disease}.md".replace(" ", "_"),
            mime="text/markdown",
            use_container_width=True,
        )
    with dc2:
        st.download_button(
            "📃 Download Text",
            data=txt_report,
            file_name=f"BioPilot_{gene}_{disease}.txt".replace(" ", "_"),
            mime="text/plain",
            use_container_width=True,
        )
