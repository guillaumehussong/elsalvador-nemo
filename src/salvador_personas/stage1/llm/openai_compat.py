from __future__ import annotations

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from salvador_personas.config.env import llm_api_key, llm_base_url, llm_model
from salvador_personas.stage1.llm.base import LLMResult, LLMUsage


class OpenAICompatClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self._api_key = (api_key or llm_api_key()).strip()
        if not self._api_key:
            raise ValueError("OPENAI_API_KEY ou APIYI_API_KEY requis dans .env")
        self._base_url = (base_url or llm_base_url()).rstrip("/")
        self._model = model or llm_model()
        self._client = OpenAI(api_key=self._api_key, base_url=self._base_url)

    @property
    def model(self) -> str:
        return self._model

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=4), reraise=True)
    def complete(self, *, system: str, user: str, json_mode: bool = True) -> LLMResult:
        kwargs: dict = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.7,
            "max_tokens": 600,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = self._client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content or ""
        usage = None
        if response.usage:
            usage = LLMUsage(
                prompt_tokens=response.usage.prompt_tokens or 0,
                completion_tokens=response.usage.completion_tokens or 0,
                total_tokens=response.usage.total_tokens or 0,
            )
        return LLMResult(content=content, usage=usage)
