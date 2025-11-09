from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from . import models, schemas

async def create_scan(db: AsyncSession, patient_id: str, input_meta: dict):
    obj = models.ScanRecord(patient_id=patient_id, input_meta=input_meta, status="pending")
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def update_scan_result(db: AsyncSession, scan_id: int, ml_result: dict, status: str = "done"):
    q = await db.execute(select(models.ScanRecord).where(models.ScanRecord.id == scan_id))
    obj = q.scalar_one()
    obj.ml_result = ml_result
    obj.status = status
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def get_scan(db: AsyncSession, scan_id: int):
    q = await db.execute(select(models.ScanRecord).where(models.ScanRecord.id == scan_id))
    return q.scalar_one_or_none()
