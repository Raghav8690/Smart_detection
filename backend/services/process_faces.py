'''

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
            session_data = supabase.table("Sessions") \
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

                    supabase.table("Sessions").update({
                        "last_seen": now,
                        "duration": int(duration)
                    }).eq("id", session_id).execute()
                else:
                    supabase.table("Visitors").update({
                        "visit_count": {"increment": 1}
                    }).eq("id", matched_id).execute()

                    supabase.table("Sessions").insert({
                        "visitor_id": matched_id,
                        "first_seen": now,
                        "last_seen": now,
                        "duration": 0
                    }).execute()
            else:
                supabase.table("Sessions").insert({
                    "visitor_id": matched_id,
                    "first_seen": now,
                    "last_seen": now,
                    "duration": 0
                }).execute()

            results.append({"visitor_id": matched_id, "status": "matched"})

        else:
            age,gender,race = feature_extraction(face)
            insert_result = supabase.table("Visitors").insert({
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

            supabase.table("Sessions").insert({
                "visitor_id": new_id,
                "first_seen": now,
                "last_seen": now,
                "duration": 0
            }).execute()

            results.append({"visitor_id": new_id, "status": "new"})

    return {"status": "processed", "results": results}


    '''

import datetime
import asyncio
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

    for face, embedding in zip(faces, embeddings):
        matched_id = face_matcher.match(embedding)

        now = datetime.datetime.now().isoformat()

        if matched_id:
            session_data = supabase.table("Sessions") \
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

                    supabase.table("Sessions").update({
                        "last_seen": now,
                        "duration": int(duration)
                    }).eq("id", session_id).execute()
                else:
                    visitor_data = supabase.table('Visitors').select('visit_count').eq('id', matched_id).execute().data
                    current_count = visitor_data[0]['visit_count'] if visitor_data else 0
                    
                    supabase.table("Visitors").update({
                        "visit_count": current_count + 1
                    }).eq("id", matched_id).execute()

                    supabase.table("Sessions").insert({
                        "visitor_id": matched_id,
                        "first_seen": now,
                        "last_seen": now,
                        "duration": 0
                    }).execute()
            else:
                supabase.table("Sessions").insert({
                    "visitor_id": matched_id,
                    "first_seen": now,
                    "last_seen": now,
                    "duration": 0
                }).execute()

            results.append({"visitor_id": matched_id, "status": "matched"})

        else:
            # FIX: Run async function synchronously
            age, gender, race = asyncio.run(feature_extraction(face))

            insert_result = supabase.table("Visitors").insert({
                "visit_count": 1,
                "gender": gender,
                "age": age,
                "race": race
            }).execute()
            new_id = insert_result.data[0]["id"]

            supabase.table("embeddings").insert({
                "visitor_id": new_id,
                "embeddings": embedding.astype(float).tolist()
            }).execute()

            face_matcher.add_to_index(np.array(embedding, dtype=np.float32), new_id)

            supabase.table("Sessions").insert({
                "visitor_id": new_id,
                "first_seen": now,
                "last_seen": now,
                "duration": 0
            }).execute()

            results.append({"visitor_id": new_id, "status": "new"})

    return {"status": "processed", "results": results}