from fastapi import APIRouter, UploadFile, File, HTTPException, Body, Request, Query
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from document_processor import document_processor
from legal_analysis import legal_analyzer
from doc_qa_service import index_document, answer_doc_question, remove_document_index
import logging
import uuid

logger = logging.getLogger(__name__)
legal_router = APIRouter()

class AnalysisRequest(BaseModel):
    text: str
    doc_type: str
    action: str
    target_lang: str = "Hindi"

class DocQARequest(BaseModel):
    question: str
    doc_namespace: str

class RiskScoreRequest(BaseModel):
    text: str
    doc_type: str

class TimelineRequest(BaseModel):
    text: str
    doc_type: str

@legal_router.get("/legal")
async def get_legal_info():
    return {"message": "Legal API endpoint"}

@legal_router.post("/upload_doc")
async def upload_document(request: Request, file: UploadFile = File(...)):
    try:
        from auth_mongo import get_current_user
        from usage_tracker import enforce_upload_limit, increment_upload_count

        auth_header = request.headers.get("Authorization")
        user = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            user = await get_current_user(credentials)
            await enforce_upload_limit(user)

        file_path = document_processor.save_upload(file)
        text = document_processor.extract_text(file_path)
        doc_type = legal_analyzer.identify_document_type(text)
        document_processor.cleanup(file_path)

        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from document.")

        doc_namespace = f"doc_{uuid.uuid4().hex[:12]}"
        chunk_count = index_document(text, doc_namespace, source_label=file.filename or "uploaded_doc")

        if user:
            await increment_upload_count(str(user["_id"]))

        return {
            "text": text,
            "doc_type": doc_type,
            "filename": file.filename,
            "doc_namespace": doc_namespace,
            "chunks_indexed": chunk_count,
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@legal_router.post("/analyze_doc")
async def analyze_document(request: AnalysisRequest):
    try:
        if request.action == "summarize":
            return legal_analyzer.summarize_document(request.text, request.doc_type)
        elif request.action == "translate":
            return {"translation": legal_analyzer.translate_document(request.text, request.target_lang)}
        elif request.action == "verify":
            return legal_analyzer.verify_legality(request.text, request.doc_type)
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@legal_router.post("/doc_qa")
async def doc_qa_endpoint(request: Request, qa_request: DocQARequest):
    try:
        from auth_mongo import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            await get_current_user(credentials)

        result = answer_doc_question(
            question=qa_request.question,
            doc_namespace=qa_request.doc_namespace,
        )
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Doc QA failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@legal_router.post("/risk_score")
async def risk_score_endpoint(request: RiskScoreRequest):
    try:
        result = legal_analyzer.extract_clauses_with_risk(request.text, request.doc_type)
        return result
    except Exception as e:
        logger.error(f"Risk score analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@legal_router.post("/timeline")
async def timeline_endpoint(request: TimelineRequest):
    try:
        result = legal_analyzer.extract_timeline(request.text, request.doc_type)
        return result
    except Exception as e:
        logger.error(f"Timeline extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@legal_router.delete("/doc_index/{doc_namespace}")
async def delete_doc_index(request: Request, doc_namespace: str):
    try:
        from auth_mongo import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            await get_current_user(credentials)

        remove_document_index(doc_namespace)
        return {"status": "deleted", "namespace": doc_namespace}
    except Exception as e:
        logger.error(f"Delete index failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
