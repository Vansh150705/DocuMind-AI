"""
utils/ai_helpers.py
All LLM-related helpers: prompt building, DNA generation,
language detection, and chat export formatting.
"""

import re
import json
import datetime


def build_prompt(question, context, history, mode, persona, language):
    """Builds the full prompt string sent to the LLM."""
    history_text = ""
    for msg in history[-6:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    mode_instructions = {
        "qa":        "Answer STRICTLY based on the document context. If not found, say so clearly. Never fabricate.",
        "eli5":      "Explain like the user is 10 years old. Use simple words and fun analogies.",
        "executive": "Write for a busy CEO. Be extremely concise. Use bullet points. Lead with the most important insight.",
        "debate":    "Present BOTH sides of any claim in the document. Challenge assumptions. Be intellectually rigorous."
    }

    persona_instructions = {
        "default":   "",
        "lawyer":    "You are an experienced lawyer. Analyze from a legal perspective, flag risks, use precise legal language.",
        "doctor":    "You are a medical doctor. Analyze from a clinical perspective, use appropriate medical terminology.",
        "financial": "You are a senior financial analyst. Focus on financial implications, risks, ROI, and business impact.",
        "teacher":   "You are a patient teacher. Break down concepts clearly with examples and step-by-step explanations.",
        "journalist":"You are an investigative journalist. Look for the key story, surprising facts, and what's unsaid."
    }

    lang_instruction = f"IMPORTANT: Respond in {language} language." if language != "English" else ""

    return f"""You are DocuMind AI. {persona_instructions.get(persona, '')} {mode_instructions.get(mode, mode_instructions['qa'])} {lang_instruction}

Conversation history:
{history_text}

Document context:
{context}

Question: {question}
Answer:"""


def generate_document_dna(text, llm):
    """
    Sends a structured JSON prompt to Gemini to extract document metadata.
    Returns a parsed dict or None on failure.
    """
    sample = text[:3000]
    prompt = f"""Analyze this document and return ONLY a valid JSON object (no markdown, no backticks):
{{"title":"inferred title","domain":"e.g. Medical/Legal/Technical/Academic/Business","tone":"e.g. Formal/Conversational/Academic/Persuasive","complexity":75,"sentiment":60,"informativeness":85,"key_themes":["t1","t2","t3","t4","t5"],"key_entities":["e1","e2","e3"],"one_line_summary":"one sentence","unusual_insight":"one surprising insight","language":"detected language"}}
complexity, sentiment (0=negative,100=positive), informativeness are 0-100.
Document: {sample}"""

    response = llm.invoke(prompt)
    raw = re.sub(r"```json|```", "", response.content.strip()).strip()
    try:
        return json.loads(raw)
    except Exception:
        return None


def detect_language(text, llm):
    """Detects the primary language of a text sample."""
    sample = text[:500]
    prompt = f"Detect the language of this text. Reply with ONLY the language name in English (e.g. Hindi, French). Text: {sample}"
    try:
        return llm.invoke(prompt).content.strip()
    except Exception:
        return "English"


def generate_chat_export(chat_history, pdf_names, dna):
    """Formats the chat history as a plain-text export string."""
    lines = [
        "=" * 60,
        "DOCUMIND AI — CHAT EXPORT",
        f"Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Documents: {', '.join(pdf_names)}"
    ]
    if dna:
        lines += [
            f"Document: {dna.get('title', '—')}",
            f"Summary: {dna.get('one_line_summary', '—')}"
        ]
    lines += ["=" * 60, ""]

    for i, msg in enumerate(chat_history):
        if msg["role"] == "user":
            lines.append(f"Q{(i // 2) + 1}: {msg['content']}")
        else:
            lines.append(f"A: {msg['content']}")
            if msg.get("sources"):
                lines.append(f"   Sources: {', '.join(msg['sources'])}")
            if msg.get("confidence"):
                lines.append(f"   Confidence: {msg['confidence']}%")
            lines.append("")

    return "\n".join(lines)


def get_analytics(chat_history):
    """Computes session analytics from chat history."""
    questions = [m for m in chat_history if m["role"] == "user"]
    answers   = [m for m in chat_history if m["role"] == "assistant"]
    confs     = [m.get("confidence", 0) for m in answers if m.get("confidence")]
    avg_conf  = int(sum(confs) / len(confs)) if confs else 0

    all_words = []
    for q in questions:
        all_words.extend(re.findall(r'\b[a-zA-Z]{4,}\b', q["content"].lower()))

    stopwords = {
        "what","this","that","with","from","have","about","which",
        "when","where","does","your","their","will","been","were","they","them"
    }
    word_freq = {}
    for w in all_words:
        if w not in stopwords:
            word_freq[w] = word_freq.get(w, 0) + 1

    return {
        "total_q":   len(questions),
        "avg_conf":  avg_conf,
        "high_conf": sum(1 for c in confs if c > 60),
        "low_conf":  sum(1 for c in confs if c <= 30),
        "top_words": sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5],
        "confs":     confs
    }
