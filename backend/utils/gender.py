# from deepface import DeepFace
# import numpy as np
# import os
# import cv2
# from PIL import Image

# async def gender_predictor(img_bytes):
#     genders = ['Female', 'Male']
#     try:

#         image_path = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

#         result = await DeepFace.analyze(img_path=image_path, actions=['gender'], enforce_detection=False)

#         gender_scores = result[0]['gender']
#         predicted_gender = genders[np.argmax(list(gender_scores.values()))]
#         confidence = max(gender_scores.values())

#         return predicted_gender

#     except Exception as e:
#         print(f"Error during prediction: {e}")
#         return None


from deepface import DeepFace
import numpy as np
import cv2

async def gender_predictor(img_bytes):
    try:
        # Decode image
        image = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            return "Unknown"

        # Analyze gender using DeepFace
        result = DeepFace.analyze(
            img_path=image, 
            actions=['gender'], 
            enforce_detection=False
        )

        # Handle both single face and multiple faces results
        if isinstance(result, list):
            result = result[0]

        gender_scores = result['gender']
        
        # Find the gender with highest confidence
        predicted_gender = max(gender_scores, key=gender_scores.get)
        
        return predicted_gender

    except Exception as e:
        print(f"Error during gender prediction: {e}")
        return "Unknown"