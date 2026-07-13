from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_frontend_uses_reproducible_multistage_build():
    dockerfile = (ROOT / "frontend" / "Dockerfile").read_text(encoding="utf-8")
    assert dockerfile.count("FROM node:20-alpine") >= 2
    assert "npm ci" in dockerfile
    assert "npm run build" in dockerfile


def test_frontend_runtime_is_non_root_and_standalone():
    dockerfile = (ROOT / "frontend" / "Dockerfile").read_text(encoding="utf-8")
    config = (ROOT / "frontend" / "next.config.mjs").read_text(encoding="utf-8")
    assert "USER nextjs" in dockerfile
    assert 'CMD ["node", "server.js"]' in dockerfile
    assert 'output: "standalone"' in config
