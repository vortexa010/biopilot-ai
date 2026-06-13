# 🧬 BioPilot AI

> **AI Research Copilot for Biomedical Discovery**
>
> Transform a single **gene + disease query** into a complete biomedical research proposal using multiple AI agents.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![Groq](https://img.shields.io/badge/Groq-LLM-green)
![Hackathon](https://img.shields.io/badge/Microsoft-Agents%20League%202026-purple)

---

#   BioPilot AI in Action

##  Home Interface

![Home](assets/home.png)

---

##  7-Agent Research Pipeline

![Pipeline](assets/pipeline.png)

---

## Generated Research Report

![Report](assets/report.png)

---

## 🎥 Demo

Watch BioPilot AI transform a single gene and disease query into a complete biomedical research proposal.

(Video Link)


#  Overview

BioPilot AI is an autonomous multi-agent biomedical research platform designed to accelerate early-stage scientific discovery.

Instead of acting as a chatbot, BioPilot AI functions as an AI research collaborator capable of generating structured biomedical research proposals from a simple gene-disease query.

Example:

Gene:
MALAT1

Disease:
Lung Adenocarcinoma (LUAD)

↓

BioPilot AI generates:

- Gene intelligence
- Literature synthesis
- Pathway analysis
- Scientific hypotheses
- Experimental design
- Publication-ready research proposal

---

## Why BioPilot?

Traditional AI chatbots answer questions.

BioPilot AI performs structured scientific reasoning through seven specialized AI agents that collaboratively generate a publication-style biomedical research proposal.

It acts as an autonomous research co-scientist rather than a conversational assistant.


# Features

✅ Multi-agent AI architecture

✅ Gene intelligence analysis

✅ Literature evidence synthesis

✅ Biological pathway exploration

✅ Novel hypothesis generation

✅ Experimental design suggestions

✅ Publication-style research report

✅ Export reports

---

# 7-Agent Architecture

```
User Query
      │
      ▼
Research Orchestrator
 ┌────┼─────┐
 │    │     │
Gene Literature Pathway
      │
      ▼
Hypothesis
      ▼
Experiment
      ▼
Scientific Report

```

Each AI agent specializes in a different stage of biomedical research and collaborates to generate a comprehensive research proposal.

---

# Example Workflow

Input

Gene:
TP53

Disease:
Breast Cancer

↓

Output

- Biological function analysis
- Literature evidence
- Pathway interactions
- Novel hypotheses
- Experimental workflow
- Expected outcomes
- Future directions
- Publication-ready report

---

# 🛠 Technology Stack

- Python
- Streamlit
- Groq API
- Llama Models
- Markdown Report Generation
- Multi-Agent Prompt Engineering

---

# 🎯 Use Cases

- Biomedical research planning
- Biomarker discovery
- lncRNA research
- Cancer genomics
- Graduate students
- PhD researchers
- Research proposal generation
- Hypothesis generation

---

## Key Innovation

Instead of relying on one general-purpose LLM, BioPilot AI coordinates seven specialized AI agents that independently analyze biological context, literature evidence, pathways, hypotheses, experimental design, and reporting before synthesizing a unified research proposal.


# ⚡ Running Locally

Clone repository

```bash
git clone https://github.com/YOUR_USERNAME/biopilot-ai.git
```

Move into project

```bash
cd biopilot-ai
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
streamlit run app.py
```

---

# 📈 Future Roadmap

- PubMed API integration
- GEO/TCGA dataset integration
- Protein structure analysis
- RAG-based literature retrieval
- Citation generation
- PDF export
- Multi-gene analysis
- Knowledge graph visualization

---

# 🏆 Built For

**Microsoft Agents League Hackathon 2026**

An autonomous AI platform designed to assist biomedical researchers through collaborative multi-agent reasoning.

---

# 👨‍💻 Author

**Vaishnavi Mangam**

Master's Student in Bioinformatics

Research interests:

- Cancer Genomics
- lncRNA Biology
- AI for Biomedical Research
- Multi-Agent Systems

---

# ⚠️ Disclaimer

BioPilot AI is intended for research and educational purposes only.

It does not provide medical diagnosis, clinical recommendations, or treatment advice.

All generated outputs should be independently validated by qualified researchers and domain experts.
