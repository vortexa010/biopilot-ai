from groq import Groq
from config.settings import GROQ_MODEL, MAX_TOKENS, TEMPERATURE


def call_llm(api_key: str, system_prompt: str, user_message: str) -> str:
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        return response.choices[0].message.content

    except Exception as e:
        err = str(e)
        if "invalid_api_key" in err or "auth" in err.lower():
            return "❌ Invalid API key. Please check your Groq API key."
        elif "rate_limit" in err.lower():
            return "❌ Rate limit reached. Please wait and try again."
        elif "decommissioned" in err or "model" in err.lower():
            return "❌ Model error. Open config/settings.py and change GROQ_MODEL."
        else:
            return f"❌ Error: {err}"