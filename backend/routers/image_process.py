from fastapi import APIRouter, HTTPException , BackgroundTasks,UploadFile,File
from services.face_compare import FaceMatcher
from services.face_extraction import face_extraction
from services.age import predict_age
from services.gender import gender_predictor
from services.race import race_predictor
from db.config import supabase
import datetime

router = APIRouter()

async def feature_extraction(image_byte):
    try:
        faces,embeddings = await face_extraction(image_byte)
        if not faces:
            raise HTTPException(status_code=400, detail="No faces detected in the image")
        return faces
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during face extraction: {e}")

@router.post("/process_image")
async def upload_image(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    image_byte = await file.read()
    if not image_byte:
        raise HTTPException(status_code=400, detail="No image data provided")
    try:
        faces , embeddings = await face_extraction(image_byte)
        if not faces:
            raise HTTPException(status_code=400, detail="No faces detected in the image")
        face_matcher = FaceMatcher()
        face_matcher.load_embeddings_from_db()
        results = []
        for face, embedding in zip(faces, embeddings):
            matched_id = face_matcher.match(embedding)
            if matched_id:
                response = supabase.table('Visitors').select('visit_count').eq('id', matched_id).execute().data
                current_count = response[0]['visit_count']
                supabase.table("Visitors").update(
                    {'visit_count' : current_count+1}
                ).eq("id", matched_id).execute()

                response = supabase.table('Visitors').select('first_seen, last_seen').eq('id', matched_id).execute()
                first_seen,last_seen = response.data[0]["first_seens"], response.data[0]["last_seen"]

                duration = last_seen-first_seen

                supabase.table("Sessions").update(
                    {"last_seen": datetime.datetime.now().isoformat()
                     "duration": duration}
                )

                supabase.table("Sessions").insert(
                    {
                        'visitor_id':matched_id
                    }
                )


    except Exception as e:
        pass

    