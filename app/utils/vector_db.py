"""
Vector database utilities for FAISS and Pinecone
"""
import os
import pickle
import json
from typing import List, Dict, Tuple, Optional
import logging
import numpy as np
from app.config import settings

logger = logging.getLogger(__name__)


class FAISSVectorDB:
    """FAISS Vector Database implementation"""
    
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self.index = None
        self.metadata = {}
        self.index_path = settings.FAISS_INDEX_PATH
        self.metadata_path = settings.FAISS_INDEX_PATH.replace('.pkl', '_metadata.json')
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create new one"""
        try:
            if os.path.exists(self.index_path):
                with open(self.index_path, 'rb') as f:
                    self.index = pickle.load(f)
                if os.path.exists(self.metadata_path):
                    with open(self.metadata_path, 'r') as f:
                        self.metadata = json.load(f)
                logger.info("Loaded existing FAISS index")
            else:
                import faiss
                self.index = faiss.IndexFlatL2(self.dimension)
                os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
                logger.info("Created new FAISS index")
        except Exception as e:
            logger.error(f"Error loading/creating index: {e}")
            raise
    
    def add_vectors(self, vectors: List[List[float]], ids: List[str], metadata: List[Dict] = None):
        """Add vectors to index"""
        try:
            import faiss
            vectors_array = np.array(vectors).astype('float32')
            self.index.add(vectors_array)
            
            if metadata:
                for i, (id_, meta) in enumerate(zip(ids, metadata)):
                    self.metadata[str(len(self.metadata))] = {
                        'id': id_,
                        'metadata': meta
                    }
            else:
                for id_ in ids:
                    self.metadata[str(len(self.metadata))] = {'id': id_}
            
            self.save()
        except Exception as e:
            logger.error(f"Error adding vectors: {e}")
            raise
    
    def search(self, vector: List[float], k: int = 10) -> List[Tuple[str, float]]:
        """Search for similar vectors"""
        try:
            vector_array = np.array([vector]).astype('float32')
            distances, indices = self.index.search(vector_array, min(k, len(self.metadata)))
            
            results = []
            for dist, idx in zip(distances[0], indices):
                if idx >= 0 and str(idx) in self.metadata:
                    item = self.metadata[str(idx)]
                    similarity = 1 / (1 + float(dist))  # Convert distance to similarity
                    results.append((item['id'], similarity))
            
            return results
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    def save(self):
        """Save index and metadata to disk"""
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            with open(self.index_path, 'wb') as f:
                pickle.dump(self.index, f)
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f)
            logger.info("Saved FAISS index")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            raise


class PineconeVectorDB:
    """Pinecone Vector Database implementation"""
    
    def __init__(self):
        try:
            import pinecone
            self.pinecone = pinecone
            pinecone.init(
                api_key=settings.PINECONE_API_KEY,
                environment=settings.PINECONE_ENVIRONMENT
            )
            self.index_name = settings.PINECONE_INDEX_NAME
            self.index = pinecone.Index(self.index_name)
        except Exception as e:
            logger.error(f"Error initializing Pinecone: {e}")
            raise
    
    def add_vectors(self, vectors: List[List[float]], ids: List[str], metadata: List[Dict] = None):
        """Add vectors to Pinecone index"""
        try:
            vectors_to_upsert = []
            for i, (id_, vector) in enumerate(zip(ids, vectors)):
                meta = metadata[i] if metadata else {}
                vectors_to_upsert.append((id_, vector, meta))
            
            self.index.upsert(vectors=vectors_to_upsert, batch_size=100)
            logger.info(f"Added {len(ids)} vectors to Pinecone")
        except Exception as e:
            logger.error(f"Error adding vectors to Pinecone: {e}")
            raise
    
    def search(self, vector: List[float], k: int = 10) -> List[Tuple[str, float]]:
        """Search for similar vectors in Pinecone"""
        try:
            results = self.index.query(vector=vector, top_k=k, include_metadata=True)
            
            matches = []
            for match in results.get('matches', []):
                matches.append((match['id'], match.get('score', 0.0)))
            
            return matches
        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            return []


def get_vector_db():
    """Factory function to get appropriate vector database instance"""
    if settings.VECTOR_DB_TYPE.lower() == "pinecone":
        return PineconeVectorDB()
    else:
        return FAISSVectorDB()


vector_db = get_vector_db()
