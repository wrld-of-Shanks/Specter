# SPECTER Legal Assistant v2.0

AI-powered Indian Legal Assistant with RAG pipeline, document intelligence, lawyer marketplace, and automated benchmarking.

## Features

- **RAG Chat Engine** — Semantic search (ChromaDB + sentence-transformers) over 13K+ legal chunks with Gemini answer generation
- **Multi-Turn Memory** — Per-user MongoDB chat sessions with 24h TTL
- **Document Intelligence** — OCR (English + 7 Indic languages), clause extraction, risk scoring, timeline extraction, per-document Q&A
- **Lawyer Marketplace** — Lawyer profiles, search by city/specialization/fee, consultation booking
- **Legal Templates** — 15+ AI-generated Indian legal document templates (rent agreement, NDA, legal notice, sale deed, will, etc.)
- **WhatsApp Integration** — Twilio webhook for WhatsApp-based legal Q&A
- **Admin Analytics** — DAU tracking, popular queries, revenue/subscription stats
- **Evaluation Framework** — Automated benchmarking with BM25 baseline, Precision@K, Recall@K, MRR, NDCG, LLM-as-a-Judge

## Architecture

```
frontend/ ←→ FastAPI Backend ←→ ChromaDB (vector store)
                    ↕                    MongoDB (users, sessions, lawyers)
                    ↕                    Gemini Flash (answer generation)
                    ↕                    Redis (optional answer cache)
```

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py          # runs on :8000 (or :8002 via config)

# Frontend
cd frontend/react_app
npm install
npm start               # runs on :3000
```

## Evaluation

```bash
# 1. Generate evaluation set
python scripts/curate_eval_set.py

# 2. Run benchmarks
python run_experiments.py --configs A,B,C,D
```

Output: `evaluation/benchmark_report.txt` and `evaluation/results_matrix.csv`

## Endpoints

| Category | Endpoints |
|----------|-----------|
| Auth | `/auth/register`, `/auth/login`, `/auth/verify-email` |
| Chat | `POST /chat`, `DELETE /chat/history` |
| Documents | `POST /legal/upload_doc`, `POST /legal/doc_qa`, `POST /legal/risk_score`, `POST /legal/timeline` |
| Marketplace | `GET /api/lawyers/search`, `POST /api/consultations/book` |
| Templates | `GET /templates/categories`, `POST /templates/generate` |
| WhatsApp | `POST /api/whatsapp/webhook` |
| Admin | `GET /admin/stats`, `GET /admin/dau`, `GET /admin/revenue` |

## Tech Stack

- **Backend**: Python 3.10, FastAPI, Motor (async MongoDB), ChromaDB, sentence-transformers
- **Frontend**: React 18, TypeScript
- **LLM**: Google Gemini Flash (with Ollama fallback)
- **Infrastructure**: Render Free Tier, MongoDB Atlas, optional Redis
