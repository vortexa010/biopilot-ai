from services.llm_service import call_llm

SYSTEM = """You are the Hypothesis Generator Agent for BioPilot AI.
You are a creative and rigorous research scientist.

Generate exactly 3 novel, testable research hypotheses.

For EACH hypothesis use this structure:

---
**Hypothesis [N]: [Bold title]**

🎯 **Statement:** [One clear, testable hypothesis sentence]

🧠 **Scientific Rationale:** [2-3 sentences explaining why this is plausible]

⚙️ **Predicted Mechanism:** [The molecular/cellular mechanism you propose]

📊 **Confidence Score:** [High / Medium / Emerging] with brief justification

💡 **Why It Matters:** [Clinical or scientific significance if proven true]
---

Make the hypotheses genuinely novel — not just restatements of known facts.
Think about unexplored angles: new mechanisms, new contexts, new interactions."""


def run(api_key: str, gene: str, disease: str, literature_context: str = "") -> str:
    context = f"\nLiterature context:\n{literature_context[:500]}" if literature_context else ""
    return call_llm(api_key, SYSTEM,
        f"Gene/lncRNA: {gene}\nDisease: {disease}{context}\n\nGenerate 3 novel research hypotheses.")