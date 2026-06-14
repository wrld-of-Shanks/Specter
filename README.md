# SPECTER Legal Assistant v2.0

AI-powered Indian Legal Assistant with RAG pipeline, chat engine, document intelligence, lawyer marketplace, legal templates, and automated evaluation.

## How It Works

SPECTER uses a **Retrieval-Augmented Generation (RAG)** pipeline:

1. **Query** → User asks a legal question via chat
2. **Retrieval** → The question is converted to a vector embedding (sentence-transformers `all-MiniLM-L6-v2`) and searched against a ChromaDB vector store containing 14,001 legal chunks. Top-4 most relevant chunks are retrieved.
3. **Answer** → Retrieved chunks are formatted into a structured response with:
   - **What the Law Says** — Legal context from the database with citations
   - **Steps You Can Take** — Practical, actionable steps
   - **Documents You Will Need** — Required paperwork
   - **Where to Go** — Relevant courts, police stations, or authorities
4. **Classification** → Queries are auto-classified into 10+ situation types (fake case, divorce, domestic violence, bail, property dispute, consumer, cyber crime, FIR filing, landlord-tenant, etc.) and answered with situation-specific advice templates.

If a Gemini API key is configured, the retrieved chunks are sent to Gemini Flash for human-like natural language generation. Without an API key, the system falls back to **retrieval-only mode**, building structured answers directly from the legal database.

### Architecture

```
User → React Frontend → FastAPI Backend → ChromaDB (vector store)
                              ↕                  MongoDB (users, sessions, lawyers, consultations)
                              ↕                  Gemini Flash (optional LLM generation)
                              ↕                  Redis (optional answer cache)
```

## Training Data

The legal knowledge base consists of **23,157 data points** across 5 files, totaling **13.1 MB**:

| Dataset | Records | Size | Content |
|---------|---------|------|---------|
| `optimized_legal_train.jsonl` | 12,996 | 7.3 MB | Indian Supreme Court & High Court case summaries with legal questions and answers (IPC, CrPC, Constitution, civil, criminal, family law) |
| `indic_legal_qa_train.jsonl` | 10,000 | 5.7 MB | Legal Q&A pairs covering Indian statutes, procedural law, and landmark judgments |
| `legal_training_data.jsonl` | 149 | 54 KB | Curated legal scenarios with expert annotations |
| `kb_seed.jsonl` | 6 | 7 KB | Knowledge base seed entries for core legal concepts |
| `seed_notes.jsonl` | 6 | 9 KB | Additional legal reference notes |

**Data sources**: Publicly available Indian legal documents from legislative.gov.in, indiacode.nic.in, Supreme Court judgments, and High Court rulings. All data is public domain government content.

**Data types covered**: 15+ legal domains including Constitutional Law, Criminal Law (IPC, CrPC), Civil Law, Family Law (Hindu Marriage Act, Special Marriage Act), Property Law, Consumer Protection, Cyber Law (IT Act 2000), Labour Law, Tax Law, Environmental Law, Corporate Law, and Procedural Law.

**Vector store**: 14,001 indexed chunks in ChromaDB using `all-MiniLM-L6-v2` embeddings (384-dimensional vectors).

## Accuracy & Evaluation

Evaluated on **146 curated test samples** using 4 retrieval metrics:

| Metric | Score | Description |
|--------|------:|-------------|
| **Precision@1** | 0.8356 | 83.6% of top-1 retrievals are relevant |
| **Precision@3** | 0.5845 | 58.5% of top-3 retrievals are relevant |
| **Recall@1** | 0.4071 | Top-1 captures 40.7% of all relevant content |
| **Recall@5** | 0.8493 | Top-5 captures 84.9% of all relevant content |
| **MRR** | 0.8413 | Mean Reciprocal Rank — first relevant result appears at rank ~1.2 on average |
| **NDCG@5** | 0.8251 | Normalized Discounted Cumulative Gain — ranking quality score |

**BM25 baseline comparison**: The BM25 keyword-search baseline (Config A) achieves P@1 = 0.8356 vs vector search (Config B) P@1 = 0.5959, confirming that keyword matching is highly effective for Indian legal case-law retrieval. The vector search excels at semantic understanding of paraphrased queries.

**Latency**: Average response time < 1s in LLM mode, ~7s in retrieval-only mode (due to Ollama connection timeout).

Run evaluation yourself:
```bash
python run_experiments.py --configs A,B,C,D
```

## Features

- **RAG Chat Engine** — Semantic search over 14K legal chunks with situation-classified structured responses
- **Situation Classifier** — Auto-detects 10+ legal scenarios (fake case, divorce, DV, bail, property, consumer, cyber crime, FIR, landlord-tenant) with tailored step-by-step advice
- **Multi-Turn Memory** — Per-user MongoDB chat sessions with 24h TTL
- **Document Intelligence** — OCR (English + 7 Indic languages), clause extraction, risk scoring, timeline extraction, per-document Q&A
- **Lawyer Marketplace** — Lawyer profiles, search by city/specialization/fee, consultation booking
- **Legal Templates** — 15+ AI-generated Indian legal document templates (rent agreement, NDA, legal notice, sale deed, will, etc.)
- **WhatsApp Integration** — Twilio webhook for WhatsApp-based legal Q&A
- **Admin Analytics** — DAU tracking, popular queries, revenue/subscription stats
- **No API Key Required** — Full functionality using retrieval-only mode with structured answers from the legal database

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

- **Backend**: Python 3.10, FastAPI, Motor (async MongoDB), ChromaDB, sentence-transformers (all-MiniLM-L6-v2)
- **Frontend**: React 18, TypeScript, Material-UI
- **LLM**: Google Gemini Flash (optional, with Ollama fallback)
- **Infrastructure**: Render Free Tier, MongoDB Atlas, optional Redis

## License

Copyright © 2025 Shankar M Darur. All Rights Reserved.
