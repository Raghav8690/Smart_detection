"""

import numpy as np
import faiss
from db.config import supabase


class FaceMatcher:
    def __init__(self, dim: int = 512, threshold: float = 0.6):
        self.dim = dim
        self.threshold = threshold
        self.index = faiss.IndexFlatIP(dim)
        self.visitor_ids = []

    def load_embeddings_from_db(self):
        try:
            print(" Loading embeddings from Supabase...")
            rows = supabase.table('embeddings').select('visitor_id, embeddings').execute().data

            if not rows:
                print(" No embeddings found in Supabase.")
                return

            embedding_vectors = np.array(
                [row['vector'] for row in rows], dtype=np.float32
            )
            faiss.normalize_L2(embedding_vectors)

            self.index.add(embedding_vectors)
            self.visitor_ids = [row['visitor_id'] for row in rows]

            print(f" Loaded {len(self.visitor_ids)} embeddings into FAISS.")
        except Exception as e:
            print(f" Error loading embeddings: {e}")

    def match(self, new_vector: np.ndarray):
        try:
            if self.index.ntotal == 0:
                print(" FAISS index is empty. Cannot match.")
                return None

            vector = np.array([new_vector], dtype=np.float32)
            faiss.normalize_L2(vector)
            D, I = self.index.search(vector, k=1)

            similarity = D[0][0]
            index_id = I[0][0]

            if similarity > self.threshold:
                return self.visitor_ids[index_id]
            return None
        except Exception as e:
            print(f" Error during face matching: {e}")
            return None

    def add_to_index(self, new_vector: np.ndarray, visitor_id: str):
        try:
            vector = np.array([new_vector], dtype=np.float32)
            faiss.normalize_L2(vector)
            self.index.add(vector)
            self.visitor_ids.append(visitor_id)
            print(f" Added visitor {visitor_id} to FAISS index.")
        except Exception as e:
            print(f" Error adding new embedding to FAISS: {e}")







# async def cosine_similarity(emb1, emb2):
#     return dot(emb1, emb2) / (norm(emb1) * norm(emb2))

# async def face_compare(emb1, emb2):
#     similarity = await cosine_similarity(emb1, emb2)
#     return similarity > threshold


"""


import numpy as np
import faiss
from db.config import supabase


class FaceMatcher:
    def __init__(self, dim: int = 512, threshold: float = 0.6):
        self.dim = dim
        self.threshold = threshold
        self.index = faiss.IndexFlatIP(dim)
        self.visitor_ids = []

    def load_embeddings_from_db(self):
        try:
            print(" Loading embeddings from Supabase...")
            rows = supabase.table('embeddings').select('visitor_id, embeddings').execute().data

            if not rows:
                print(" No embeddings found in Supabase.")
                return

            # Fixed: changed 'vector' to 'embeddings' to match the selected column
            embedding_vectors = np.array(
                [row['embeddings'] for row in rows], dtype=np.float32
            )
            faiss.normalize_L2(embedding_vectors)

            self.index.add(embedding_vectors)
            self.visitor_ids = [row['visitor_id'] for row in rows]

            print(f" Loaded {len(self.visitor_ids)} embeddings into FAISS.")
        except Exception as e:
            print(f" Error loading embeddings: {e}")

    def match(self, new_vector: np.ndarray):
        try:
            if self.index.ntotal == 0:
                print(" FAISS index is empty. Cannot match.")
                return None

            vector = np.array([new_vector], dtype=np.float32)
            faiss.normalize_L2(vector)
            D, I = self.index.search(vector, k=1)

            similarity = D[0][0]
            index_id = I[0][0]

            if similarity > self.threshold:
                return self.visitor_ids[index_id]
            return None
        except Exception as e:
            print(f" Error during face matching: {e}")
            return None

    def add_to_index(self, new_vector: np.ndarray, visitor_id: str):
        try:
            vector = np.array([new_vector], dtype=np.float32)
            faiss.normalize_L2(vector)
            self.index.add(vector)
            self.visitor_ids.append(visitor_id)
            print(f" Added visitor {visitor_id} to FAISS index.")
        except Exception as e:
            print(f" Error adding new embedding to FAISS: {e}")