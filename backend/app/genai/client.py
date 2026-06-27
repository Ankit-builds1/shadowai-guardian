import logging

from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_nvidia_client() -> OpenAI:
    return OpenAI(base_url=settings.NVIDIA_NIM_BASE_URL, api_key=settings.NVIDIA_NIM_API_KEY)


def nim_chat(prompt: str, max_tokens: int = 700, temperature: float = 0.3) -> str | None:
    if not settings.NVIDIA_NIM_API_KEY or settings.NVIDIA_NIM_API_KEY == "your_nvidia_nim_key_here":
        return None
    try:
        response = get_nvidia_client().chat.completions.create(
            model=settings.NVIDIA_NIM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as exc:
        logger.exception("NVIDIA NIM call failed: %s", exc)
        return None
