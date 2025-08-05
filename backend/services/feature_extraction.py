from utils.gender import gender_predictor
from utils.age import predict_age
from utils.race import race_predictor
from fastapi import HTTPException

async def feature_extraction(face: bytes):
    try:
        if face:
            age =  await predict_age(face)
            gender =  await gender_predictor(face)
            race =  await race_predictor(face)
        else:
            raise HTTPException(status_code=400, detail="No face data provided")
        return age,gender,race
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during feature extraction: {e}")