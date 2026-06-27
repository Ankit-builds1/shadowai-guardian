from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import agent, dashboard, github_scan, reports, rewrite, scan, tool_risk
from app.core.database import init_db
from app.ml.predict import load_model

app = FastAPI(title="ShadowAI Guardian", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3010",
        "http://127.0.0.1:3010",
        "http://localhost:3020",
        "http://127.0.0.1:3020",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan.router, prefix="/api")
app.include_router(rewrite.router, prefix="/api")
app.include_router(github_scan.router, prefix="/api")
app.include_router(tool_risk.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(reports.router, prefix="/api")


@app.on_event("startup")
async def startup() -> None:
    await init_db()
    load_model()


@app.get("/health")
async def health():
    load_model()
    return {"status": "ok", "model_loaded": True}
