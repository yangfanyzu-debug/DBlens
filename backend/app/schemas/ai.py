from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class AiMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AiSchemaContext(BaseModel):
    tables: list[str] = Field(default_factory=list)
    columns: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)


class AiChatRequest(BaseModel):
    conn_id: str
    database: Optional[str] = None
    message: str
    editor_sql: str = ""
    selected_sql: str = ""
    history: list[AiMessage] = Field(default_factory=list)
    schema_context: AiSchemaContext = Field(default_factory=AiSchemaContext, alias="schema")

    model_config = ConfigDict(populate_by_name=True)
