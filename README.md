# ShadowAI Guardian

## Agentic Privacy Firewall for GenAI Tool Usage

ShadowAI Guardian is a local-first cybersecurity and AI privacy application that scans prompts, documents, clipboard text, and GitHub repositories before sensitive data reaches external GenAI tools.

It detects API keys, passwords, database URLs, private keys, JWTs, personal identifiers, prompt injection attacks, unsafe commands, and risky AI tool domains. It also generates safe rewritten prompts, audit logs, privacy scoring, and detailed PDF reports.

> Built as a full-stack AI/ML + cybersecurity project for practical local deployment. No cloud database. No telemetry. Your data stays on your machine.

---

## Demo Highlights

- Prompt risk scanner with rule-based detection + ML risk scoring
- Prompt injection and indirect document injection detection
- Safe prompt rewriting with redaction placeholders
- PDF, DOCX, and TXT privacy scanning
- GitHub repository secret scanner
- AI tool trust checker
- Agentic privacy workflow with seven steps: Observe, Analyze, Decide, Explain, Rewrite, Ask, Log
- Privacy Amnesia Score for monthly privacy behavior tracking
- Detailed downloadable PDF reports
- SQLite local audit history

---

## One-Command Local Deployment

### Windows

```powershell
git clone https://github.com/YOUR_USERNAME/shadowai-guardian.git
cd shadowai-guardian
.\setup.ps1
.\start.ps1
```

### macOS / Linux

```bash
git clone https://github.com/YOUR_USERNAME/shadowai-guardian.git
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

## Requirements

- Python 3.11 or newer
- Node.js 18 or newer
- Git

No Docker is required.

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

The default model is:

```env
NVIDIA_NIM_MODEL=meta/llama-3.1-8b-instruct
```

---

## Tech Stack

### Frontend

- Next.js 14
- TypeScript
- Tailwind CSS
- Recharts
- Lucide Icons

### Backend

- FastAPI
- Python 3.11+
- SQLAlchemy async
- SQLite
- PyMuPDF
- python-docx
- GitPython

### AI / ML

- Scikit-learn
- TF-IDF
- Random Forest
- Rule-based cybersecurity detectors
- NVIDIA NIM via OpenAI-compatible client, with local fallback

---

## Architecture

```text
shadowai-guardian/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routers
│   │   ├── agents/           # Agentic privacy workflow
│   │   ├── core/             # Config, SQLite models, async DB
│   │   ├── detectors/        # Regex + prompt injection detectors
│   │   ├── genai/            # NVIDIA NIM wrappers + fallbacks
│   │   ├── ml/               # TF-IDF + Random Forest model
│   │   ├── services/         # PDF, GitHub, report generation
│   │   └── schemas/          # Pydantic request models
│   └── requirements.txt
├── frontend/
│   ├── app/                  # Next.js pages
│   ├── components/           # Shared UI components
│   └── package.json
├── data/                     # Synthetic local sample data
├── setup.ps1 / setup.sh      # Local setup scripts
├── start.ps1 / start.sh      # Local app runners
└── .env.example
```

---

## Core API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Backend health check |
| `POST` | `/api/scan/prompt` | Scan prompt or text |
| `POST` | `/api/rewrite` | Generate redacted safe prompt |
| `POST` | `/api/scan/document` | Scan PDF, DOCX, or TXT |
| `POST` | `/api/scan/github` | Scan public GitHub repository |
| `POST` | `/api/tool-risk` | Check AI tool trust |
| `POST` | `/api/agent/analyze` | Run 7-step privacy agent |
| `GET` | `/api/dashboard/stats` | Dashboard metrics |
| `GET` | `/api/reports` | Scan report history |
| `GET` | `/api/reports/{id}/pdf` | Download detailed PDF report |

---

## Privacy Guarantee

ShadowAI Guardian is designed to run locally:

- SQLite database is stored on your machine
- No cloud database
- No telemetry
- No tracking
- No uploaded scan history
- GenAI calls are optional and have rule-based fallbacks

---

## Resume Bullets

- Built a local-first AI privacy firewall that detects secrets, personal information, and prompt injection attacks before data reaches GenAI tools.
- Implemented a FastAPI + SQLite backend with async SQLAlchemy models, ML-based risk scoring, GitHub repository scanning, document scanning, and PDF report generation.
- Developed a Next.js + TypeScript dashboard with privacy scoring, charts, report history, safe prompt rewriting, and an agentic seven-step privacy workflow.
- Packaged the project for one-command local deployment across Windows, macOS, and Linux.

---

## License

MIT License. Use responsibly and never scan repositories or documents without permission.
