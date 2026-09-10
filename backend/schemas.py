from typing import Dict, List, Optional
from pydantic import BaseModel

#modelele Pydantic definesc structura răspunsurilor JSON returnate de endpoint-urile API-ului


class EmotionResponse(BaseModel):
    #răspunsul returnat pentru analiza unei imagini sau a unui cadru webcam
    emotie_dominanta: str
    detalii_procente: Dict[str, float]
    face_confidence: float
    face_detected: bool
    fisier: Optional[str] = None


class VideoFrameEmotion(BaseModel):
    #rezultatul analizei pentru un cadru individual extras din videoclip
    frame_index: int
    time_seconds: float
    emotie_dominanta: str
    detalii_procente: Dict[str, float]
    face_detected: bool
    face_confidence: float


class VideoAnalysisResponse(BaseModel):
    #răspunsul complet returnat după analiza unui videoclip
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
    #structura utilizată pentru răspunsurile de eroare
    eroare: str