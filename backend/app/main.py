from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import ai, auth, connections, databases, query, data, ws

app = FastAPI(title="DBLens API", version="1.0.0", redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(connections.router)
app.include_router(ai.router)
app.include_router(auth.router)
app.include_router(databases.router)
app.include_router(query.router)
app.include_router(data.router)
app.include_router(ws.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
