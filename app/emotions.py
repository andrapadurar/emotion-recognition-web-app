from deepface import DeepFace

# logica de analiza cu DeepFace, pentru img si video

def analyze_emotion(image_path: str) -> dict:
    try:
        result = DeepFace.analyze(
            img_path=image_path,
            actions=["emotion"],
            enforce_detection=False
        )

        face_data = result[0] if isinstance(result, list) else result

        emotii_curate = {
            emotie: float(scor)
            for emotie, scor in face_data["emotion"].items()
        }

        return {
            "emotie_dominanta": face_data["dominant_emotion"],
            "detalii_procente": emotii_curate
        }

    except Exception as e:
        return {"eroare": str(e)}


def analyze_emotion_from_frame(frame) -> dict:
    try:
        result = DeepFace.analyze(
            img_path=frame,
            actions=["emotion"],
            enforce_detection=False
        )

        face_data = result[0] if isinstance(result, list) else result

        emotii_curate = {
            emotie: float(scor)
            for emotie, scor in face_data["emotion"].items()
        }

        return {
            "emotie_dominanta": face_data["dominant_emotion"],
            "detalii_procente": emotii_curate
        }

    except Exception as e:
        return {"eroare": str(e)}