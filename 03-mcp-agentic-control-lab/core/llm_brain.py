import re
from typing import List, Dict, Any, Optional
from openai import OpenAI
import config

class LLMBrain:
    """Unified client interface for Local AI Brain (Ollama / DeepSeek-R1 on GPU) 
    and OpenAI API fallback."""
    
    def __init__(self):
        self.base_url = config.AI_BRAIN_BASE_URL
        self.model = config.AI_BRAIN_MODEL
        self.api_key = config.AI_BRAIN_API_KEY
        self.client = self._init_client()

    def _init_client(self) -> OpenAI:
        try:
            print(f"[INFO] Connecting to AI Brain Endpoint: {self.base_url} [Model: {self.model}]")
            return OpenAI(base_url=self.base_url, api_key=self.api_key or "ollama")
        except Exception as e:
            print(f"[WARNING] Primary AI Brain connection setup error: {e}")
            if config.OPENAI_API_KEY:
                print("[INFO] Falling back to official OpenAI API endpoint...")
                return OpenAI(api_key=config.OPENAI_API_KEY)
            raise e

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 500
    ) -> str:
        """Call LLM completion and extract response text, removing DeepSeek-R1 <think> tags."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            raw_content = response.choices[0].message.content or ""
            cleaned_content = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL).strip()
            return cleaned_content if cleaned_content else raw_content.strip()
        except Exception as e:
            if config.OPENAI_API_KEY and self.base_url != "https://api.openai.com/v1":
                try:
                    print(f"[WARNING] Primary model '{self.model}' call failed ({e}). Retrying with OpenAI gpt-4o-mini...")
                    fallback_client = OpenAI(api_key=config.OPENAI_API_KEY)
                    res = fallback_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    return res.choices[0].message.content or ""
                except Exception as fallback_err:
                    return f"[ERROR] System Error (LLM Call Failed): {fallback_err}"
            return f"[ERROR] System Error (LLM Call Failed): {e}"

_llm_brain_instance = None

def get_llm_brain() -> LLMBrain:
    global _llm_brain_instance
    if _llm_brain_instance is None:
        _llm_brain_instance = LLMBrain()
    return _llm_brain_instance
