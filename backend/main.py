import os
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.config import (
    IMAGE_UPLOAD_DIR,
    VIDEO_UPLOAD_DIR,
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_VIDEO_EXTENSIONS,
    DEFAULT_FRAME_SKIP,
    MAX_IMAGE_SIZE_MB,
    MAX_VIDEO_SIZE_MB,
)
from backend.emotions import analyze_emotion
from backend.schemas import EmotionResponse, VideoAnalysisResponse
from backend.utils import (
    ensure_folder_exists,
    is_allowed_extension,
    generate_unique_filename,
    get_file_size_mb,
)
from backend.video_analysis import analyze_video_emotions

app = FastAPI(
    title="Emotion Recognition API",
    description="API for emotion recognition from images and videos",
    version="1.0.0"
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173"
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#endpoint de bază utilizat pentru verificarea funcționarii API-ului
@app.get("/")
def home():
    return {"message": "Emotion recognition API is running"}

#endpoint simplu de verificare a starii serverului
@app.get("/health")
def health():
    return {"status": "ok"}


#endpoint pentru analiza emoțiilor dintr-o imagine 
@app.post("/analyze-image/", response_model=EmotionResponse)
async def analyze_image(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="The file has no name.")


    if not is_allowed_extension(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail="Invalid format. Only jpg, jpeg, and png files are allowed."
        )

    ensure_folder_exists(IMAGE_UPLOAD_DIR)

    unique_filename = generate_unique_filename(file.filename)
    file_location = os.path.join(IMAGE_UPLOAD_DIR, unique_filename)

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        
        if os.path.getsize(file_location) == 0:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty."
            )
    

        file_size_mb = get_file_size_mb(file_location)
        if file_size_mb > MAX_IMAGE_SIZE_MB:
            raise HTTPException(
                status_code=413,
                detail=f"Image is too large. Maximum allowed size: {MAX_IMAGE_SIZE_MB} MB."
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


#endpoint pentru analiza emoțiilor faciale dintr-un videoclip
@app.post("/analyze-video/", response_model=VideoAnalysisResponse)
async def analyze_video(
    file: UploadFile = File(...),
    frame_skip: int = Query(DEFAULT_FRAME_SKIP, ge=1, le=60)
):
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="The file has no name.")

    
    if not is_allowed_extension(file.filename, ALLOWED_VIDEO_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail="Invalid format. Only mp4, avi, mov, and mkv files are allowed."
        )

    ensure_folder_exists(VIDEO_UPLOAD_DIR)


    unique_filename = generate_unique_filename(file.filename)
    file_location = os.path.join(VIDEO_UPLOAD_DIR, unique_filename)

    try:
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        
        if os.path.getsize(file_location) == 0:
            raise HTTPException(
                status_code=400,
                detail="The uploaded video file is empty."
            )

        
        file_size_mb = get_file_size_mb(file_location)
        if file_size_mb > MAX_VIDEO_SIZE_MB:
            raise HTTPException(
                status_code=413,
                detail=f"Video is too large. Maximum allowed size: {MAX_VIDEO_SIZE_MB} MB."
            )

        #analizăm videoclipul prin extragerea și procesarea cadrelor
        result = analyze_video_emotions(file_location, frame_skip=frame_skip)

        
        if "eroare" in result:
            raise HTTPException(status_code=500, detail=result["eroare"])

        
        result["fisier"] = unique_filename
        return result

    finally:
        file.file.close()
        if os.path.exists(file_location):
            os.remove(file_location)


#endpoint care returnează formatele de fișiere acceptate de aplicatie
@app.get("/supported-formats")
def supported_formats():
    return {
        "image_formats": sorted(list(ALLOWED_IMAGE_EXTENSIONS)),
        "video_formats": sorted(list(ALLOWED_VIDEO_EXTENSIONS)),
    }