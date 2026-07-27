import re
import html
from typing import List, Tuple

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?prior\s+prompts",
    r"system\s*:\s*",
    r"you\s+are\s+now\s+a",
    r"override\s+(the\s+)?system",
    r"reveal\s+(the\s+)?(api\s+key|system\s+prompt|secret)",
    r"print\s+(the\s+)?environment",
    r"do\s+anything\s+now",
    r"dan\s+mode",
    r"jailbreak",
]

def sanitize_input_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    return text.strip()

def validate_prompt_security(prompt: str) -> Tuple[bool, str]:
    cleaned_prompt = sanitize_input_text(prompt)
    if not cleaned_prompt:
        return False, "Empty prompt provided."

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, cleaned_prompt, re.IGNORECASE):
            return False, f"Security Violation: Potential prompt injection detected matching pattern '{pattern}'."

    return True, "Prompt validation passed."

def sanitize_output_html(content: str) -> str:
    if not content:
        return ""
    return html.escape(content)

def verify_output_grounding(answer: str, context_chunks: List[str], min_overlap_ratio: float = 0.05) -> Tuple[bool, str]:
    if not answer or not answer.strip():
        return False, "Empty response generated."

    refusal_keywords = ["not found", "don't know", "not in the provided", "no information", "cannot find"]
    if any(k in answer.lower() for k in refusal_keywords):
        return True, answer

    if not context_chunks:
        return False, "Information not found in provided authoritative documents."

    combined_context = " ".join(context_chunks).lower()
    context_words = set(re.findall(r"\w+", combined_context))
    answer_words = set(re.findall(r"\w+", answer.lower()))
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "this", "that", "it"}
    content_words = answer_words - stop_words

    if not content_words:
        return True, answer

    overlap = content_words.intersection(context_words)
    overlap_ratio = len(overlap) / len(content_words)

    if overlap_ratio < min_overlap_ratio:
        return False, "❌ SECURITY GUARDRAIL: Answer failed strict document context grounding check. Response blocked to prevent hallucination."

    return True, answer

def filter_system_leaks(output_text: str) -> str:
    patterns_to_redact = [
        r"sk-[a-zA-Z0-9]{32,}",
        r"AI_SECRET_[A-Z0-9_]+",
        r"System\s+Prompt\s*:\s*.*",
    ]
    redacted = output_text
    for p in patterns_to_redact:
        redacted = re.sub(p, "[REDACTED_SECURITY_DATA]", redacted, flags=re.IGNORECASE)
    return redacted
