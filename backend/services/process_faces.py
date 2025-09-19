"""

import datetime
from concurrent.futures import ThreadPoolExecutor
from services.face_compare import FaceMatcher
from utils.face_extraction import face_extraction
from db.config import supabase
import numpy as np  
from services.feature_extraction import feature_extraction


face_matcher = FaceMatcher()
face_matcher.load_embeddings_from_db()

def process_faces(image_bytes: bytes):
    results = []

    faces, embeddings = face_extraction(image_bytes)

    if not faces or not embeddings:
        return {"status": "no_faces"}

    for face,embedding in zip(faces,embeddings):
        matched_id = face_matcher.match(embedding)

        now = datetime.datetime.now().isoformat()

        if matched_id:
            session_data = supabase.table("sessions") \
                .select("id, first_seen, last_seen") \
                .eq("visitor_id", matched_id) \
                .order("last_seen", desc=True) \
                .limit(1).execute().data

            if session_data:
                last_seen_str = session_data[0]["last_seen"]
                first_seen_str = session_data[0]["first_seen"]
                session_id = session_data[0]["id"]

                diff_sec = (
                    datetime.datetime.fromisoformat(now) -
                    datetime.datetime.fromisoformat(last_seen_str)
                ).total_seconds()

                if diff_sec <= 15:
                    duration = (
                        datetime.datetime.fromisoformat(now) -
                        datetime.datetime.fromisoformat(first_seen_str)
                    ).total_seconds()

                    supabase.table("sessions").update({
                        "last_seen": now,
                        "duration": int(duration)
                    }).eq("id", session_id).execute()
                else:
                    supabase.table("visitors").update({
                        "visit_count": {"increment": 1}
                    }).eq("id", matched_id).execute()

                    supabase.table("sessions").insert({
                        "visitor_id": matched_id,
                        "first_seen": now,
                        "last_seen": now,
                        "duration": 0
                    }).execute()
            else:
                supabase.table("sessions").insert({
                    "visitor_id": matched_id,
                    "first_seen": now,
                    "last_seen": now,
                    "duration": 0
                }).execute()

            results.append({"visitor_id": matched_id, "status": "matched"})

        else:
            age,gender,race = feature_extraction(face)
            insert_result = supabase.table("visitors").insert({
                "visit_count": 1,
                "gender":gender,
                "age":age,
                "race":race
            }).execute()
            new_id = insert_result.data[0]["id"]


            supabase.table("embeddings").insert({
                "visitor_id": new_id,
                "embeddings": embedding.astype(float).tolist()
            }).execute()

            face_matcher.add_to_index(np.array(embedding, dtype=np.float32), new_id)

            supabase.table("sessions").insert({
                "visitor_id": new_id,
                "first_seen": now,
                "last_seen": now,
                "duration": 0
            }).execute()

            results.append({"visitor_id": new_id, "status": "new"})

    return {"status": "processed", "results": results}


    """

# import datetime
# import asyncio
# from services.face_compare import FaceMatcher
# from utils.face_extraction import face_extraction
# from db.config import supabase
# import numpy as np
# from services.feature_extraction import feature_extraction

# face_matcher = FaceMatcher()
# face_matcher.load_embeddings_from_db()

# def process_faces(image_bytes: bytes):
#     results = []

#     faces, embeddings = face_extraction(image_bytes)

#     if not faces or not embeddings:
#         return {"status": "no_faces"}

#     for face, embedding in zip(faces, embeddings):
#         matched_id = face_matcher.match(embedding)

#         now = datetime.datetime.now().isoformat()

#         if matched_id:
#             session_data = supabase.table("sessions") \
#                 .select("id, first_seen, last_seen") \
#                 .eq("visitor_id", matched_id) \
#                 .order("last_seen", desc=True) \
#                 .limit(1).execute().data

#             if session_data:
#                 last_seen_str = session_data[0]["last_seen"]
#                 first_seen_str = session_data[0]["first_seen"]
#                 session_id = session_data[0]["id"]

#                 diff_sec = (
#                     datetime.datetime.fromisoformat(now) -
#                     datetime.datetime.fromisoformat(last_seen_str)
#                 ).total_seconds()

#                 if diff_sec <= 15:
#                     duration = (
#                         datetime.datetime.fromisoformat(now) -
#                         datetime.datetime.fromisoformat(first_seen_str)
#                     ).total_seconds()

#                     supabase.table("sessions").update({
#                         "last_seen": now,
#                         "duration": int(duration)
#                     }).eq("id", session_id).execute()
#                 else:
#                     visitor_data = supabase.table('visitors').select('visit_count').eq('id', matched_id).execute().data
#                     current_count = visitor_data[0]['visit_count'] if visitor_data else 0

#                     supabase.table("visitors").update({
#                         "visit_count": current_count + 1
#                     }).eq("id", matched_id).execute()

#                     supabase.table("sessions").insert({
#                         "visitor_id": matched_id,
#                         "first_seen": now,
#                         "last_seen": now,
#                         "duration": 0
#                     }).execute()
#             else:
#                 supabase.table("sessions").insert({
#                     "visitor_id": matched_id,
#                     "first_seen": now,
#                     "last_seen": now,
#                     "duration": 0
#                 }).execute()

#             results.append({"visitor_id": matched_id, "status": "matched"})

