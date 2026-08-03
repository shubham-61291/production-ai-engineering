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

    system_prompt = (
        "You are an elite Lead Frontend & 3D Web Graphics Engineer creating world-class web applications for AETHERIS-WEBFORGE.\n"
        "Generate a complete, self-contained single-page HTML5 web application based on the user's request.\n"
        "DESIGN & GRAPHICS REQUIREMENTS:\n"
        "- Aesthetic: Pure deep space dark background (#000000), vibrant neon gradients (from cyan-400 via fuchsia-500 to pink-500), glassmorphic cards, Google Fonts (Inter / Outfit).\n"
        "- Header & Logo: Include Magnetar/AETHERIS logo image (src='https://res.cloudinary.com/dud3yhilm/image/upload/v1761113319/Gemini_Generated_Image_f6b5ff6b5ff6b5ff_aqa9q6.png') with gradient title and tagline 'Engineering the Path to Singularity'.\n"
        "- 3D Background Canvas: Include a full-page Three.js background canvas with a central glowing star core, 5000 spherical corona particles, and chaotic flickering magnetic plasma loops.\n"
        "- Include CDN scripts in <head>:\n"
        "  <script src='https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js'></script>\n"
        "  <script src='https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js'></script>\n"
        "- Components: Responsive Header/Nav, Hero Section with gradient title ('Harnessing AI Power', 'Enterprise Grade AI Integration'), Features Grid, Pricing/Stats, Testimonials, FAQ Accordion, Contact Form, and Footer.\n"
        "- Return ONLY raw executable HTML5 code without markdown code fences."
    )

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
