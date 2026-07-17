from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import settings
from app.schemas.ai import AiChatRequest


def format_sse_event(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


def build_messages(request: AiChatRequest) -> list[dict[str, str]]:
    schema_summary = _format_schema(request)
    current_context = "\n".join([
        f"当前数据库：{request.database or '未选择'}",
        "当前编辑器 SQL：",
        request.editor_sql.strip() or "(空)",
        "当前选中 SQL：",
        request.selected_sql.strip() or "(无)",
        "可用结构：",
        schema_summary,
    ])
    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": (
                "你是 DBLens 的数据库 SQL 助手。优先生成只读 SQL，并基于用户提供的数据库、"
                "当前 SQL 和表结构回答。不要声称已经执行 SQL，也不要要求或暗示你可以直接执行 SQL。"
                "如果生成 UPDATE、DELETE、DROP、TRUNCATE、ALTER 等高风险语句，必须说明风险和建议先备份或加 WHERE。"
                "生成 SQL 时使用 ```sql 代码块。"
            ),
        },
        {"role": "user", "content": current_context},
    ]

    for item in request.history[-8:]:
        content = item.content.strip()
        if content:
            messages.append({"role": item.role, "content": content})

    messages.append({"role": "user", "content": request.message.strip()})
    return messages


async def stream_chat_events(
    request: AiChatRequest,
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
    timeout: int | None = None,
) -> AsyncIterator[str]:
    token = api_key if api_key is not None else settings.AI_API_KEY
    if not token:
        yield format_sse_event("error", {"message": "AI_API_KEY 未配置"})
        return

    try:
        response = await asyncio.to_thread(
            _open_chat_stream,
            request,
            token,
            base_url or settings.AI_BASE_URL,
            model or settings.AI_MODEL,
            timeout or settings.AI_TIMEOUT_SECONDS,
        )
        with response:
            iterator = iter(response)
            while True:
                line = await asyncio.to_thread(next, iterator, None)
                if line is None:
                    break
                event = _parse_openai_stream_line(line)
                if event == "[DONE]":
                    yield format_sse_event("done", {})
                    return
                if event:
                    yield format_sse_event("delta", {"content": event})
        yield format_sse_event("done", {})
    except HTTPError as exc:
        yield format_sse_event("error", {"message": f"AI 请求失败：HTTP {exc.code}"})
    except URLError as exc:
        yield format_sse_event("error", {"message": f"AI 请求失败：{exc.reason}"})
    except Exception as exc:
        yield format_sse_event("error", {"message": f"AI 请求失败：{exc}"})


def _open_chat_stream(request: AiChatRequest, api_key: str, base_url: str, model: str, timeout: int):
    payload = {
        "model": model,
        "messages": build_messages(request),
        "stream": True,
    }
    http_request = Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
        method="POST",
    )
    return urlopen(http_request, timeout=timeout)


def _parse_openai_stream_line(raw_line: bytes | str) -> str:
    line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
    line = line.strip()
    if not line.startswith("data:"):
        return ""

    data = line[5:].strip()
    if data == "[DONE]":
        return "[DONE]"
    if not data:
        return ""

    chunk = json.loads(data)
    choices = chunk.get("choices") or []
    if not choices:
        return ""
    choice = choices[0]
    delta = choice.get("delta") or {}
    message = choice.get("message") or {}
    return delta.get("content") or message.get("content") or ""


def _format_schema(request: AiChatRequest) -> str:
    if not request.schema_context.tables:
        return "(未加载表结构)"

    lines: list[str] = []
    for table in request.schema_context.tables[:80]:
        columns = request.schema_context.columns.get(table, [])
        column_text = ", ".join(
            f"{col.get('name')} {col.get('type', '')}".strip()
            for col in columns[:24]
            if col.get("name")
        )
        lines.append(f"- {table}: {column_text or '(无列信息)'}")
    return "\n".join(lines)
