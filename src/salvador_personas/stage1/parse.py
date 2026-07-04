from __future__ import annotations

import json
import re


def extract_json_object(raw: str) -> dict:
    text = raw.strip()
    if not text:
        raise json.JSONDecodeError("empty response", raw, 0)

    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]

    return json.loads(text)
