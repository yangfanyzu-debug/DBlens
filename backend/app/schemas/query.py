from pydantic import BaseModel
from typing import Optional


class QueryExecuteRequest(BaseModel):
    conn_id: str
    database: Optional[str] = None
    sql: str
    query_id: Optional[str] = None
