# SPECTER Legal Assistant v2.1 — Hybrid Retrieval

AI-powered Indian Legal Assistant with **hybrid retrieval** (BM25 + Dense + RRF), cross-encoder reranking, chat engine, document intelligence, lawyer marketplace, legal templates, and automated evaluation.

## How It Works

SPECTER uses a **Hybrid Retrieval-Augmented Generation (RAG)** pipeline:

1. **Query** → User asks a legal question via chat
2. **Hybrid Retrieval** → The question is searched against **59,630 legal chunks** using two parallel paths:
   - **BM25 lexical search** — exact keyword matching (critical for section numbers, case citations, statutory references)
   - **Dense vector search** — semantic similarity via `all-MiniLM-L6-v2` embeddings in ChromaDB
3. **RRF Fusion** → Results from both paths are merged using Reciprocal Rank Fusion (k=60), with **citation-aware boosting** (BM25 weighted 1.5× when section/case citations detected)
4. **Cross-Encoder Reranker** → Top-15 fused results are reranked by `cross-encoder/ms-marco-MiniLM-L-6-v2` for precision
5. **Answer** → Top-4 chunks are formatted into a structured response with:
   - **What the Law Says** — Legal context from the database with citations
   - **Steps You Can Take** — Practical, actionable steps
   - **Documents You Will Need** — Required paperwork
   - **Where to Go** — Relevant courts, police stations, or authorities
6. **Classification** → Queries are auto-classified into 10+ situation types (fake case, divorce, domestic violence, bail, property dispute, consumer, cyber crime, FIR filing, landlord-tenant, etc.) and answered with situation-specific advice templates.

**v2.1 uses retrieval-only mode** — answers are built directly from the legal database without any external LLM API. The system works completely offline, using its own curated corpus of Indian legal texts.

### Architecture

```
User → React Frontend → FastAPI Backend
                              ↕
                    ┌─────────────────────┐
                    │  Hybrid Retrieval    │
                    │  ┌──────┐ ┌───────┐  │
                    │  │ BM25 │ │Dense  │  │
                    │  │Lexical│ │Vector │  │
                    │  └──┬───┘ └───┬───┘  │
                    │     └──┬──┬──┘      │
                    │   Citation Boost?   │
                    │        ↓            │
                    │   RRF Fusion (k=60) │
                    │        ↓           │
                    │  Cross-Encoder      │
                    │  Reranker (top-5)   │
                    └─────────────────────┘
                              ↕
                    ChromaDB (vector store)
                    MongoDB (users, sessions)
                    Redis (optional cache)
```

## Training Data

The legal knowledge base consists of **59,829 training records** across 8 files, totaling **~30 MB**:

| Dataset | Records | Content |
|---------|---------|---------|
| `optimized_legal_train.jsonl` | 12,996 | Indian Supreme Court & High Court case summaries with legal Q&A (IPC, CrPC, Constitution, civil, criminal, family law) |
| `indic_legal_qa_train.jsonl` | 10,000 | Legal Q&A pairs covering Indian statutes, procedural law, and landmark judgments |
| `indian_laws_training.jsonl` | 34,243 | Full text of Indian Acts (IPC, CrPC, Constitution, property, labour, tax, and more) with section-level Q&A |
| `meera_legal_qa.jsonl` | 2,364 | Synthetic Indian legal Q&A pairs covering IPC, Constitution, and procedural law |
| `legal_training_data.jsonl` | 149 | Curated legal scenarios with expert annotations |
| `faq_training_data.jsonl` | 65 | Comprehensive legal FAQ (criminal, civil, constitutional, procedural law) |
| `kb_seed.jsonl` | 6 | Knowledge base seed entries for core legal concepts |
| `seed_notes.jsonl` | 6 | Additional legal reference notes |

**Data sources**: Publicly available Indian legal documents from legislative.gov.in, indiacode.nic.in, Supreme Court judgments, High Court rulings, Hugging Face Indian legal datasets (CC-BY-SA 4.0 licensed), and Indian Kanoon. All primary legal texts are public domain government content.

**Data types covered**: 15+ legal domains including Constitutional Law, Criminal Law (IPC, CrPC, Evidence Act), Civil Law, Family Law (Hindu Marriage Act, Special Marriage Act), Property Law, Consumer Protection, Cyber Law (IT Act 2000), Labour Law, Tax Law, Environmental Law, Corporate Law, and Procedural Law.

**Vector store**: **59,630 indexed chunks** in ChromaDB using `all-MiniLM-L6-v2` embeddings (384-dimensional vectors), with 10 situation-based advice templates for common legal scenarios.

## Accuracy & Evaluation

