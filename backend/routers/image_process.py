'''

from fastapi import APIRouter, HTTPException , BackgroundTasks,UploadFile,File
import asyncio
from services.process_faces import process_faces
from concurrent.futures import ThreadPoolExecutor



router = APIRouter()
executor = ThreadPoolExecutor(max_workers=4)


@router.post("/")
async def process_image(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="No image provided")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, process_faces, image_bytes)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

'''

# @router.post("/")
# async def process_image(file: UploadFile = File(...)):
#     try:
#         image_bytes = await file.read()
#         if not image_bytes:
#             raise HTTPException(status_code=400, detail="No image provided")

#         loop = asyncio.get_event_loop()
#         result = await loop.run_in_executor(executor, process_faces, image_bytes)
#         return result

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))







# async def feature_extraction(image_byte):
#     try:
#         faces,embeddings = await face_extraction(image_byte)
#         if not faces:
#             raise HTTPException(status_code=400, detail="No faces detected in the image")
#         return faces
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error during face extraction: {e}")

# @router.post("/process_image")
# async def upload_image(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
#     image_byte = await file.read()
#     if not image_byte:
#         raise HTTPException(status_code=400, detail="No image data provided")
#     try:
#         faces , embeddings = await face_extraction(image_byte)
#         if not faces:
#             raise HTTPException(status_code=400, detail="No faces detected in the image")
#         face_matcher = FaceMatcher()
#         face_matcher.load_embeddings_from_db()
#         for face, embedding in zip(faces, embeddings):
#             matched_id = face_matcher.match(embedding)
#             if matched_id:
#                 response = supabase.table('Visitors').select('visit_count').eq('id', matched_id).execute().data
#                 current_count = response[0]['visit_count']
#                 supabase.table("Visitors").update(
#                     {'visit_count' : current_count+1}
#                 ).eq("id", matched_id).execute()

#                 response = supabase.table('Visitors').select('first_seen, last_seen').eq('id', matched_id).execute()
#                 first_seen,last_seen = response.data[0]["first_seens"], response.data[0]["last_seen"]

#                 duration = last_seen-first_seen

#                 supabase.table("Sessions").update(
#                     {"last_seen": datetime.datetime.now().isoformat()
#                      "duration": duration}
#                 )

#                 supabase.table("Sessions").insert(
#                     {
#                         'visitor_id':matched_id
#                     }
#                 )


#     except Exception as e:
#         pass

    



    # ------------------ New ---------------------------

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
import asyncio
from services.process_faces import process_faces
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=4)

@router.post("/")
async def process_image(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="No image provided")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, process_faces, image_bytes)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))