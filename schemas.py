from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ScanIn(BaseModel):
    patient_id: str = Field(..., min_length=1)
    # Example: frontend can send image as base64 or a reference to an uploaded file
    image_base64: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MLResult(BaseModel):
    stroke_prob: float
    labels: Optional[Dict[str, float]] = None
    details: Optional[Dict[str, Any]] = None

class ScanOut(BaseModel):
    id: int
    patient_id: str
    status: str
    ml_result: Optional[MLResult] = None
