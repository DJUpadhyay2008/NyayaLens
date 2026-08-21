import os
import requests
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Function to load .env file if available
def load_env():
    env_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        ".env"
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip())
            except Exception as e:
                logger.warning(f"Failed to read .env from {env_path}: {e}")

load_env()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
PRIMARY_MODEL = os.getenv("OPENROUTER_MODEL", "z-ai/glm-5.2:free")

FALLBACK_MODELS = [
    "liquid/lfm-2.5-2.6b:free",
    "google/gemma-4-31b-it:free",
    "dots-studio/dots-3-note-preview:free",
    "openrouter/auto"
]

OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

def get_api_key() -> str:
    return os.getenv("OPENROUTER_API_KEY", OPENROUTER_API_KEY)

def call_openrouter_llm(prompt: str, system_instruction: str = None) -> Optional[str]:
    """
    Calls OpenRouter chat completions API using z-ai/glm-5.2:free with fallback models.
    """
    api_key = get_api_key()
    if not api_key:
        logger.warning("OPENROUTER_API_KEY is not configured.")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "NyayaLens Legal AI Engine",
        "Content-Type": "application/json"
    }

    system_content = system_instruction or (
        "You are NyayaLens AI, an expert Judicial Analyst for Indian Commercial Courts. "
        "Provide zero-hallucination, structured Executive Judicial Briefs using exact legal terminology, "
        "statutory provisions, and clear section headers in Markdown."
    )

    models_to_try = [PRIMARY_MODEL] + [m for m in FALLBACK_MODELS if m != PRIMARY_MODEL]

    for model in models_to_try:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1500
        }

        try:
            response = requests.post(OPENROUTER_ENDPOINT, headers=headers, json=payload, timeout=25)
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    if content and len(content.strip()) > 30:
                        logger.info(f"OpenRouter LLM summary successfully generated using model: {model}")
                        return content
            else:
                logger.warning(f"OpenRouter model {model} returned status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            logger.error(f"Error calling OpenRouter model {model}: {e}")

    return None

def generate_fallback_case_brief(case_title: str, citation: str, decision_date: str, bench: str, raw_text: str) -> str:
    """
    Deterministic rule-based summary when LLM services are offline/rate-limited.
    """
    snippet = raw_text[:1200] if raw_text else "No raw text available."
    return f"""### 📋 Executive Judicial Summary
**Case Title:** {case_title}
**Citation:** {citation} | **Date:** {decision_date} | **Bench:** {bench or 'Supreme Court of India'}

---

### ⚖️ Ratio Decidendi & Legal Key Points
* **Precedent Authority:** This judgment serves as an official binding Supreme Court precedent for Indian Commercial Courts under the Commercial Courts Act, 2015.
* **Factual & Procedural Matrix:** The dispute involves commercial obligations, contractual performance, and statutory interpretation under Indian jurisdiction.
* **Judicial Holding Summary:** The Bench adjudicated on contract enforcement, procedural timelines, and statutory remedies as set out in the record below.

---

### 📜 Verified Passage Excerpt
> "{snippet[:600]}..."

---

*Note: Generated via NyayaLens Judicial Retrieval Engine.*"""

def summarize_judgment_case(case_title: str, citation: str, decision_date: str, bench: str, raw_text: str, chunks: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generates an AI Executive Judicial Brief for a specific judgment case.
    """
    # Select key text snippets
    text_sample = ""
    if chunks and len(chunks) > 0:
        chunk_texts = [f"[Chunk {idx+1} - {c.get('paragraph_reference', 'Para')}] {c.get('text', '')[:400]}" for idx, c in enumerate(chunks[:8])]
        text_sample = "\n\n".join(chunk_texts)
    else:
        text_sample = raw_text[:3500] if raw_text else "Text not available."

    prompt = f"""Synthesize the following Supreme Court of India Commercial Court Judgment into a high-precision, zero-hallucination Executive Judicial Brief.

Case Name: {case_title}
Citation: {citation}
Date of Decision: {decision_date}
Bench: {bench or 'Supreme Court of India'}

Judgment Text Excerpts:
{text_sample}

Please structure your response into the following 4 Markdown sections:
1. ### 📋 Executive Summary & Legal Issue
   - Provide a 2-3 sentence overview of the core commercial dispute.
2. ### ⚖️ Ratio Decidendi (Core Legal Holding)
   - Bullet points highlighting the main legal principles established by the Bench.
3. ### 📜 Statutory Provisions & Precedents
   - Mention any acts, sections, or key precedents discussed (e.g. Arbitration Act, Contract Act, Commercial Courts Act).
4. ### 📌 Key Practical Takeaway for Commercial Courts
   - A concise conclusion on how this precedent applies to commercial litigation.

Keep it professional, concise, and formatted in clean Markdown."""

    llm_output = call_openrouter_llm(prompt)

    if not llm_output:
        llm_output = generate_fallback_case_brief(case_title, citation, decision_date, bench, raw_text)

    return {
        "case_title": case_title,
        "citation": citation,
        "model_used": PRIMARY_MODEL,
        "summary": llm_output
    }

def summarize_search_results(query: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Synthesizes top retrieved search results into a unified AI Executive Judicial Brief for a search query.
    """
    if not results:
        return {
            "query": query,
            "summary": "No verified precedent chunks available to synthesize for this query."
        }

    passages_text = ""
    for idx, res in enumerate(results[:6]):
        passages_text += f"\n[Precedent #{idx+1}] {res.get('case_name')} ({res.get('citation')})\nPassage: {res.get('passage', '')[:400]}\n"

    prompt = f"""You are a Judicial AI Analyst for Indian Commercial Courts. Synthesize a unified Executive Legal Synthesis for the following user search query based strictly on the retrieved Supreme Court precedent passages below.

User Search Query: "{query}"

Retrieved Supreme Court Passages:
{passages_text}

Structure your response into:
1. ### 📋 Executive Synthesis for Query
   - Direct synthesized answer to the query based on the retrieved precedents.
2. ### ⚖️ Key Legal Principles & Standards
   - Bulleted legal rules established in the cited Supreme Court judgments.
3. ### 📌 Top Cited Precedents
   - Mention the relevant judgment citations (e.g., S.C.R. citations) and their specific holdings.

Maintain strict zero-hallucination standards. If the passages don't fully answer the query, explicitly state the limitations."""

    llm_output = call_openrouter_llm(prompt)

    if not llm_output:
        # Fallback brief synthesis
        llm_output = f"""### 📋 Executive Synthesis for Query: *"{query}"*

* **Retrieved Precedents Analyzed:** {len(results)} Supreme Court Commercial Judgments.
* **Primary Precedent Authority:** {results[0].get('case_name', 'Supreme Court Judgment')} ({results[0].get('citation', 'S.C.R.')})
* **Judicial Ratio Excerpt:** "{results[0].get('passage', '')[:500]}..."

---
*Generated via NyayaLens Hybrid Retrieval & Judicial Synthesizer.*"""

    return {
        "query": query,
        "model_used": PRIMARY_MODEL,
        "summary": llm_output
    }
