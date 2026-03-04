"""
Utility functions for embeddings and vector operations
"""
import numpy as np
from typing import List, Dict, Any
import openai
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing embeddings"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.EMBEDDING_MODEL
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = openai.Embedding.create(
                input=text,
                model=self.model
            )
            return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            response = openai.Embedding.create(
                input=texts,
                model=self.model
            )
            # Sort by index to maintain order
            embeddings = sorted(response['data'], key=lambda x: x['index'])
            return [item['embedding'] for item in embeddings]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score (-1 to 1)
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        magnitude1 = np.linalg.norm(vec1)
        magnitude2 = np.linalg.norm(vec2)
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return float(dot_product / (magnitude1 * magnitude2))
    
    def similarity_batch(self, query_vec: List[float], vectors: List[List[float]]) -> List[float]:
        """
        Calculate similarity between query vector and multiple vectors
        
        Args:
            query_vec: Query vector
            vectors: List of vectors to compare
            
        Returns:
            List of similarity scores
        """
        query_vec = np.array(query_vec)
        vectors = np.array(vectors)
        
        dot_products = np.dot(vectors, query_vec)
        magnitudes = np.linalg.norm(vectors, axis=1)
        query_magnitude = np.linalg.norm(query_vec)
        
        if query_magnitude == 0:
            return [0.0] * len(vectors)
        
        similarities = dot_products / (magnitudes * query_magnitude + 1e-8)
        return [float(s) for s in similarities]


embedding_service = EmbeddingService()
