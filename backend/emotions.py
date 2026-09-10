from deepface import DeepFace


#scor minim de incredere pentru a considera daca o fată a fost detectată în imagine sau cadru video
FACE_CONFIDENCE_THRESHOLD = 0.4


def analyze_emotion(image_path: str) -> dict:
    """
     Analiza emoției dintr-o imagine.

    Funcția utilizează DeepFace pentru detectarea feței și clasificarea
    emoției dominante, returnând distribuția procentuală a emoțiilor și
    nivelul de încredere al detecției faciale.
    """

    try:
        result = DeepFace.analyze(
            img_path=image_path,
            actions=["emotion"],
            enforce_detection=False
        )

        face_data = result[0] if isinstance(result, list) else result

        
        emotion_scores = { 
            emotion: float(score)
            for emotion, score in face_data["emotion"].items()
        }
 

        face_confidence = float(face_data.get("face_confidence", 0.0))
        face_detected = face_confidence >= FACE_CONFIDENCE_THRESHOLD

        return {
            "emotie_dominanta": face_data["dominant_emotion"],
            "detalii_procente": emotion_scores,
            "face_confidence": round(face_confidence, 3),
            "face_detected": face_detected,
        }

    except Exception as e:
        error_msg = str(e).lower()
        if "cannot identify image" in error_msg or "invalid" in error_msg:
            return {"eroare": "The image file appears to be corrupted or invalid."}
        return {"eroare": "An unexpected error occurred during analysis."}


def analyze_emotion_from_frame(frame) -> dict:
    """
    Analiza emoției dintr-un cadru video sau webcam

    Funcția este utilizată pentru procesarea cadrelor extrase din videoclipuri
    sau capturate în timp real prin camera web.
    """
    try:
        result = DeepFace.analyze(
            img_path=frame,
            actions=["emotion"],
            enforce_detection=False
        )
        

        face_data = result[0] if isinstance(result, list) else result

        
        emotion_scores = {
            emotion: float(score)
            for emotion, score in face_data["emotion"].items()
        }

        face_confidence = float(face_data.get("face_confidence", 0.0))
        face_detected = face_confidence >= FACE_CONFIDENCE_THRESHOLD

        return {
            "emotie_dominanta": face_data["dominant_emotion"],
            "detalii_procente": emotion_scores,
            "face_confidence": round(face_confidence, 3),
            "face_detected": face_detected,
        }

    except Exception as e:
        error_msg = str(e).lower()
        if "cannot identify image" in error_msg or "invalid" in error_msg:
            return {"eroare": "The video frame appears to be corrupted or invalid."}
        return {"eroare": "An unexpected error occurred during frame analysis."}