#         else:
#             # FIX: Run async function synchronously
#             age, gender, race = asyncio.run(feature_extraction(face))

#             insert_result = supabase.table("visitors").insert({
#                 "visit_count": 1,
#                 "gender": gender,
#                 "age": age,
#                 "race": race
#             }).execute()
#             new_id = insert_result.data[0]["id"]

#             supabase.table("embeddings").insert({
#                 "visitor_id": new_id,
#                 "embeddings": embedding.astype(float).tolist()
#             }).execute()

#             face_matcher.add_to_index(np.array(embedding, dtype=np.float32), new_id)

#             supabase.table("sessions").insert({
#                 "visitor_id": new_id,
#                 "first_seen": now,
#                 "last_seen": now,
#                 "duration": 0
#             }).execute()

#             results.append({"visitor_id": new_id, "status": "new"})

#     return {"status": "processed", "results": results}

import datetime
import asyncio
from services.face_compare import FaceMatcher
from utils.face_extraction import face_extraction
from db.config import supabase
import numpy as np
from services.feature_extraction import feature_extraction

# Global face matcher instance
face_matcher = FaceMatcher()


def process_faces(image_bytes: bytes):
    try:
        results = []

        # Extract faces and embeddings
        faces_and_embeddings = face_extraction(image_bytes)
        if not faces_and_embeddings:
            return {"status": "no_faces", "results": []}

        for face_image, embedding in faces_and_embeddings:
            print(f"face_image {type(face_image)}\t embedding {type(embedding)}")
            try:
                # Try to match the face
                matched_id = face_matcher.match(embedding)
                print("match id : ", matched_id)
                now = datetime.datetime.now(datetime.timezone.utc).isoformat()

                if matched_id:
                    # Handle existing visitor
                    session_response = (
                        supabase.table("sessions")
                        .select("id, first_seen, last_seen")
                        .eq("visitor_id", matched_id)
                        .order("last_seen", desc=True)
                        .limit(1)
                        .execute()
                    )

                    if session_response.data:
                        session_data = session_response.data[0]
                        last_seen_str = session_data["last_seen"]
                        first_seen_str = session_data["first_seen"]
                        session_id = session_data["id"]

                        # Calculate time difference
                        diff_sec = (
                            datetime.datetime.fromisoformat(now)
                            - datetime.datetime.fromisoformat(last_seen_str)
                        ).total_seconds()

                        if diff_sec <= 15:
                            # Update existing session
                            duration = (
                                datetime.datetime.fromisoformat(now)
                                - datetime.datetime.fromisoformat(first_seen_str)
                            ).total_seconds()

                            supabase.table("sessions").update(
                                {"last_seen": now, "duration": int(duration)}
                            ).eq("id", session_id).execute()
                        else:
                            # Increment visit count and create new session
                            visitor_response = (
                                supabase.table("visitors")
                                .select("visit_count")
                                .eq("id", matched_id)
                                .execute()
                            )
                            current_count = (
                                visitor_response.data[0]["visit_count"]
                                if visitor_response.data
                                else 0
                            )
                            supabase.table("visitors").update(
                                {"visit_count": current_count + 1}
                            ).eq("id", matched_id).execute()

                            supabase.table("sessions").insert(
                                {
                                    "visitor_id": matched_id,
                                    "first_seen": now,
                                    "last_seen": now,
                                    "duration": 0,
                                }
                            ).execute()
                    else:
                        # No existing session, create new one
                        supabase.table("sessions").insert(
                            {
                                "visitor_id": matched_id,
                                "first_seen": now,
                                "last_seen": now,
                                "duration": 0,
                            }
                        ).execute()

                    results.append({"visitor_id": matched_id, "status": "matched"})

                else:
                    # Handle new visitor
                    try:
                        # Extract features using asyncio
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        age, gender, race = loop.run_until_complete(
                            feature_extraction(face_image)
                        )
                        print(f"age {age}, gender {gender} race {race}")
                        loop.close()
                    except Exception as e:
                        print(f"Error extracting features: {e}")
                        age, gender, race = "Unknown", "Unknown", "Unknown"

                    # Insert new visitor
                    insert_result = (
                        supabase.table("visitors")
                        .insert(
                            {
                                "visit_count": 1,
                                "gender": gender,
                                "age": age,
                                "race": race,
                            }
                        )
                        .execute()
                    )

                    if not insert_result.data:
                        raise Exception("Failed to insert new visitor")

                    new_id = insert_result.data[0]["id"]

                    # Store embedding
                    supabase.table("embeddings").insert(
                        {
                            "visitor_id": new_id,
                            "embeddings": embedding.astype(float).tolist(),
                        }
                    ).execute()

                    # Add to FAISS index
                    face_matcher.add_to_index(
                        np.array(embedding, dtype=np.float32), new_id
                    )

                    # Create initial session
                    supabase.table("sessions").insert(
                        {
                            "visitor_id": new_id,
                            "first_seen": now,
                            "last_seen": now,
                            "duration": 0,
                        }
                    ).execute()

                    results.append({"visitor_id": new_id, "status": "new"})

            except Exception as e:
                print(f"Error processing individual face: {e}")
                results.append({"error": str(e), "status": "error"})

        return {"status": "processed", "results": results}

    except Exception as e:
        print(f"Error in process_faces: {e}")
        return {"status": "error", "error": str(e)}

