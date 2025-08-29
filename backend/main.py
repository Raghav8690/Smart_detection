# from fastapi import FastAPI, HTTPException
# from routers.image_process import router as image_process_router

# app = FastAPI()

# @app.get("/")
# def index():
#     return {"msg": "Welcome to the Supabase Image API"}

# app.include_router(image_process_router, prefix="/process_image")


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.image_process import router as image_process_router

app = FastAPI(
    title="Smart Detection API",
    description="Face detection and recognition API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    return {"msg": "Welcome to the Smart Detection API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Include the image processing router
app.include_router(
    image_process_router, 
    prefix="/api/v1", 
    tags=["Image Processing"]
)