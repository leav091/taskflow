# server/main.py
from contextlib import asynccontextmanager
from starlette.concurrency import run_in_threadpool

from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

from backend.server.models import Base
from backend.server.db import engine
from backend.server.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Bootstrap a fresh database only at startup, never at import time.
    await run_in_threadpool(Base.metadata.create_all, bind=engine)
    try:
        yield
    finally:
        engine.dispose()

# Tag descriptions (optional, but good for docs)
tags_metadata = [
    {
        "name": "items",
        "description": "Operations related to item management—create, read, update, delete."
    }
]

# Initialize FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title="Taskflow LangChain MCP API",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
)

# Include your regular CRUD router
app.include_router(router, prefix="/api", tags=["Items"])

# === FastAPI-MCP wiring ===
mcp = FastApiMCP(
    app,
    name="My API MCP",                      # human-friendly name
    description="MCP server for Item CRUD",
    describe_all_responses=True,            # Include all possible response schemas
    describe_full_response_schema=True,     # Include full JSON schema in descriptions
    include_tags=["items"]
)

# Mount into the same ASGI app
mcp.mount()

# Refresh the MCP server
mcp.setup_server()

# Run the app
if __name__ == "__main__": # pragma: no cover
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
