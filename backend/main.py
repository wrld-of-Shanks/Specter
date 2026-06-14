from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request, UploadFile, File, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
import sqlite3
import logging

from doc_parser import parse_and_chunk
from embed_store import add_chunks_to_db
from auth_mongo import auth_router
from legal_api import legal_router
from contact_service import contact_router
from payment_api import payment_router
from lawyer_api import lawyer_router
from whatsapp_service import whatsapp_router

app = FastAPI(title="SPECTER Legal Assistant API", version="2.0.0")

@app.on_event("startup")
async def startup_event():
    from mongodb_config import connect_to_mongo
    from user_memory_store import ensure_indexes
    from kb_seeder import seed_kb_if_empty
    from lawyer_service import ensure_lawyer_indexes

    await connect_to_mongo()
    await ensure_indexes()
    await ensure_lawyer_indexes()

    import asyncio
    asyncio.get_event_loop().run_in_executor(None, seed_kb_if_empty)

@app.on_event("shutdown")
async def shutdown_event():
    from mongodb_config import close_mongo_connection
    await close_mongo_connection()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(legal_router, prefix="/legal", tags=["legal"])
app.include_router(contact_router, prefix="/api", tags=["contact"])
app.include_router(payment_router, prefix="/payment", tags=["payment"])
app.include_router(lawyer_router, prefix="/api", tags=["lawyer"])
app.include_router(whatsapp_router, prefix="/api", tags=["whatsapp"])

@app.post("/upload_doc")
async def upload_doc_fallback(request: Request, file: UploadFile = File(...)):
    from legal_api import upload_document
    return await upload_document(request, file)

@app.post("/analyze_doc")
async def analyze_doc_fallback(request: Request):
    from legal_api import analyze_document, AnalysisRequest
    data = await request.json()
    analysis_request = AnalysisRequest(**data)
    return await analyze_document(analysis_request)

@app.get("/")
async def root():
    return {"message": "SPECTER Legal Assistant API v2.0 is running"}

@app.get("/health")
async def health_check():
    from local_llm import get_google_api_key
    api_key = get_google_api_key()
    return {
        "status": "healthy",
        "google_api_key_detected": api_key is not None and len(api_key) > 0,
        "env_keys": [k for k in os.environ.keys() if "API" in k or "KEY" in k or "URL" in k or "MONGODB" in k]
    }

@app.get("/usage")
async def get_usage(request: Request):
    try:
        from auth_mongo import get_current_user
        from usage_tracker import get_usage_stats
        from fastapi.security import HTTPAuthorizationCredentials

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"error": "Authentication required"})

        token = auth_header.replace("Bearer ", "")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        user = await get_current_user(credentials)
        stats = await get_usage_stats(user)
        return stats

    except HTTPException as he:
        return JSONResponse(status_code=he.status_code, content={"error": he.detail})
    except Exception as e:
        logging.error(f"Usage stats error: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})

@app.post("/chat")
async def chat_endpoint(request: Request):
    try:
        from auth_mongo import get_current_user
        from usage_tracker import enforce_question_limit, increment_question_count
        from fastapi.security import HTTPAuthorizationCredentials
        from chat_engine_rag import answer_query_with_rag
        from user_memory_store import get_chat_history, append_message

        data = await request.json()
        user_message = data.get("message", "").strip()
        target_lang = data.get("target_lang", "english")
        reset_history = data.get("reset_history", False)

        if not user_message:
            return JSONResponse(status_code=400, content={"error": "Message cannot be empty"})

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"error": "Authentication required"})

        token = auth_header.replace("Bearer ", "")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        user = await get_current_user(credentials)
        user_id = str(user["_id"])

        await enforce_question_limit(user)

        if reset_history:
            from user_memory_store import clear_history
            await clear_history(user_id)

        history = await get_chat_history(user_id)

        response = await answer_query_with_rag(
            query=user_message,
            user_id=user_id,
            chat_history=history,
            namespace="global"
        )

        await append_message(user_id, "user", user_message)
        await append_message(user_id, "assistant", response["answer"])

        await increment_question_count(user_id)

        return {
            "answer": response["answer"],
            "sources": response.get("sources", []),
            "confidence": response.get("confidence", 0.0),
            "matched_chunks": response.get("matched_chunks", []),
            "low_confidence": response.get("low_confidence", False),
        }

    except HTTPException as he:
        return JSONResponse(status_code=he.status_code, content={"error": he.detail})
    except Exception as e:
        logging.error(f"Chat endpoint error: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Internal server error"})

