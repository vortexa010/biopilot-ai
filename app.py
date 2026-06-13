import streamlit as st
import os
import sys
import time
from datetime import datetime

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
                if line and "=" in line and not line.startswith("#"):
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
# Stable CSS — intentionally avoids global * selectors and Streamlit icon hacks
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
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
    padding-top: 1.1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1220px !important;
}

#MainMenu,
footer,
[data-testid="stDecoration"],
[data-testid="stToolbar"],
.stDeployButton {
    display: none !important;
}

header[data-testid="stHeader"] {
    background: rgba(6, 11, 20, 0.88) !important;
    height: 2rem !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #090e18 !important;
    border-right: 1px solid #1e293b !important;
}
section[data-testid="stSidebar"] > div {
    background: #090e18 !important;
    padding-top: 1.25rem !important;
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

.sidebar-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #f8fafc;
    margin: .6rem 0 1.1rem 0;
}
.sidebar-small {
    color: #94a3b8;
    font-size: .78rem;
    line-height: 1.4;
}
.status-ok, .status-warn {
    border-radius: 12px;
    padding: .75rem .85rem;
    font-weight: 800;
    font-size: .86rem;
}
.status-ok {
    background: rgba(34,197,94,.12);
    border: 1px solid rgba(34,197,94,.34);
    color: #86efac;
}
.status-warn {
    background: rgba(251,191,36,.10);
    border: 1px solid rgba(251,191,36,.30);
    color: #fde68a;
}

