"""
OpenRouter via OpenAI-compatible SDK.

Uses the OpenAI client pointing to OpenRouter's base URL with required headers.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - handled at runtime
    OpenAI = None


DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_HEADERS = {
    "HTTP-Referer": "https://github.com/whisper-cheap/whisper-cheap",
    "X-Title": "Whisper Cheap",
}


class LLMClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        default_model: Optional[str] = None,
        client: Optional[Any] = None,
        default_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self.base_url = base_url
        self.default_model = default_model
        self.default_headers = default_headers or DEFAULT_HEADERS

        if client is not None:
            self._client = client
        elif OpenAI:
            self._client = OpenAI(
                base_url=base_url,
                api_key=api_key,
                default_headers=self.default_headers,
            )
        else:
            self._client = None

        if self._client is None:
            raise RuntimeError("No LLM client available (install openai)")

    def _build_provider_body(self, providers: Optional[List[str]]) -> Dict[str, Any]:
        if providers:
            return {"only": providers, "allow_fallbacks": True}
        return {"sort": "throughput", "allow_fallbacks": True}

    def postprocess(
        self,
        text: str,
        prompt_template: str,
        model: Optional[str] = None,
        timeout: Optional[float] = 30.0,
        system_prompt: Optional[str] = None,  # Deprecated, ignored
        providers: Optional[list[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Call OpenRouter (OpenAI-compatible) with prompt_template as system prompt.
        The user message is just the transcription wrapped in XML tags.
        """
        if not prompt_template:
            raise ValueError("prompt_template is required")
        active_model = model or self.default_model
        if not active_model:
            raise ValueError("model is required")

        # prompt_template = system instructions, user message = transcription in XML
        messages = [
            {"role": "system", "content": prompt_template},
            {"role": "user", "content": f"<transcription>\n{text}\n</transcription>"},
        ]

        provider_body = self._build_provider_body(providers)
        last_error: Optional[Exception] = None
        response = None
        for attempt in range(2):
            try:
                response = self._client.chat.completions.create(
                    model=active_model,
                    messages=messages,
                    timeout=timeout,
                    extra_body={"provider": provider_body},
                )
                if response:
                    break
            except Exception as exc:  # pragma: no cover - network/runtime errors
                last_error = exc
                continue

        if response is None:
            print(f"[openrouter] postprocess failed: {last_error}")
            return None

        choices = getattr(response, "choices", None)
        if not choices:
            print("[openrouter] respuesta sin texto; se usara la transcripcion original")
            return None
        choice = choices[0]
        message = getattr(choice, "message", None)
        content = getattr(message, "content", None) if message is not None else None
        if not content:
            print("[openrouter] respuesta sin texto; se usara la transcripcion original")
            return None

        usage = getattr(response, "usage", None)
        usage_dict = None
        if usage:
            usage_dict = {
                "prompt_tokens": getattr(usage, "prompt_tokens", None),
                "completion_tokens": getattr(usage, "completion_tokens", None),
                "total_tokens": getattr(usage, "total_tokens", None),
            }

        return {
            "text": content,
            "model": getattr(response, "model", active_model),
            "id": getattr(response, "id", None),
            "finish_reason": getattr(choice, "finish_reason", None),
            "usage": usage_dict,
        }

    def list_models(self, timeout: float | None = 10.0) -> list[dict[str, Any]]:
        """
        Fetch available models from OpenRouter.
        Returns a list of dicts with at least {"id": "..."}; empty list on failure.
        """
        if not self._client:
            print("[openrouter] client not initialized")
            return []
        try:
            res = self._client.models.list(timeout=timeout)
            items = getattr(res, "data", []) or []
            normalized = []
            for m in items:
                mid = getattr(m, "id", None) or m.get("id") if isinstance(m, dict) else None
                if not mid:
                    continue
                display = getattr(m, "name", None) if not isinstance(m, dict) else m.get("name")
                normalized.append({"id": mid, "name": display or mid})
            return normalized
        except Exception as exc:  # pragma: no cover - network/runtime errors
            print(f"[openrouter] list_models failed: {exc}")
            return []
