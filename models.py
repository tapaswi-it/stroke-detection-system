from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from .database import Base

class ScanRecord(Base):
    __tablename__ = "scan_records"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, index=True, nullable=False)
    input_meta = Column(JSON, nullable=True)   # any metadata (e.g., image filename, sensor info)
    ml_result = Column(JSON, nullable=True)
    status = Column(String, default="pending", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
