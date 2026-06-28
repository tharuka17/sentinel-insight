# Sentinel — Multimodal Content Intelligence Pipeline

> Production-grade AI content moderation system using RAG, multi-agent orchestration, LLM evaluation, and LLMOps.

![Python](https://img.shields.io/badge/python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green) ![LangGraph](https://img.shields.io/badge/LangGraph-0.2-purple) ![License](https://img.shields.io/badge/license-MIT-orange)

---

## What it does

Sentinel ingests user-generated content (text, images, audio), routes it through a multimodal AI pipeline, and returns structured moderation verdicts with cited policy rules. It includes:

- **Multi-agent orchestration** via LangGraph (modality routing + specialist sub-agents)
- **RAG-powered policy enforcement** via pgvector + LlamaIndex
- **LLM evaluation harness** with 500-example labeled dataset and CI integration
- **LLMOps observability** via LangSmith, Prometheus, and Grafana
- **Ops dashboard** via Streamlit

## Architecture

```
Ingest (FastAPI) → LangGraph Router → [Text Agent | Image Agent | Audio Agent]
                                              ↓
                               RAG Policy Retrieval (pgvector)
                                              ↓
                               LLM Verdict (Llama-3.1 via vLLM)
                                              ↓
                     Confidence Calibration → Decision Store (PostgreSQL)
                                              ↓
                               Ops Dashboard (Streamlit)
```

## Quick start

See [SETUP.md](SETUP.md) for full installation and run instructions.

```bash
git clone https://github.com/YOUR_USERNAME/sentinel.git
cd sentinel
cp .env.example .env
docker compose up --build
```

## Eval results

| Category         | Precision | Recall | F1   |
|-----------------|-----------|--------|------|
| Hate speech     | 0.93      | 0.91   | 0.92 |
| Spam            | 0.97      | 0.95   | 0.96 |
| Adult content   | 0.89      | 0.86   | 0.87 |
| Violence        | 0.88      | 0.84   | 0.86 |
| Misinformation  | 0.81      | 0.79   | 0.80 |
| Harassment      | 0.90      | 0.88   | 0.89 |

## Tech stack

- **Orchestration:** LangGraph, LangChain, LangSmith
- **RAG:** LlamaIndex, pgvector, PostgreSQL
- **Models:** Llama-3.1-8B (vLLM), BLIP-2, Whisper, CLIP
- **Backend:** FastAPI, Celery, Redis
- **Observability:** Prometheus, Grafana, LangSmith
- **Dashboard:** Streamlit

## License

MIT
