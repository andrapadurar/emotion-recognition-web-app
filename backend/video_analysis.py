from collections import Counter
import cv2
from backend.emotions import analyze_emotion_from_frame

#modul pentru analiza emoțiilor din videoclipuri


EMOTII = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]


def analyze_video_emotions(video_path: str, frame_skip: int = 10) -> dict:
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return {"eroare": "Could not open the video file. It may be corrupted or in an unsupported format."}

    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    
    if fps is None or fps <= 0:
        fps = 25.0

    
    if total_frames == 0:
        cap.release()
        return {"eroare": "The video file contains no frames."}

    durata_secunde = total_frames / fps if fps > 0 else 0

    frames_results = []
    emotii_video = []

    scoruri_totale = {emotie: 0.0 for emotie in EMOTII}
    frame_index = 0
    frame_count_valid = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            
            if frame_index % frame_skip == 0:
                result = analyze_emotion_from_frame(frame)

                if "eroare" not in result:
                    time_seconds = round(frame_index / fps, 2)

                
                    frame_data = {
                        "frame_index": frame_index,
                        "time_seconds": time_seconds,
                        "emotie_dominanta": result["emotie_dominanta"],
                        "detalii_procente": result["detalii_procente"],
                        "face_detected": result.get("face_detected", False),
                        "face_confidence": result.get("face_confidence", 0.0),
                    }

                    frames_results.append(frame_data)
                    emotii_video.append(result["emotie_dominanta"])

                    
                    for emotie in EMOTII:
                        scoruri_totale[emotie] += result["detalii_procente"].get(emotie, 0.0)

                    frame_count_valid += 1

            frame_index += 1

    finally:
        cap.release()

    
    if frame_count_valid == 0:
        return {
            "total_frames": total_frames,
            "fps": float(round(fps, 2)),
            "durata_secunde": round(durata_secunde, 2),
            "frame_skip": frame_skip,
            "frame_count_analyzed": 0,
            "emotie_dominanta_video": "necunoscuta",
            "distributie_emotii": {},
            "medie_procente_video": {},
            "frames": []
        }

    
    distributie = dict(Counter(emotii_video))
    medie_procente_video = {
        emotie: round(scoruri_totale[emotie] / frame_count_valid, 2)
        for emotie in EMOTII
    }
    emotie_dominanta_video = max(medie_procente_video, key=medie_procente_video.get)

    
    frames_with_face = sum(1 for f in frames_results if f.get("face_detected", False))
    face_ratio = frames_with_face / len(frames_results) if frames_results else 0

    if face_ratio < 0.2:
        emotie_dominanta_video = "necunoscuta"

    
    return {
        "total_frames": total_frames,
        "fps": float(round(fps, 2)),
        "durata_secunde": round(durata_secunde, 2),
        "frame_skip": frame_skip,
        "frame_count_analyzed": len(frames_results),
        "emotie_dominanta_video": emotie_dominanta_video,
        "distributie_emotii": distributie,
        "medie_procente_video": medie_procente_video,
        "frames": frames_results
    }