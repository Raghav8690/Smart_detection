# from utils.gender import gender_predictor
# from utils.age import predict_age
# from utils.race import race_predictor
# from fastapi import HTTPException

# async def feature_extraction(face: bytes):
#     try:
#         if face:
#             age =  await predict_age(face)
#             gender =  await gender_predictor(face)
#             race =  await race_predictor(face)
#         else:
#             raise HTTPException(status_code=400, detail="No face data provided")
#         return age,gender,race
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error during feature extraction: {e}")


from utils.gender import gender_predictor
from utils.age import predict_age
from utils.race import race_predictor
from fastapi import HTTPException
import cv2
import numpy as np

async def feature_extraction(face_image):
    try:
        if face_image is None or face_image.size == 0:
            raise HTTPException(status_code=400, detail="No face data provided")
        
        # Convert face image to bytes for the utility functions
        success, encoded_image = cv2.imencode('.jpg', face_image)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to encode face image")
        
        face_bytes = encoded_image.tobytes()
        
        # Extract features
        age = await predict_age(face_bytes)
        gender = await gender_predictor(face_bytes)
        race = await race_predictor(face_bytes)
        
        return age, gender, race
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during feature extraction: {e}")