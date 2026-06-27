from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import dashboard, github_scan, proxy, reports, rewrite, scan
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
    allow_origin_regex=r"chrome-extension://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan.router, prefix="/api")
app.include_router(rewrite.router, prefix="/api")
app.include_router(github_scan.router, prefix="/api")
app.include_router(proxy.router, prefix="/api")
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
