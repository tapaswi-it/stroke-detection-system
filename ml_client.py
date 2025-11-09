import httpx
from .config import settings
from typing import Dict, Any

class MLServiceError(Exception):
    pass

async def call_ml_api(payload: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    """Call external ML server. Payload comes from validated schema.
       This function is intentionally generic — your friend provides the actual ML endpoint."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.post(settings.ML_API_URL, json=payload)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            raise MLServiceError(f"ML API returned bad status {exc.response.status_code}") from exc
        except Exception as exc:
            raise MLServiceError("Failed to reach ML service") from exc
