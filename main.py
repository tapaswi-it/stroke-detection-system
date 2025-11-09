from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from . import schemas, crud, ml_client, database, logger
from .config import settings
from typing import Any

log = logger.get_logger(__name__)
app = FastAPI(title="Stroke Detection Backend")

# startup/shutdown: create tables if not exist (simple approach)
@app.on_event("startup")
async def startup():
    async with database.engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.create_all)
    log.info("Database tables ensured")

@app.post("/scan/", response_model=schemas.ScanOut, status_code=201)
async def create_scan(scan_in: schemas.ScanIn, db: AsyncSession = Depends(database.get_db)):
    # 1) save record with status pending
    try:
        input_meta = scan_in.metadata or {}
        record = await crud.create_scan(db, patient_id=scan_in.patient_id, input_meta=input_meta)
        log.info("Created scan record %s for patient %s", record.id, record.patient_id)
    except Exception as exc:
        log.exception("DB insert failed")
        raise HTTPException(status_code=500, detail="Failed to create scan record")

    # 2) prepare payload for ML API
    ml_payload = {
        "patient_id": scan_in.patient_id,
        "image_base64": scan_in.image_base64,
        "metadata": input_meta
    }

    # 3) call ML service
    try:
        ml_resp = await ml_client.call_ml_api(ml_payload)
        log.info("ML response received for record %s", record.id)
    except ml_client.MLServiceError as exc:
        log.exception("ML service error")
        # update DB as failed
        await crud.update_scan_result(db, scan_id=record.id, ml_result={"error": str(exc)}, status="failed")
        # respond but indicate ML failed
        raise HTTPException(status_code=502, detail="ML service error")

    # 4) update DB
    try:
        updated = await crud.update_scan_result(db, scan_id=record.id, ml_result=ml_resp, status="done")
    except Exception:
        log.exception("Failed to update record with ML result")
        raise HTTPException(status_code=500, detail="Failed to update scan with result")

    return schemas.ScanOut(
        id=updated.id,
        patient_id=updated.patient_id,
        status=updated.status,
        ml_result=updated.ml_result
    )

@app.get("/scan/{scan_id}", response_model=schemas.ScanOut)
async def get_scan(scan_id: int, db: AsyncSession = Depends(database.get_db)):
    rec = await crud.get_scan(db, scan_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")
    return schemas.ScanOut(id=rec.id, patient_id=rec.patient_id, status=rec.status, ml_result=rec.ml_result)

# Global exception handlers (example)
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    log.warning("HTTPException: %s", exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
