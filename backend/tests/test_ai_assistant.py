import json
import unittest
from unittest.mock import patch


class AiAssistantConfigTestCase(unittest.TestCase):
    def test_ai_settings_default_to_disabled_without_api_key(self):
        from app.config import Settings

        settings = Settings(_env_file=None)

        self.assertEqual(settings.AI_PROVIDER, "ark")
        self.assertEqual(settings.AI_BASE_URL, "https://ark.cn-beijing.volces.com/api/coding/v3")
        self.assertEqual(settings.AI_MODEL, "glm-5.2")
        self.assertEqual(settings.AI_TIMEOUT_SECONDS, 60)
        self.assertEqual(settings.AI_API_KEY, "")


class AiAssistantServiceTestCase(unittest.TestCase):
    def test_format_sse_event_serializes_event_and_json_payload(self):
        from app.services.ai_assistant import format_sse_event

        event = format_sse_event("delta", {"content": "SELECT 1"})

        self.assertEqual(event, 'event: delta\ndata: {"content": "SELECT 1"}\n\n')

    def test_build_messages_includes_sql_safety_and_schema_context(self):
        from app.schemas.ai import AiChatRequest, AiSchemaContext
        from app.services.ai_assistant import build_messages

        request = AiChatRequest(
            conn_id="conn-1",
            database="ry-cloud",
            message="统计分类数量",
            editor_sql="select * from categories",
            selected_sql="",
            history=[],
            schema=AiSchemaContext(
                tables=["categories"],
                columns={"categories": [{"name": "id", "type": "int", "primary_key": True}]},
            ),
        )

        messages = build_messages(request)
        joined = "\n".join(message["content"] for message in messages)

        self.assertIn("优先生成只读 SQL", joined)
        self.assertIn("categories", joined)
        self.assertIn("select * from categories", joined)

    async def collect(self, stream):
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)
        return chunks

    def test_missing_api_key_streams_error_event(self):
        from app.schemas.ai import AiChatRequest
        from app.services.ai_assistant import stream_chat_events

        request = AiChatRequest(conn_id="conn-1", database="main", message="select 1")

        chunks = asyncio_run(self.collect(stream_chat_events(request, api_key="")))

        self.assertIn("event: error", chunks[0])
        self.assertIn("AI_API_KEY 未配置", chunks[0])

    def test_stream_chat_events_emits_delta_and_done_from_openai_compatible_chunks(self):
        from app.schemas.ai import AiChatRequest
        from app.services.ai_assistant import stream_chat_events

        response_lines = [
            b'data: {"choices":[{"delta":{"content":"SELECT"}}]}\n',
            b'data: {"choices":[{"delta":{"content":" 1"}}]}\n',
            b"data: [DONE]\n",
        ]

        class ResponseStub:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            def __iter__(self):
                return iter(response_lines)

        with patch("app.services.ai_assistant.urlopen", return_value=ResponseStub()):
            chunks = asyncio_run(self.collect(stream_chat_events(
                AiChatRequest(conn_id="conn-1", database="main", message="select 1"),
                api_key="secret",
            )))

        self.assertEqual(json.loads(chunks[0].split("data: ", 1)[1])["content"], "SELECT")
        self.assertEqual(json.loads(chunks[1].split("data: ", 1)[1])["content"], " 1")
        self.assertEqual(chunks[-1], "event: done\ndata: {}\n\n")


def asyncio_run(coro):
    import asyncio

    return asyncio.run(coro)


if __name__ == "__main__":
    unittest.main()