Evaluated on **146 curated test samples** drawn from 7 source datasets. The evaluation set breakdown by legal domain is documented in `evaluation/benchmark_report.txt`.

### Retrieval Strategy Comparison (50 samples)

Results comparing all retrieval strategies on recall, MRR, hit rate, and NDCG:

| Metric | Dense-Only | BM25-Only | Hybrid (RRF) | **+Reranker** | Δ vs Dense |
|--------|:----------:|:---------:|:------------:|:-------------:|:----------:|
| **Hit Rate** | 0.3200 | 0.3800 | 0.3800 | **0.4400** | **+37.5%** |
| **Recall@5** | 0.4169 | 0.4522 | 0.4225 | **0.4759** | **+14.2%** |
| **Recall@10** | 0.7400 | **0.8400** | 0.8000 | 0.8000 | +8.1% |
| **Precision@5** | 0.5520 | 0.4920 | 0.5040 | **0.5840** | +5.8% |
| **MRR** | 0.6302 | 0.6477 | 0.6625 | **0.7640** | **+21.2%** |
| **NDCG@5** | 0.6492 | 0.6372 | 0.6527 | **0.7543** | +16.2% |
| **Avg Latency** | 1.34s | **0.29s** | 1.52s | 3.59s | — |

**Key findings:**
- **Cross-encoder reranker delivers the largest gain**: MRR +21.2%, Hit Rate +37.5% over dense-only
- **BM25 alone beats dense on recall** — Indian legal queries contain specific section numbers and citations where exact keyword matching excels
- **Citation-aware RRF** (BM25 weighted 1.5× when citations detected) provides marginal improvement; most queries already contain citations
- Full pipeline: Hybrid Retrieval → RRF Fusion → Cross-Encoder Reranker → Top-4 → LLM

### End-to-End System Performance (v2.0 — Production Pipeline)

Vector Search (ChromaDB, all-MiniLM-L6-v2) + Situation-Aware Template Response:

| Metric | Score | Description |
|--------|------:|-------------|
| **Precision@1** | 0.5959 | 59.6% of top-1 retrievals are relevant |
| **Precision@3** | 0.4977 | 49.8% of top-3 retrievals are relevant |
| **Precision@5** | 0.3822 | 38.2% of top-5 retrievals are relevant |
| **Recall@1** | 0.2694 | Top-1 captures 26.9% of all relevant content |
| **Recall@3** | 0.5765 | Top-3 captures 57.7% of all relevant content |
| **Recall@5** | 0.7260 | Top-5 captures 72.6% of all relevant content |
| **MRR** | 0.6444 | Mean Reciprocal Rank |
| **NDCG@5** | 0.6572 | Normalized Discounted Cumulative Gain |
| **Avg latency** | 0.93s | Average response time per query |

Run evaluation yourself:
```bash
# Full evaluation pipeline
python run_experiments.py

# Compare all retrieval strategies
python evaluation/compare_all.py --max-samples 50
```

## Features

- **Hybrid RAG Chat Engine** — BM25 + Dense retrieval with RRF fusion and cross-encoder reranking over 59K legal chunks
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

### Configuration Flags (backend/chat_engine_rag.py)

```python
USE_HYBRID_RETRIEVAL = True   # Toggle hybrid BM25+Dense retrieval
USE_RERANKER = True            # Cross-encoder reranking (requires model download)
USE_CITATION_BOOST = True      # Boost BM25 weight when legal citations detected
```

Set all three to `False` to revert to v2.0 dense-only behavior.

## New Files (v2.1)

| File | Purpose |
|------|---------|
| `backend/bm25_retriever.py` | BM25 index built from ChromaDB chunks; tokenizer handles legal citations |
| `backend/rrf_fusion.py` | RRF fusion with citation-aware BM25 boosting |
| `backend/hybrid_retrieval.py` | Orchestrates BM25 + Dense → RRF → optional cross-encoder reranker |
| `evaluation/compare_all.py` | Benchmarks all 6 retrieval strategies (dense, BM25, hybrid, hybrid+reranker, citation-aware) |

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

- **Backend**: Python 3.10, FastAPI, Motor (async MongoDB), ChromaDB, rank-bm25, sentence-transformers (all-MiniLM-L6-v2), cross-encoder/ms-marco-MiniLM-L-6-v2
- **Frontend**: React 18, TypeScript, Material-UI
- **Retrieval**: Hybrid BM25 + Dense Vector + RRF Fusion + Cross-Encoder Reranker
- **Infrastructure**: Render Free Tier, MongoDB Atlas, optional Redis

## License

Copyright © 2025 Shankar M Darur. All Rights Reserved.
