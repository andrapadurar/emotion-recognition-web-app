from typing import Dict, List, Optional
from pydantic import BaseModel

# forma raspunsurilor JSON 

class EmotionResponse(BaseModel):
    emotie_dominanta: str
    detalii_procente: Dict[str, float]
    fisier: Optional[str] = None


class VideoFrameEmotion(BaseModel):
    frame_index: int
    time_seconds: float
    emotie_dominanta: str
    detalii_procente: Dict[str, float]


class VideoAnalysisResponse(BaseModel):
    fisier: Optional[str] = None
    total_frames: int
    fps: float
    durata_secunde: float
    frame_skip: int
    frame_count_analyzed: int
    emotie_dominanta_video: str
    distributie_emotii: Dict[str, int]
    frames: List[VideoFrameEmotion]
    medie_procente_video: Dict[str, float]


class ErrorResponse(BaseModel):
    eroare: str