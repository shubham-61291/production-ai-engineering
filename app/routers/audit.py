import logging
import uuid
import os
import tempfile
import shutil
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Depends, UploadFile, File, Form
from app.core.limiter import limiter
from app.core.auth import validate_api_key
from app.core.cache import redis_cache
from app.core.document_parser import extract_text_from_file
from app.core.audit_workflow import run_audit_workflow
from app.core.utils import generate_audit_pdf, upload_to_gcs
from app.core.config import settings
from app.models.schemas import AuditStatusResponse, AuditReportResponse

router = APIRouter()
logger = logging.getLogger(__name__)

async def run_audit_job(job_id: str, contract_text: str, session_id: str = None):
    try:
        await redis_cache.set_audit_job(job_id, {"status": "running", "progress": "Starting audit...", "session_id": session_id}, ttl=3600)
        report = await run_audit_workflow(contract_text)

        pdf_filename = f"audit_{job_id}.pdf"
        pdf_path = generate_audit_pdf(report, pdf_filename)

        pdf_url = None
        if settings.REPORT_STORAGE == "gcs" and settings.GCS_BUCKET_NAME:
            try:
                gcs_path = f"audit_reports/{pdf_filename}"
                pdf_url = upload_to_gcs(pdf_path, gcs_path)
            except Exception as e:
                logger.error(f"GCS upload failed: {e}")
        else:
            pdf_url = f"/api/v1/audit/{job_id}/report"

        result_data = {
            "status": "completed",
            "progress": "Audit complete",
            "report": report.model_dump(),
            "pdf_filename": pdf_filename,
            "pdf_url": pdf_url,
            "session_id": session_id,
        }
        await redis_cache.set_audit_job(job_id, result_data, ttl=3600)
        logger.info(f"Audit job {job_id} completed.")

    except Exception as e:
        logger.exception(f"Audit job {job_id} failed")
        await redis_cache.set_audit_job(job_id, {"status": "failed", "error": str(e), "session_id": session_id}, ttl=3600)

@router.post("/audit", response_model=dict)
@limiter.limit("50/minute")
async def start_audit(
    request: Request,
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    api_key: str = Depends(validate_api_key),
):
    contract_text = ""

    if file and file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in {".pdf", ".docx", ".txt", ".md"}:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        try:
            contract_text = extract_text_from_file(tmp_path, ext)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to extract text: {str(e)}")
        finally:
            os.unlink(tmp_path)
    elif text:
        contract_text = text
    else:
        raise HTTPException(status_code=400, detail="Either file or text must be provided")

    if not contract_text.strip():
        raise HTTPException(status_code=400, detail="No text extracted")

    job_id = str(uuid.uuid4())
    await redis_cache.set_audit_job(job_id, {"status": "pending", "progress": "Job queued", "session_id": session_id}, ttl=3600)
    background_tasks.add_task(run_audit_job, job_id, contract_text, session_id)

    return {"job_id": job_id, "status": "pending"}

@router.get("/audit/{job_id}/status", response_model=AuditStatusResponse)
@limiter.limit("50/minute")
async def get_audit_status(request: Request, job_id: str, api_key: str = Depends(validate_api_key)):
    data = await redis_cache.get_audit_job(job_id)
    if not data:
        raise HTTPException(status_code=404, detail="Job not found")
    return AuditStatusResponse(job_id=job_id, **data)

@router.get("/audit/{job_id}/report")
@limiter.limit("50/minute")
async def download_audit_report(request: Request, job_id: str, api_key: str = Depends(validate_api_key)):
    data = await redis_cache.get_audit_job(job_id)
    if not data:
        raise HTTPException(status_code=404, detail="Job not found")
    if data.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Audit not completed")
    pdf_filename = data.get("pdf_filename")
    if not pdf_filename:
        raise HTTPException(status_code=404, detail="PDF not generated")
    pdf_path = os.path.join(settings.REPORTS_DIR, pdf_filename)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file missing")
    from fastapi.responses import FileResponse
    return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_filename)

@router.get("/audit/{job_id}/result", response_model=AuditReportResponse)
@limiter.limit("50/minute")
async def get_audit_result(request: Request, job_id: str, api_key: str = Depends(validate_api_key)):
    data = await redis_cache.get_audit_job(job_id)
    if not data:
        raise HTTPException(status_code=404, detail="Job not found")
    return AuditReportResponse(job_id=job_id, report=data.get("report"))
