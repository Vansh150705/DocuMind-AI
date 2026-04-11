"""
utils/agents.py
Agentic AI features:
  1. Clarification Agent  — detects vague queries before retrieval
  2. Self-Reflection      — reviews and improves its own answers
  3. Confidence Adapter   — adapts response based on confidence score
"""

import re


# ============================================================
# AGENT 1: CLARIFICATION AGENT
# Intercepts vague queries BEFORE retrieval (rule-based, zero LLM cost)
# ============================================================

VAGUE_PATTERNS = [
    r'^(explain|tell me|describe|what|how|why|summarize|summary|info|information|details?|more|elaborate|go on|continue|and\??)$',
    r'^(explain this|tell me more|what does this mean|what is this|describe this|elaborate on this)$',
    r'^(yes|no|ok|okay|sure|fine|alright|got it|i see|hmm|hm)$',
]


def is_vague_query(question: str) -> bool:
    """Returns True if the query is too vague to retrieve meaningfully."""
    q = question.strip().lower().rstrip("?.!")
    if len(q.split()) <= 2:
        return True
    for pattern in VAGUE_PATTERNS:
        if re.fullmatch(pattern, q, re.IGNORECASE):
            return True
    return False


def get_clarification_question(question: str) -> str:
    """Returns a targeted clarifying question based on the vague input."""
    q = question.strip().lower()
    if any(w in q for w in ["explain", "describe", "elaborate"]):
        return "Could you be more specific? What aspect or topic would you like me to explain from the document?"
    if any(w in q for w in ["summarize", "summary"]):
        return "Would you like a full document summary, or a summary of a specific section or topic?"
    if any(w in q for w in ["what", "how", "why"]):
        return "Could you complete your question? What specifically would you like to know about the document?"
    return "Your question seems a bit broad. Could you provide more details about what you're looking for in this document?"


# ============================================================
# AGENT 2: SELF-REFLECTION
# Reviews initial answer and improves it if needed (second LLM pass)
# ============================================================

def self_reflect_and_improve(question: str, context: str, initial_answer: str, llm) -> str:
    """
    Sends a second prompt to the LLM asking it to review its own answer.
    If the answer is good → returns the original.
    If it has gaps → returns an improved version.
    Only runs for answers longer than 20 words to save API calls.
    """
    if len(initial_answer.split()) <= 20:
        return initial_answer

    reflection_prompt = f"""You are a critical reviewer. A user asked a question and an AI gave an answer based on document context.

Your job:
1. Check if the answer is complete, accurate, and well-supported by the context
2. If it is good — respond with exactly: APPROVED
3. If it has gaps, vagueness, or missing details — respond with an improved version only (no preamble, no explanation)

Question: {question}
Document Context: {context}
Initial Answer: {initial_answer}

Your verdict (either 'APPROVED' or the improved answer):"""

    try:
        response = llm.invoke(reflection_prompt)
        result = response.content.strip()
        if result.upper().startswith("APPROVED"):
            return initial_answer
        return result
    except Exception:
        return initial_answer


# ============================================================
# AGENT 3: CONFIDENCE-BASED RESPONSE ADAPTATION
# Appends warning or disclaimer based on confidence score
# ============================================================

def apply_confidence_adaptation(answer: str, confidence: int) -> str:
    """
    Modifies the answer text based on confidence level:
      > 60  → no change (high confidence)
      30-60 → soft disclaimer appended
      ≤ 30  → bold warning appended
    """
    if confidence > 60:
        return answer

    if confidence <= 30:
        return (
            answer +
            "\n\n⚠️ **Low Confidence Warning:** The document may not contain strong evidence "
            "for this answer. Please verify from the source document directly."
        )

    # Medium: 31-60
    return (
        answer +
        "\n\n_ℹ️ Note: This answer is based on partially relevant sections of the document. "
        "Consider rephrasing your question or checking the source pages._"
    )


# ============================================================
# SHARED: CONFIDENCE SCORING
# ============================================================

def get_confidence(docs, question: str) -> int:
    """
    Heuristic confidence score based on keyword overlap between
    the question and the retrieved document chunks.
    Returns an integer 0-98.
    """
    if not docs:
        return 0

    keywords = set(re.findall(r'\w+', question.lower()))
    scores = []
    for doc in docs:
        doc_words = set(re.findall(r'\w+', doc.page_content.lower()))
        overlap = len(keywords & doc_words) / max(len(keywords), 1)
        scores.append(overlap)

    return min(int((sum(scores) / len(scores)) * 180), 98)
