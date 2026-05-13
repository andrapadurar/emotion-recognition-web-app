import os
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse

from app.config import (
    IMAGE_UPLOAD_DIR,
    VIDEO_UPLOAD_DIR,
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_VIDEO_EXTENSIONS,
    DEFAULT_FRAME_SKIP,
    MAX_IMAGE_SIZE_MB,
    MAX_VIDEO_SIZE_MB,
)
from app.emotions import analyze_emotion
from app.schemas import EmotionResponse, VideoAnalysisResponse
from app.utils import (
    ensure_folder_exists,
    is_allowed_extension,
    generate_unique_filename,
    get_file_size_mb,
)
from app.video_analysis import analyze_video_emotions

app = FastAPI(
    title="Emotion Recognition API",
    description="API pentru recunoașterea emoțiilor din imagini și videoclipuri",
    version="1.0.0"
)


@app.get("/")
def home():
    return {"message": "Emotion recognition API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze-image/", response_model=EmotionResponse)
async def analyze_image(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Fișierul nu are nume.")

    if not is_allowed_extension(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail="Format invalid. Sunt permise doar: jpg, jpeg, png."
        )

    ensure_folder_exists(IMAGE_UPLOAD_DIR)

    unique_filename = generate_unique_filename(file.filename)
    file_location = os.path.join(IMAGE_UPLOAD_DIR, unique_filename)

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size_mb = get_file_size_mb(file_location)
        if file_size_mb > MAX_IMAGE_SIZE_MB:
            raise HTTPException(
                status_code=413,
                detail=f"Imaginea este prea mare. Maxim permis: {MAX_IMAGE_SIZE_MB} MB."
            )

        result = analyze_emotion(file_location)

        if "eroare" in result:
            raise HTTPException(status_code=500, detail=result["eroare"])

        result["fisier"] = unique_filename
        return result

    finally:
        file.file.close()
        if os.path.exists(file_location):
            os.remove(file_location)


@app.post("/analyze-video/", response_model=VideoAnalysisResponse)
async def analyze_video(
    file: UploadFile = File(...),
    frame_skip: int = Query(DEFAULT_FRAME_SKIP, ge=1, le=60)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Fișierul nu are nume.")

    if not is_allowed_extension(file.filename, ALLOWED_VIDEO_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail="Format invalid. Sunt permise doar: mp4, avi, mov, mkv."
        )

    ensure_folder_exists(VIDEO_UPLOAD_DIR)

    unique_filename = generate_unique_filename(file.filename)
    file_location = os.path.join(VIDEO_UPLOAD_DIR, unique_filename)

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size_mb = get_file_size_mb(file_location)
        if file_size_mb > MAX_VIDEO_SIZE_MB:
            raise HTTPException(
                status_code=413,
                detail=f"Videoclipul este prea mare. Maxim permis: {MAX_VIDEO_SIZE_MB} MB."
            )

        result = analyze_video_emotions(file_location, frame_skip=frame_skip)

        if "eroare" in result:
            raise HTTPException(status_code=500, detail=result["eroare"])

        result["fisier"] = unique_filename
        return result

    finally:
        file.file.close()
        if os.path.exists(file_location):
            os.remove(file_location)


@app.get("/supported-formats")
def supported_formats():
    return {
        "image_formats": sorted(list(ALLOWED_IMAGE_EXTENSIONS)),
        "video_formats": sorted(list(ALLOWED_VIDEO_EXTENSIONS)),
    }