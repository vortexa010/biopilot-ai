import streamlit as st
from agents import run_biopilot

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BioPilot AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .stApp { background-color: #0f1117; color: #e0e0e0; }
    .hero-title {
        font-size: 3rem; font-weight: 800;
        background: linear-gradient(135deg, #00d4ff, #7b2ff7);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 0.2rem;
    }
    .hero-sub {
        text-align: center; color: #888; font-size: 1.1rem; margin-bottom: 2rem;
    }
    .agent-card {
        background: #1a1d27; border: 1px solid #2a2d3a;
        border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.8rem;
    }
    .agent-label {
        font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 1px; color: #00d4ff; margin-bottom: 0.3rem;
    }
    .agent-content { color: #d0d0d0; font-size: 0.95rem; line-height: 1.6; }
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff, #7b2ff7);
        color: white; border: none; border-radius: 8px;
        padding: 0.6rem 2rem; font-weight: 700; font-size: 1rem;
        width: 100%; margin-top: 0.5rem;
    }
    .stTextInput > div > div > input,
    .stSelectbox > div > div { background-color: #1a1d27; color: #e0e0e0; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🧬 BioPilot AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Your Autonomous Biomedical Research Co-Scientist</div>',
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    api_key = st.text_input("Anthropic API Key", type="password",
                            help="Get yours at console.anthropic.com")
    st.markdown("---")
    st.markdown("### 📖 How to use")
    st.markdown("""
1. Enter your API key above
2. Type a gene name & disease
3. Click **Run BioPilot**
4. Review the 4-agent report
""")
    st.markdown("---")
    st.markdown("### 🤖 Agents")
    st.markdown("""
- 🔬 **Gene Analyst** — biology & function  
- 📚 **Literature Agent** — known evidence  
- 💡 **Hypothesis Agent** — novel ideas  
- 🧪 **Experiment Agent** — validation plan
""")
    st.markdown("---")
    st.caption("Built with GitHub Copilot · Powered by Claude AI")

# ── Main Input ────────────────────────────────────────────────────────────────
st.markdown("### 🔍 Research Query")

col1, col2 = st.columns(2)
with col1:
    gene = st.text_input("Gene / lncRNA of interest",
                         placeholder="e.g. MALAT1, BRCA1, TP53")
with col2:
    disease = st.text_input("Disease / condition",
                            placeholder="e.g. Lung Adenocarcinoma, Breast Cancer")

custom_query = st.text_area(
    "Or describe your research question (optional)",
    placeholder="e.g. I discovered a novel lncRNA upregulated in TCGA-LUAD. Help me design a research study.",
    height=80,
)

run_btn = st.button("🚀 Run BioPilot", use_container_width=True)

# ── Results ───────────────────────────────────────────────────────────────────
if run_btn:
    if not api_key:
        st.error("⚠️ Please enter your Anthropic API key in the sidebar.")
        st.stop()
    if not gene and not custom_query:
        st.error("⚠️ Please enter a gene name or a research question.")
        st.stop()

    query = custom_query if custom_query else f"{gene} in {disease}"

    st.markdown("---")
    st.markdown(f"### 🧬 Research Report: *{query}*")
    st.markdown("*Four specialized agents are analyzing your query...*")

    agents_config = [
        ("🔬 Gene Analyst", "gene"),
        ("📚 Literature Agent", "literature"),
        ("💡 Hypothesis Agent", "hypothesis"),
        ("🧪 Experiment Agent", "experiment"),
    ]

    for label, agent_type in agents_config:
        with st.spinner(f"{label} is thinking..."):
            result = run_biopilot(api_key, agent_type, query)

        st.markdown(f"""
<div class="agent-card">
  <div class="agent-label">{label}</div>
  <div class="agent-content">{result}</div>
</div>
""", unsafe_allow_html=True)

    st.success("✅ BioPilot analysis complete!")
    st.balloons()