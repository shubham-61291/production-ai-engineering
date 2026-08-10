import re
from openai import OpenAI
from config import DEFAULT_OLLAMA_URL, DEFAULT_OLLAMA_MODEL, DEFAULT_OPENAI_MODEL
from core.security import validate_prompt_security, filter_system_leaks

def strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    return text.strip()

def generate_website_html(
    prompt: str,
    provider: str = "ollama",
    ollama_url: str = DEFAULT_OLLAMA_URL,
    ollama_model: str = DEFAULT_OLLAMA_MODEL,
    openai_key: str = "",
    openai_model: str = DEFAULT_OPENAI_MODEL
) -> str:
    is_safe, reason = validate_prompt_security(prompt)
    if not is_safe:
        raise ValueError(f"Security Rejection: {reason}")

    system_prompt = """
You are a world-class senior frontend engineer, UI/UX designer, and web architect.

Your task is to generate a COMPLETE production-quality single-file HTML5 application that fulfills the user's request.

Requirements:
- Return ONLY valid HTML (no markdown, no explanations, no code fences).
- The output must start with <!DOCTYPE html>.
- Modern, premium design with beautiful typography, responsive layout, and smooth animations.
- Use semantic HTML5, modern CSS, vanilla JS (unless a specific library is requested).
- You may use trusted CDNs (Tailwind, Bootstrap, Font Awesome, Google Fonts, etc.) if helpful.
- Do NOT include any hardcoded branding, logos, or company names unless requested.
- Include all requested functionality (dashboard, landing page, portfolio, admin panel, e-commerce, etc.).
- For forms: validate input, show friendly messages, prevent invalid submission.
- For images: use royalty-free placeholder URLs (e.g., Unsplash Source, Picsum).
- Ensure accessibility (heading hierarchy, ARIA labels, focus states).
- Optimize for performance (minimal DOM, lazy loading where appropriate).
- Never leave placeholders, TODOs, or incomplete sections.
- Output ONLY the finished HTML document. No extra text.
"""

    if provider.lower() == "ollama":
        client = OpenAI(
            base_url=ollama_url,
            api_key="ollama"
        )
        model = ollama_model
    else:
        if not openai_key:
            raise ValueError("OpenAI API Key is required when provider is set to 'openai'")
        client = OpenAI(api_key=openai_key)
        model = openai_model

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    raw_html = resp.choices[0].message.content or ""
    clean_html = strip_fences(raw_html)
    return filter_system_leaks(clean_html)
