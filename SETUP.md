# Sentinel — Complete Setup, Run & GitHub Guide

## Prerequisites

Before you begin, make sure you have these installed on your machine:

| Tool | Version | Install link |
|------|---------|-------------|
| Python | 3.11+ | https://python.org/downloads |
| Docker Desktop | Latest | https://docs.docker.com/get-docker |
| Git | 2.40+ | https://git-scm.com/downloads |
| GitHub account | — | https://github.com/join |

---

## Part 1 — Download & set up the project

### Step 1: Get the project files

The project folder is provided as a download from Claude. After downloading `sentinel.zip`, open your terminal and run:

```bash
# Unzip the project
unzip sentinel.zip -d sentinel

# Navigate into the project folder
cd sentinel
```

If you're on Windows, right-click the zip file → "Extract All" → open the extracted folder, then open a terminal (PowerShell or Windows Terminal) inside it.

---

### Step 2: Create your environment file

The project uses a `.env` file to store sensitive settings like API keys and database passwords. A safe template is provided:

```bash
cp .env.example .env
```

Now open `.env` in any text editor and fill in your values:

```
# The minimum you need to get started:
POSTGRES_PASSWORD=any-password-you-choose

# If you have a LangSmith account (free tier available at smith.langchain.com):
LANGCHAIN_API_KEY=ls__your_key_here
LANGCHAIN_TRACING_V2=true

# If you want to use OpenAI instead of local vLLM:
OPENAI_API_KEY=sk-your_key_here
```

> **Note:** For your first run, the defaults in `.env.example` will work without any changes.
> You only need to set `OPENAI_API_KEY` if you skip the local vLLM model setup.

---

### Step 3: Choose your LLM backend

**Option A — Use OpenAI API (easiest, costs money per call)**

Edit `.env`:
```
VLLM_BASE_URL=https://api.openai.com/v1
VLLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-your_key_here
```

Then in `app/agents/verdict_agent.py`, change:
```python
api_key="not-needed",
```
to:
```python
api_key=settings.OPENAI_API_KEY,
```

**Option B — Run Llama-3.1 locally via vLLM (free, needs GPU)**

```bash
# Install vLLM (separate terminal, needs CUDA)
pip install vllm

# Start the vLLM server (leave this terminal open)
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --port 8000 \
  --max-model-len 4096
```

Leave this terminal running. Your `.env` defaults already point to `http://localhost:8000/v1`.

---

## Part 2 — Run the project

### Step 4: Start all services with Docker

Make sure Docker Desktop is running, then:

```bash
docker compose up --build
```

This will download and start:
- PostgreSQL with pgvector extension
- Redis (for the task queue)
- The FastAPI backend
- The Celery worker
- The Streamlit dashboard
- Prometheus metrics collector
- Grafana dashboards

**First run takes 3–5 minutes** while Docker downloads the base images.

You'll know it's ready when you see:
```
api_1        | INFO:     Application startup complete.
dashboard_1  | You can now view your Streamlit app in your browser.
```

---

### Step 5: Ingest your policy documents into the vector store

Open a new terminal (keep `docker compose up` running) and run:

```bash
# This reads data/policies/moderation_policy_v1.md,
# chunks it, embeds it, and stores it in pgvector
docker compose exec api python scripts/ingest_policies.py
```

You should see:
```
INFO | Policy ingestion complete.
```

This only needs to be run once (or whenever you update the policy documents).

---

### Step 6: Test the API

The FastAPI docs are available at: **http://localhost:8080/docs**

You can test directly from the browser, or use curl:

```bash
# Test with plain text
curl -X POST http://localhost:8080/api/v1/moderate \
  -F "text=Buy cheap followers now! 10k for $5, click here."

# Test with an image file
curl -X POST http://localhost:8080/api/v1/moderate \
  -F "file=@/path/to/your/image.jpg"

# Test with an audio file
curl -X POST http://localhost:8080/api/v1/moderate \
  -F "file=@/path/to/audio.mp3"
```

Expected response:
```json
{
  "verdict": "flagged",
  "category": "spam",
  "confidence": 0.95,
  "policy_rule_ids": ["SP-001"],
  "reasoning": "The content contains hallmarks of commercial spam solicitation.",
  "modality": "text"
}
```

---

### Step 7: Open the dashboards

| Service | URL | Credentials |
|---------|-----|-------------|
| Streamlit ops dashboard | http://localhost:8501 | None |
| API docs (Swagger UI) | http://localhost:8080/docs | None |
| Grafana | http://localhost:3000 | admin / sentinel |
| Prometheus | http://localhost:9090 | None |

---

### Step 8: Run the eval harness

```bash
docker compose exec api python -m app.eval.run_eval \
  --dataset data/eval_set.jsonl \
  --output reports/eval_report.json
```

The report will be saved to `reports/eval_report.json` and will include:
- Precision / recall / F1 per category
- Hallucination rate (LLM citing fake policy rule IDs)
- Latency p50 and p99

You can also view it via the API:
```bash
curl http://localhost:8080/api/v1/eval/report
```

---

### Step 9: Run unit tests

```bash
docker compose exec api pytest tests/unit/ -v
```

