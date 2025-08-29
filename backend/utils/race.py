# async def race_predictor(img_bytes):
#     return None


from deepface import DeepFace
import cv2
import numpy as np

async def race_predictor(img_bytes):
    try:
        # Decode image
        image = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            return "Unknown"

        # Analyze race using DeepFace
        result = DeepFace.analyze(
            img_path=image, 
            actions=['race'], 
            enforce_detection=False
        )

        # Handle both single face and multiple faces results
        if isinstance(result, list):
            result = result[0]

        race_scores = result['race']
        
        # Find the race with highest confidence
        predicted_race = max(race_scores, key=race_scores.get)
        
        return predicted_race

    except Exception as e:
        print(f"Error during race prediction: {e}")
        return "Unknown"