@app.delete("/chat/history")
async def clear_chat_history(request: Request):
    try:
        from auth_mongo import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials
        from user_memory_store import clear_history

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"error": "Authentication required"})

        token = auth_header.replace("Bearer ", "")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        user = await get_current_user(credentials)
        await clear_history(str(user["_id"]))
        return {"status": "cleared"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    try:
        from auth_mongo import get_current_user
        from usage_tracker import enforce_upload_limit, increment_upload_count
        from fastapi.security import HTTPAuthorizationCredentials

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"error": "Authentication required"})

        token = auth_header.replace("Bearer ", "")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        user = await get_current_user(credentials)
        await enforce_upload_limit(user)

        import os as _os
        _os.makedirs("data/processed", exist_ok=True)
        content = await file.read()
        with open(f"data/processed/{file.filename}", "wb") as f:
            f.write(content)

        await increment_upload_count(str(user["_id"]))
        return {"filename": file.filename, "status": "uploaded"}

    except HTTPException as he:
        return JSONResponse(status_code=he.status_code, content={"error": he.detail})
    except Exception as e:
        logging.error(f"Upload endpoint error: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})

class LawyerContactRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str = ''
    caseType: str
    description: str = ''

@app.post('/contact-lawyer')
def contact_lawyer(request: LawyerContactRequest):
    smtp_user = os.getenv('LAWYER_SMTP_USER')
    smtp_pass = os.getenv('LAWYER_SMTP_PASS')
    smtp_to = os.getenv('LAWYER_RECEIVER_EMAIL')
    smtp_host = os.getenv('LAWYER_SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('LAWYER_SMTP_PORT', '587'))

    if not (smtp_user and smtp_pass and smtp_to):
        return {"status": "error", "message": "Email credentials not set in .env"}

    subject = f"New SPECTER Contact Request: {request.caseType}"
    body = f"""
Name: {request.name}
Email: {request.email}
Phone: {request.phone}
Case Type: {request.caseType}
Description: {request.description}
"""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = smtp_to

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, smtp_to, msg.as_string())
        return {"status": "success", "message": "Request sent to lawyer network."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to send email: {e}"}

@app.get("/admin/stats")
async def admin_stats(request: Request):
    from auth_mongo import get_current_user
    from fastapi.security import HTTPAuthorizationCredentials

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"error": "Authentication required"})
    token = auth_header.replace("Bearer ", "")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    user = await get_current_user(credentials)
    if user.get("email") not in ("admin@specter.app", "shankardarur158@gmail.com"):
        return JSONResponse(status_code=403, content={"error": "Admin access required"})

    from admin_service import get_platform_stats
    stats = await get_platform_stats()
    return stats

@app.get("/admin/queries/popular")
async def admin_popular_queries(request: Request, limit: int = Query(20, ge=1, le=100)):
    from auth_mongo import get_current_user
    from fastapi.security import HTTPAuthorizationCredentials

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"error": "Authentication required"})
    token = auth_header.replace("Bearer ", "")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    user = await get_current_user(credentials)
    if user.get("email") not in ("admin@specter.app", "shankardarur158@gmail.com"):
        return JSONResponse(status_code=403, content={"error": "Admin access required"})

    from admin_service import get_popular_queries
    queries = await get_popular_queries(limit=limit)
    return {"queries": queries, "count": len(queries)}

@app.get("/admin/dau")
async def admin_dau(request: Request, days: int = Query(30, ge=1, le=365)):
    from auth_mongo import get_current_user
    from fastapi.security import HTTPAuthorizationCredentials

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"error": "Authentication required"})
    token = auth_header.replace("Bearer ", "")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    user = await get_current_user(credentials)
    if user.get("email") not in ("admin@specter.app", "shankardarur158@gmail.com"):
        return JSONResponse(status_code=403, content={"error": "Admin access required"})

    from admin_service import get_dau_stats
    dau_data = await get_dau_stats(days=days)
    return {"dau": dau_data, "days": days}

@app.get("/admin/subscriptions")
async def admin_subscriptions(request: Request):
    from auth_mongo import get_current_user
    from fastapi.security import HTTPAuthorizationCredentials

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"error": "Authentication required"})
    token = auth_header.replace("Bearer ", "")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    user = await get_current_user(credentials)
    if user.get("email") not in ("admin@specter.app", "shankardarur158@gmail.com"):
        return JSONResponse(status_code=403, content={"error": "Admin access required"})

    from admin_service import get_subscription_stats
    return await get_subscription_stats()

@app.get("/admin/revenue")
async def admin_revenue(request: Request):
    from auth_mongo import get_current_user
    from fastapi.security import HTTPAuthorizationCredentials

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"error": "Authentication required"})
    token = auth_header.replace("Bearer ", "")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    user = await get_current_user(credentials)
    if user.get("email") not in ("admin@specter.app", "shankardarur158@gmail.com"):
        return JSONResponse(status_code=403, content={"error": "Admin access required"})

    from admin_service import get_revenue_stats
    return await get_revenue_stats()

@app.get("/templates/categories")
async def template_categories():
    from template_service import list_categories
    return list_categories()

@app.get("/templates/category/{category}")
async def templates_by_category(category: str):
    from template_service import list_templates_in_category
    templates = list_templates_in_category(category)
    if not templates:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    return {"category": category, "templates": templates}

@app.get("/templates/{template_id}")
async def template_detail(template_id: str):
    from template_service import get_template_structure
    structure = get_template_structure(template_id)
    if not structure:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    return structure

class TemplateGenerateRequest(BaseModel):
    template_id: str
    inputs: dict

@app.post("/templates/generate")
async def template_generate(request: TemplateGenerateRequest):
    try:
        from template_service import generate_template_document
        document = generate_template_document(request.template_id, request.inputs)
        return {"template_id": request.template_id, "document": document}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Template generation error: {e}")
        raise HTTPException(status_code=500, detail="Template generation failed")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
