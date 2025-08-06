from fastapi import FastAPI, HTTPException
from routers.image_process import router as image_process_router

app = FastAPI()

@app.get("/")
def index():
    return {"msg": "Welcome to the Supabase Image API"}

app.include_router(image_process_router, prefix="/process_image")