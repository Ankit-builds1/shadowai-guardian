# ShadowAI Guardian

## Local-First AI Safety Proxy

ShadowAI Guardian is a focused cybersecurity + AI/ML project that prevents sensitive data from leaking into GenAI tools. It runs locally, scans prompts and GitHub repositories, applies policy-based blocking, tracks privacy risk over time, and exports audit-ready PDF reports.

The project is intentionally kept to four strong features:

1. **Prompt Firewall** - detects secrets, PII, credentials, and prompt injection before AI submission.
2. **Browser Extension / Local Proxy** - inspects prompts on AI websites through `localhost` before they are sent.
3. **Repo Secret Scanner** - scans public GitHub repositories for exposed credentials.
4. **Risk Timeline + Reports** - tracks privacy score improvement and generates PDF audit reports.

No cloud database. No telemetry. GenAI enhancement is optional. Core scanning works locally.

---

## One-Command Local Deployment

### Windows

```powershell
git clone https://github.com/Ankit-builds1/shadowai-guardian.git
cd shadowai-guardian
.\setup.ps1
.\start.ps1
```

### macOS / Linux

```bash
git clone https://github.com/Ankit-builds1/shadowai-guardian.git
cd shadowai-guardian
chmod +x setup.sh start.sh
./setup.sh
./start.sh
```

Then open:

- App: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Load the Chrome Extension

After `start.ps1` or `start.sh` is running:

1. Open Chrome.
2. Go to `chrome://extensions`.
3. Enable **Developer mode**.
4. Click **Load unpacked**.
5. Select the `browser-extension` folder from this repo.

The extension adds an **Inspect with ShadowAI** button on supported AI websites and calls:

```text
http://localhost:8000/api/proxy/inspect
```

Supported sites include ChatGPT, Claude, Gemini, and Microsoft Copilot.

---

## Optional NVIDIA NIM Setup

The app works without an API key using local rule-based fallbacks.

To enable GenAI-enhanced explanations and rewrite polishing:

1. Get an NVIDIA NIM API key from https://build.nvidia.com
2. Open `backend/.env`
3. Set:

```env
NVIDIA_NIM_API_KEY=nvapi-your-key-here
```

---

## Tech Stack

### Frontend

- Next.js 14
- TypeScript
- Tailwind CSS
- Recharts
- Lucide Icons
- Chrome Extension Manifest V3

### Backend

- FastAPI
- Python 3.11+
- SQLAlchemy async
- SQLite
- GitPython
- PyMuPDF for PDF reports

### AI / ML / Security

- Scikit-learn
- TF-IDF
- Random Forest
- Rule-based secret and PII detection
- Prompt injection detection
- Policy-based allow/warn/block decisions
- NVIDIA NIM via OpenAI-compatible client, with local fallback

---

## Core API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Backend health check |
| `POST` | `/api/proxy/inspect` | Local proxy inspection with policy decision |
| `POST` | `/api/scan/prompt` | Direct prompt scan |
| `POST` | `/api/rewrite` | Generate redacted safe prompt |
| `POST` | `/api/scan/github` | Scan public GitHub repository |
| `GET` | `/api/dashboard/stats` | Privacy score and risk timeline |
| `GET` | `/api/reports` | Scan report history |
| `GET` | `/api/reports/{id}/pdf` | Download detailed PDF report |

---

## Architecture

```text
shadowai-guardian/
|-- backend/
|   |-- app/
|   |   |-- api/              # FastAPI routers
|   |   |-- core/             # Config, SQLite models, async DB
|   |   |-- detectors/        # Secret, PII, prompt injection detection
|   |   |-- genai/            # NVIDIA NIM wrappers + fallbacks
|   |   |-- ml/               # TF-IDF + Random Forest model
|   |   |-- services/         # GitHub scanning, policy engine, PDF reports
|   |   `-- schemas/          # Pydantic request models
|   `-- requirements.txt
|-- browser-extension/        # Chrome Manifest V3 local safety proxy
|-- frontend/
|   |-- app/                  # Next.js pages
|   |-- components/           # Shared UI components
|   `-- package.json
|-- setup.ps1 / setup.sh      # Local setup scripts
|-- start.ps1 / start.sh      # Local app runners
`-- .env.example
```

---

## Interview Pitch

> I built ShadowAI Guardian, a local-first AI safety proxy that scans prompts and repositories for secrets, PII, prompt injection, and risky AI usage before data reaches GenAI tools. It includes a Chrome extension, FastAPI policy engine, ML risk scoring, privacy timeline, and PDF audit reports.

## Resume Bullets

- Built a local-first AI safety proxy using Next.js, FastAPI, SQLite, Chrome Manifest V3, and ML-based risk scoring to prevent sensitive data leakage into GenAI tools.
- Implemented policy-based allow/warn/block decisions for prompts containing API keys, PII, credentials, or prompt injection attacks.
- Developed a GitHub repository secret scanner and audit reporting workflow with privacy score tracking, risk timeline analytics, and downloadable PDF reports.
- Packaged the system for one-command local deployment across Windows, macOS, and Linux.

---

## License

MIT License. Use responsibly and never scan repositories or prompts without permission.