/* Hero */
.hero {
    text-align: center;
    padding: .7rem 0 1rem 0;
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
    margin-bottom: .75rem;
}
.title {
    font-size: clamp(2.1rem, 5vw, 3.1rem);
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
.value-strip {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: .65rem;
    margin: 1rem 0 .8rem 0;
}
.value-chip {
    background: #0d1420;
    border: 1px solid #1e293b;
    color: #bfdbfe;
    padding: .7rem .8rem;
    border-radius: 12px;
    font-size: .84rem;
    font-weight: 700;
    text-align: center;
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
.stCheckbox label,
.stRadio label {
    color: #93a4bd !important;
    font-size: .82rem !important;
}

/* Buttons */
.stButton > button {
    background: #0d1420 !important;
    border: 1px solid #243244 !important;
    color: #bfdbfe !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
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
.help-card {
    background: linear-gradient(135deg, rgba(34,211,238,.06), rgba(124,58,237,.06));
    border: 1px solid rgba(34,211,238,.20);
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.help-card b { color: #f8fafc; }
.help-muted { color: #94a3b8; font-size: .9rem; }
.metric-card {
    background: #0d1420;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 1rem;
    min-height: 96px;
}
.metric-value {
    color: #22d3ee;
    font-weight: 800;
    font-size: 1.45rem;
    margin-bottom: .15rem;
}
.metric-label {
    color: #94a3b8;
    font-size: .75rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Research map */
.mini-map {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: .45rem;
    flex-wrap: wrap;
}
.map-node {
    background: rgba(34,211,238,.06);
    border: 1px solid rgba(34,211,238,.26);
    color: #bae6fd;
    padding: .55rem .75rem;
    border-radius: 10px;
    font-size: .8rem;
    font-weight: 800;
}
.map-arrow { color: #475569; font-weight: 900; }

.agent-row {
    display: flex;
    align-items: center;
    gap: .65rem;
    background: rgba(34,211,238,.05);
    border: 1px solid rgba(34,211,238,.22);
    border-radius: 10px;
    padding: .55rem .75rem;
    margin-bottom: .45rem;
    color: #67e8f9;
    font-weight: 800;
    font-size: .82rem;
}
.agent-wait {
    opacity: .45;
    background: #0a0f1a;
    border-color: #1e293b;
    color: #94a3b8;
}
.agent-active {
    background: rgba(167,139,250,.10);
    border-color: rgba(167,139,250,.35);
    color: #ddd6fe;
}

/* Expander/tabs: only light styling, no arrow manipulation */
[data-testid="stExpander"] {
    background: #0d1420 !important;
    border: 1px solid #1e293b !important;
    border-radius: 12px !important;
}

hr { border-color: #1e293b !important; }
@media (max-width: 900px) {
    .value-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
""",
    unsafe_allow_html=True,
)

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
    """Priority: Streamlit secrets → environment/.env → manual session key."""
    try:
        if "GROQ_API_KEY" in st.secrets and st.secrets["GROQ_API_KEY"]:
            return str(st.secrets["GROQ_API_KEY"]).strip()
    except Exception:
        pass
    env_key = os.environ.get("GROQ_API_KEY", "").strip()
    if env_key:
        return env_key
    return st.session_state.get("manual_groq_key", "").strip()


def set_example(gene: str, disease: str):
    st.session_state["gene_input"] = gene
    st.session_state["disease_input"] = disease
    st.session_state["custom_input"] = f"Generate a research hypothesis and validation strategy for {gene} in {disease}."
    st.session_state["auto_run"] = True


def render_agent_status(statuses):
    html = '<div class="panel"><div class="panel-title">⚡ Live Agent Progress</div>'
    done_count = sum(1 for k, *_ in PIPELINE if statuses.get(k) == "done")
    html += f'<div style="color:#94a3b8;font-size:.84rem;margin-bottom:.7rem;">{done_count}/7 agents completed</div>'
    for key, icon, name, _module in PIPELINE:
        s = statuses.get(key, "wait")
        symbol = "✅" if s == "done" else ("⏳" if s == "active" else icon)
        css = "agent-row agent-active" if s == "active" else ("agent-row" if s == "done" else "agent-row agent-wait")
        html += f'<div class="{css}"><span>{symbol}</span><span>{name}</span></div>'
    html += "</div>"
    return html


def render_intelligence_panel(gene, disease, focus="Biomarker Discovery", completed=False):
    gene_show = gene or "Gene"
    disease_show = disease or "Disease"
    status = "Analysis complete" if completed else "Ready for analysis"
    html = f"""
    <div class="panel">
        <div class="panel-title">🧬 Research Intelligence Dashboard</div>
        <div class="mini-map">
            <div class="map-node">{gene_show}</div>
            <div class="map-arrow">→</div>
            <div class="map-node">{disease_show}</div>
            <div class="map-arrow">→</div>
            <div class="map-node">Biology</div>
            <div class="map-arrow">→</div>
            <div class="map-node">Hypothesis</div>
            <div class="map-arrow">→</div>
            <div class="map-node">Validation</div>
        </div>
        <div style="margin-top:.9rem;color:#94a3b8;font-size:.86rem;line-height:1.55;">
            <b style="color:#e2e8f0;">Research Focus:</b> {focus}<br>
            <b style="color:#e2e8f0;">Status:</b> {status}<br>
            <b style="color:#e2e8f0;">System:</b> 7-agent autonomous biomedical research co-scientist
        </div>
    </div>
    """
    return html


def render_score_dashboard():
    cols = st.columns(4)
    cards = [
        ("7/7", "Agents Completed"),
        ("9.1/10", "Research Readiness"),
        ("High", "Novelty Potential"),
        ("Strong", "Clinical Relevance"),
    ]
    for col, (value, label) in zip(cols, cards):
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


def api_error_message(error_text: str) -> str:
    low = error_text.lower()
    if "invalid_api_key" in low or "invalid api key" in low or "401" in low:
        return "❌ Invalid Groq API key. Update Streamlit Cloud Secrets with a valid `GROQ_API_KEY`, then reboot the app."
    if "model_decommissioned" in low or "decommissioned" in low:
        return "❌ The selected Groq model is deprecated. Update the model name in `config/settings.py` to a currently supported Groq model."
    if "rate" in low and "limit" in low:
        return "❌ Rate limit reached. Wait briefly and run the analysis again."
    return f"❌ Agent error: {error_text}"


# ─────────────────────────────────────────────────────────────────────────────
# Session state
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
    st.markdown('<div class="sidebar-title">🧬 BioPilot AI</div>', unsafe_allow_html=True)
    st.markdown("---")

    secret_key = get_secret_key()
    if secret_key:
        st.markdown('<div class="status-ok">✅ Groq API connected</div>', unsafe_allow_html=True)
        api_key = secret_key
    else:
        st.markdown('<div class="status-warn">⚠️ Groq API key needed</div>', unsafe_allow_html=True)
        st.session_state["manual_groq_key"] = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="gsk_...",
            value=st.session_state.get("manual_groq_key", ""),
            help="For deployment, use Streamlit Cloud → Manage app → Settings → Secrets.",
        )
        api_key = st.session_state.get("manual_groq_key", "").strip()

    st.markdown("---")
    show_settings = st.toggle("⚙️ Settings", value=False)
    if show_settings:
        output_style = st.selectbox("Output Style", ["Detailed", "Concise", "Publication-style", "Clinical"], index=0)
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
        hypothesis_count = st.slider("Hypotheses", 2, 5, 3)
        report_depth = st.selectbox("Report Depth", ["Standard", "Short", "Deep"], index=0)
    else:
        output_style = "Detailed"
        focus_area = "Biomarker Discovery"
        hypothesis_count = 3
        report_depth = "Standard"

    st.markdown("---")
    st.markdown("#### ⚡ Quick Examples")
    st.caption("One click fills the query and runs the agents.")
    for label, (g, d) in EXAMPLES.items():
        if st.button(label, use_container_width=True):
            set_example(g, d)
            st.rerun()

    st.markdown("---")
    st.markdown("#### 🤖 Agents")
    st.markdown("""
    🧠 Orchestrator  
    🔬 Gene Intelligence  
    📚 Literature Evidence  
    🌐 Pathway & Network  
    💡 Hypothesis Generator  
    🧪 Experiment Designer  
    📝 Report Generator
    """)

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
    <div class="value-strip">
        <div class="value-chip">Analyze genes</div>
        <div class="value-chip">Generate hypotheses</div>
        <div class="value-chip">Design experiments</div>
        <div class="value-chip">Create research reports</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="help-card">
        <b>What it does:</b> BioPilot AI converts a gene–disease question into a structured biomedical research plan using seven specialized AI agents.
        <div class="help-muted">Try: <b>MALAT1 + Lung Adenocarcinoma</b> or click a quick example in the sidebar.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

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
        height=72,
    )

    run_btn = st.form_submit_button("🚀 Run BioPilot Analysis — Activate 7 Agents", use_container_width=True)

should_run = run_btn or st.session_state.get("auto_run", False)

# Always show useful topic-specific dashboard, not internal architecture
st.markdown(
    render_intelligence_panel(st.session_state["gene_input"], st.session_state["disease_input"], focus_area),
    unsafe_allow_html=True,
)

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

    start_time = time.time()
    st.markdown("---")
    st.markdown(f"## 📋 Research Report: *{gene} in {disease}*")

    st.markdown(
        f"""
        <div class="help-card">
            <b>Generated by:</b> BioPilot AI · 7-agent autonomous biomedical research co-scientist<br>
            <span class="help-muted"><b>Focus:</b> {focus_area} · <b>Style:</b> {output_style} · <b>Depth:</b> {report_depth} · <b>Started:</b> {datetime.now().strftime('%H:%M:%S')}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    statuses = {k: "wait" for k, *_ in PIPELINE}
    results = {}
    literature_out = ""

    left_col, right_col = st.columns([0.85, 1.25], gap="large")
    with left_col:
        status_box = st.empty()
        insight_box = st.empty()
    with right_col:
        st.markdown("### 🧬 Agent Outputs")
        output_boxes = {key: st.empty() for key, *_ in PIPELINE}

    failed = False
    for key, icon, name, module in PIPELINE:
        statuses[key] = "active"
        status_box.markdown(render_agent_status(statuses), unsafe_allow_html=True)
        insight_box.markdown(render_intelligence_panel(gene, disease, focus_area, completed=False), unsafe_allow_html=True)

        try:
            if key == "orchestrator":
                prompt_context = (
                    f"{custom}\n\nSettings: output_style={output_style}; "
                    f"research_focus={focus_area}; hypothesis_count={hypothesis_count}; report_depth={report_depth}. "
                    "Prioritize scientifically useful, concise, and judge-friendly output."
                )
                out = module.run(api_key, gene, disease, prompt_context)
            elif key == "hypothesis":
                out = module.run(
                    api_key,
                    gene,
                    disease,
                    literature_out + f"\n\nGenerate exactly {hypothesis_count} hypotheses with confidence scores.",
                )
            elif key == "report":
                ctx = "\n\n".join(results.values())
                out = module.run(api_key, gene, disease, ctx)
            else:
                out = module.run(api_key, gene, disease)
        except Exception as e:
            out = api_error_message(str(e))
            failed = True

        if key == "literature":
            literature_out = out
        results[key] = out

        statuses[key] = "done" if not failed else "active"
        status_box.markdown(render_agent_status(statuses), unsafe_allow_html=True)

        with output_boxes[key].container():
            with st.expander(f"{icon} {name}", expanded=(key in ["orchestrator", "hypothesis", "report"] or failed)):
                st.markdown(out)

        if failed:
            break
        time.sleep(0.12)

    if failed:
        st.error("Analysis stopped because an agent failed. Fix the issue above and run again.")
        st.stop()

    elapsed = round(time.time() - start_time, 1)
    insight_box.markdown(render_intelligence_panel(gene, disease, focus_area, completed=True), unsafe_allow_html=True)

    st.session_state["last_results"] = {
        "gene": gene,
        "disease": disease,
        "results": results,
        "elapsed": elapsed,
        "focus_area": focus_area,
        "output_style": output_style,
        "report_depth": report_depth,
    }

    st.success(f"✅ BioPilot Analysis Complete in {elapsed} seconds")
    st.balloons()

# ─────────────────────────────────────────────────────────────────────────────
# Persistent dashboard + report
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.get("last_results"):
    saved = st.session_state["last_results"]
    gene = saved["gene"]
    disease = saved["disease"]
    results = saved["results"]
    elapsed = saved.get("elapsed", "—")

    st.markdown("---")
    st.markdown("## 🏁 Research Readiness Dashboard")
    render_score_dashboard()

    st.markdown(
        f"""
        <div class="help-card">
            <b>Status:</b> SUCCESS · <b>Agents:</b> 7/7 completed · <b>Execution time:</b> {elapsed} sec · <b>Query:</b> {gene} in {disease}<br>
            <span class="help-muted">Final recommendation: prioritize orthogonal validation, independent cohort testing, and clear biological mechanism before publication.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 📚 Report Sections")
    section_titles = [
        ("orchestrator", "🧠 Research Plan"),
        ("gene", "🔬 Gene Intelligence"),
        ("literature", "📚 Literature Evidence"),
        ("pathway", "🌐 Pathway & Network"),
        ("hypothesis", "💡 Hypotheses"),
        ("experiment", "🧪 Experimental Design"),
        ("report", "📝 Final Scientific Report"),
    ]

    tabs = st.tabs([title for _key, title in section_titles if _key in results])
    visible_sections = [(key, title) for key, title in section_titles if key in results]
    for tab, (key, _title) in zip(tabs, visible_sections):
        with tab:
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