---

### Step 10: Stop the project

```bash
# Stop all containers (keeps your data)
docker compose down

# Stop and delete all data (clean slate)
docker compose down -v
```

---

## Part 3 — Upload to GitHub

### Step 11: Create a new GitHub repository

1. Go to https://github.com/new
2. Fill in:
   - **Repository name:** `sentinel`
   - **Description:** `Multimodal content moderation pipeline — RAG, LangGraph agents, LLM eval harness, LLMOps`
   - **Visibility:** Public (for portfolio purposes)
   - **DO NOT** check "Add a README file" (you already have one)
3. Click **Create repository**
4. Copy the repository URL shown on the next screen — it will look like:
   `https://github.com/YOUR_USERNAME/sentinel.git`

---

### Step 12: Initialise Git in your project folder

In your terminal, inside the `sentinel` folder:

```bash
# Initialise a git repository
git init

# Set the default branch name to main
git branch -M main

# Stage all project files
git add .

# Make your first commit
git commit -m "feat: initial Sentinel project — multimodal content moderation pipeline"
```

---

### Step 13: Connect to GitHub and push

```bash
# Replace YOUR_USERNAME with your actual GitHub username
git remote add origin https://github.com/YOUR_USERNAME/sentinel.git

# Push your code to GitHub
git push -u origin main
```

You'll be prompted for your GitHub credentials. If you're using two-factor authentication (which GitHub now requires), you'll need a **Personal Access Token** instead of your password:

1. Go to https://github.com/settings/tokens/new
2. Give it a name (e.g. "Sentinel push")
3. Set expiration to 90 days
4. Check the `repo` scope
5. Click **Generate token** and copy it
6. Use this token as your password when prompted

---

### Step 14: Verify your repository

Go to `https://github.com/YOUR_USERNAME/sentinel` in your browser.

You should see the project files and the README rendered nicely.

---

### Step 15: Set up GitHub Actions CI (automatic)

The CI workflow is already in `.github/workflows/ci.yml`. It will automatically:
- Lint your code with `ruff` on every push
- Run unit tests
- Run the eval harness against the sample dataset

To make it work with your LLM:
1. Go to your repo on GitHub → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add: `VLLM_BASE_URL` = your vLLM endpoint (or OpenAI URL)

---

## Part 4 — Ongoing development workflow

### Making changes and pushing updates

```bash
# After making code changes:
git add .
git commit -m "feat: improve confidence calibration threshold"
git push
```

### Adding your policy documents

Drop `.md`, `.txt`, or `.pdf` files into `data/policies/` and re-run:
```bash
docker compose exec api python scripts/ingest_policies.py
```

### Expanding the eval dataset

Add more labeled examples to `data/eval_set.jsonl` in the same format:
```json
{"id": "009", "text": "Your content here.", "verdict": "flagged", "category": "hate_speech"}
```

### Swapping the LLM model

Edit `.env` only — no code changes needed:
```
VLLM_MODEL=meta-llama/Llama-3.1-70B-Instruct
```
Then restart: `docker compose restart api worker`

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `docker compose up` fails on port 5432 | Stop local PostgreSQL: `brew services stop postgresql` (Mac) |
| `policy_embeddings` table not found | Run Step 5 (ingest_policies) |
| LLM returns non-JSON | Check `VLLM_BASE_URL` in `.env` matches your running server |
| Import errors on startup | Run `pip install -r requirements.txt` inside the container: `docker compose exec api pip install -r requirements.txt` |
| Can't push to GitHub | Use a Personal Access Token (see Step 13) |

---

## Project structure reference

```
sentinel/
├── app/
│   ├── agents/           # LangGraph agent nodes
│   │   ├── orchestrator.py   # Main LangGraph pipeline
│   │   ├── text_agent.py
│   │   ├── image_agent.py    # BLIP-2 captioning
│   │   ├── audio_agent.py    # Whisper transcription
│   │   ├── rag_agent.py      # pgvector policy retrieval
│   │   └── verdict_agent.py  # LLM verdict generation
│   ├── api/
│   │   ├── main.py           # FastAPI app entry point
│   │   └── routers/
│   │       ├── moderate.py   # POST /api/v1/moderate
│   │       ├── health.py
│   │       └── eval_router.py
│   ├── core/
│   │   ├── config.py         # Pydantic settings
│   │   ├── database.py       # SQLAlchemy async engine
│   │   └── celery_app.py     # Celery config
│   ├── eval/
│   │   └── run_eval.py       # Eval harness CLI
│   └── models/
│       └── decision.py       # SQLAlchemy Decision model
├── dashboard/
│   └── app.py                # Streamlit ops dashboard
├── data/
│   ├── policies/             # Policy documents for RAG
│   └── eval_set.jsonl        # Labeled evaluation dataset
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.dashboard
│   └── prometheus.yml
├── scripts/
│   ├── ingest_policies.py    # One-time RAG ingestion
│   └── init_db.sql           # pgvector schema
├── tests/
│   └── unit/
│       └── test_verdict_agent.py
├── .github/workflows/ci.yml  # GitHub Actions CI
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```
