# import cv2
# import numpy as np
# import insightface
# from insightface.app import FaceAnalysis


# app = FaceAnalysis(name='buffalo_l')
# app.prepare(ctx_id=0, det_size=(640, 640)) 

# async def face_extraction(img_bytes: bytes):
#     try:
#         img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
#         if img is None:
#             print("Failed to decode image")
#             return []
            
#         faces = app.get(img)
#         results = []
        
#         for face in faces:
#             box = face.bbox.astype(int)
#             cropped_face = img[box[1]:box[3], box[0]:box[2]]
#             embedding = face.embedding
#             results.append((cropped_face, embedding))
#         return results
#     except Exception as e:
#         print(f"Error in face extraction: {e}")
#         return []

import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis

# Global app instance to avoid reinitializing
app = None

def get_face_app():
    global app
    if app is None:
        try:
            app = FaceAnalysis(name='buffalo_l')
            app.prepare(ctx_id=0, det_size=(640, 640))
        except Exception as e:
            print(f"Error initializing face analysis: {e}")
            return None
    return app

def face_extraction(img_bytes: bytes):
    try:
        # Get face analysis app
        face_app = get_face_app()
        if face_app is None:
            print("Face analysis app not available")
            return []

        # Decode image
        img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            print("Failed to decode image")
            return []
        print(f"Image decoded successfully. Shape: {img.shape}, Dtype: {img.dtype}")

        # Get faces
        faces = face_app.get(img)
        print(f"Number of faces detected: {len(faces)}")
        results = []

        for idx, face in enumerate(faces):
            try:
                # Extract bounding box and crop face
                box = face.bbox.astype(int)
                # Ensure coordinates are within image bounds
                box[0] = max(0, box[0])
                box[1] = max(0, box[1])
                box[2] = min(img.shape[1], box[2])
                box[3] = min(img.shape[0], box[3])

                cropped_face = img[box[1]:box[3], box[0]:box[2]]
                resized_face = []
                for i in cropped_face:
                    resized_face = resized_face.append(cv2.resize(cropped_face, (224, 224), interpolation=cv2.INTER_LANCZOS4))

                if resized_face.size == 0:
                    print(f"Face {idx}: Cropped face is empty, skipping.")
                    continue

                embedding = face.embedding
                print(f"Face {idx}: Cropped face shape: {resized_face.shape}, Embedding shape: {embedding.shape}")
                results.append((resized_face, embedding))
            except Exception as e:
                print(f"Error processing individual face {idx}: {e}")
                continue

        print(f"Total faces processed and returned: {len(results)}")
        return results
    except Exception as e:
        print(f"Error in face extraction: {e}")
        return []