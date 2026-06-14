# SPECTER System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         SPECTER System                           │
│                    AI Legal Assistant Platform                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                          Frontend Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  React + TypeScript + Vite                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Login/  │  │   Chat   │  │  Upload  │  │ Contact  │       │
│  │  Signup  │  │  System  │  │   Docs   │  │  Lawyer  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                  │
│  Features:                                                       │
│  • Multi-language support (6 languages)                         │
│  • Voice assistant integration                                  │
│  • Usage tracking display                                       │
│  • Subscription management                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP/REST API
┌─────────────────────────────────────────────────────────────────┐
│                         Backend Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI + Python 3.9                                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                    API Endpoints                        │    │
│  ├────────────────────────────────────────────────────────┤    │
│  │  /auth/*        - Authentication & Authorization        │    │
│  │  /chat          - Legal Q&A Chat                        │    │
│  │  /legal/*       - Document Upload & Analysis            │    │
│  │  /api/*         - Contact Lawyer Service                │    │
│  │  /payment/*     - Subscription Management               │    │
│  │  /usage         - Usage Statistics                      │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Processing Layer                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │  Document        │  │  Legal           │                    │
│  │  Processor       │  │  Analyzer        │                    │
│  ├──────────────────┤  ├──────────────────┤                    │
│  │ • PDF Extract    │  │ • Summarize      │                    │
│  │ • DOCX Extract   │  │ • Translate      │                    │
│  │ • TXT Extract    │  │ • Verify         │                    │
│  │ • OCR (Images)   │  │ • Type ID        │                    │
│  └──────────────────┘  └──────────────────┘                    │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │  Chat Engine     │  │  Usage           │                    │
│  │  (RAG)           │  │  Tracker         │                    │
│  ├──────────────────┤  ├──────────────────┤                    │
│  │ • Query Match    │  │ • Question Count │                    │
│  │ • Fuzzy Search   │  │ • Upload Count   │                    │
│  │ • Answer Gen     │  │ • Limit Enforce  │                    │
│  └──────────────────┘  └──────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      External Services                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   MongoDB    │  │    Ollama    │  │  Tesseract   │         │
│  │   Database   │  │     LLM      │  │     OCR      │         │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤         │
│  │ • Users      │  │ • llama2     │  │ • Image OCR  │         │
│  │ • Sessions   │  │ • Summaries  │  │ • PDF OCR    │         │
│  │ • Usage Data │  │ • Translation│  │              │         │
│  │ • Contacts   │  │ • Verification│ │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │   ChromaDB   │  │    Email     │                            │
│  │   Vector DB  │  │   Service    │                            │
│  ├──────────────┤  ├──────────────┤                            │
│  │ • Embeddings │  │ • SMTP       │                            │
│  │ • FAQ Search │  │ • Lawyer     │                            │
│  │              │  │   Contact    │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### 1. Document Upload & Analysis Flow

```
User
  │
  ├─→ Upload Document (PDF/DOCX/TXT/Image)
  │
  ↓
Frontend (React)
  │
  ├─→ POST /legal/upload_doc
  │   └─→ Headers: Authorization (if logged in)
  │   └─→ Body: FormData with file
  │
  ↓
Backend API (FastAPI)
  │
  ├─→ Check Authentication
  │   └─→ If authenticated: Check upload limits
  │
  ├─→ Document Processor
  │   ├─→ Save file temporarily
  │   ├─→ Extract text
  │   │   ├─→ TXT: Direct read
  │   │   ├─→ DOCX: python-docx
  │   │   ├─→ PDF: PyPDF2 → OCR if needed
  │   │   └─→ Image: Tesseract OCR
  │   └─→ Delete file (privacy)
  │
  ├─→ Legal Analyzer
  │   └─→ Identify document type
  │       ├─→ Pattern matching (fast)
  │       └─→ LLM fallback (if needed)
  │
  ├─→ Increment usage count (if authenticated)
  │
  └─→ Return: {text, doc_type, filename}
  │
  ↓
Frontend
  │
  ├─→ Display document type
  ├─→ Show action buttons (Summarize/Translate/Verify)
  │
  └─→ User selects action
      │
      ├─→ POST /legal/analyze_doc
      │   └─→ Body: {text, doc_type, action, target_lang}
      │
      ↓
      Backend API
      │
      ├─→ Legal Analyzer
      │   ├─→ Summarize: Generate structured summary
      │   ├─→ Translate: Translate to target language
      │   └─→ Verify: Check legal compliance
      │       │
      │       └─→ Ollama LLM
      │           └─→ Generate analysis
      │
      └─→ Return: {summary/translation/verification}
      │
      ↓
      Frontend
      │
      └─→ Display results with formatting
```

### 2. Chat System Flow

```
User
  │
  ├─→ Type legal question
  │
  ↓
Frontend
  │
  ├─→ POST /chat
  │   └─→ Headers: Authorization
  │   └─→ Body: {message, target_lang}
  │
  ↓
Backend API
  │
  ├─→ Check Authentication
  ├─→ Check question limits
  │
  ├─→ Chat Engine (RAG)
  │   ├─→ Try exact match in legal DB
  │   ├─→ Try fuzzy matching
  │   └─→ Calculate confidence
  │
  ├─→ Increment question count
  │
  └─→ Return: {answer, sources, confidence}
  │
  ↓
Frontend
  │
  └─→ Display answer with formatting
```

### 3. Authentication Flow

```
User
  │
  ├─→ Signup/Login
  │
  ↓
Frontend
  │
  ├─→ POST /auth/signup or /auth/login
  │   └─→ Body: {email, password, ...}
  │
  ↓
Backend API
  │
  ├─→ Auth Service
  │   ├─→ Validate credentials
  │   ├─→ Hash password (bcrypt)
  │   ├─→ Generate JWT token
  │   └─→ Store in MongoDB
  │
  └─→ Return: {token, user_data}
  │
  ↓
Frontend
  │
  ├─→ Store token in localStorage
  ├─→ Set user state
  └─→ Redirect to home
```

## Component Details

### Frontend Components

```
src/
├── App.tsx                 # Main app component
├── Login.tsx              # Login page
├── Signup.tsx             # Signup page
├── UserProfile.tsx        # User profile & subscription
├── Dashboard.tsx          # User dashboard
├── VoiceAssistant.js      # Voice commands
├── LegalServicesData.js   # Legal services info
└── config.ts              # API configuration
```

### Backend Modules

```
backend/
├── main.py                      # FastAPI app & routes
├── auth_mongo.py                # Authentication
├── legal_api.py                 # Document upload/analysis
├── document_processor.py        # Text extraction
├── legal_analysis.py            # AI analysis
├── chat_engine_rag.py          # Chat system
├── comprehensive_legal_db.py    # Legal knowledge base
├── usage_tracker.py             # Usage limits
├── contact_service.py           # Lawyer contact
├── payment_api.py               # Subscriptions
└── vector_rag_trainer.py        # RAG training
```

## Technology Stack

### Frontend
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **Styling:** CSS (custom)
- **State Management:** React Hooks
- **HTTP Client:** Fetch API

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.9
- **Authentication:** JWT + bcrypt
- **Database:** MongoDB (Motor async driver)
- **Vector DB:** ChromaDB
- **LLM:** Ollama (llama2)
- **OCR:** Tesseract + pdf2image
- **Document Processing:** PyPDF2, python-docx, Pillow

### Infrastructure
- **Backend Hosting:** Render / Railway
- **Frontend Hosting:** Netlify / Vercel
- **Database:** MongoDB Atlas
- **LLM:** Self-hosted Ollama or cloud API

## Security Features

1. **Authentication:** JWT-based with secure token storage
2. **Password Hashing:** bcrypt with salt
3. **Authorization:** Role-based access control
4. **File Security:** Immediate deletion after processing
5. **Input Validation:** Pydantic models
6. **CORS:** Configured for specific origins
7. **Rate Limiting:** Usage tracking and limits
8. **HTTPS:** Required for production

## Scalability Considerations

1. **Horizontal Scaling:** Stateless API design
2. **Database Indexing:** MongoDB indexes on user_id, email
3. **Caching:** Can add Redis for session/response caching
4. **Load Balancing:** Multiple API instances
5. **CDN:** Static assets via CDN
6. **Async Processing:** Motor for async MongoDB operations
7. **Connection Pooling:** MongoDB connection pool

## Monitoring & Logging

1. **Health Checks:** `/health` endpoint
2. **Logging:** Python logging module
3. **Error Tracking:** Exception handling with logging
4. **Usage Analytics:** MongoDB usage collection
5. **Performance Metrics:** Response time tracking

---

**Last Updated:** 2025-12-30  
**Version:** 1.0.0
