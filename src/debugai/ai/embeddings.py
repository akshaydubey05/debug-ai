"""
Embeddings - Text embeddings for semantic search

Uses sentence-transformers for local embeddings or Gemini for cloud embeddings.
"""

from typing import List, Optional
import numpy as np


class EmbeddingModel:
    """
    Manages text embeddings for semantic similarity search.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", use_local: bool = True):
        """
        Initialize embedding model.
        
        Args:
            model_name: Model to use for embeddings
            use_local: Use local model (sentence-transformers) vs cloud
        """
        self.model_name = model_name
        self.use_local = use_local
        self._model = None
        self._dimension = 384  # Default for MiniLM
    
    def _load_model(self):
        """Load the embedding model."""
        if self._model is None:
            if self.use_local:
                try:
                    from sentence_transformers import SentenceTransformer
                    self._model = SentenceTransformer(self.model_name)
                    self._dimension = self._model.get_sentence_embedding_dimension()
                except ImportError:
                    raise ImportError(
                        "sentence-transformers not installed. "
                        "Run: pip install sentence-transformers"
                    )
            else:
                # Use Gemini embeddings
                self._model = "gemini"
        return self._model
    
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector as list of floats
        """
        model = self._load_model()
        
        if self.use_local:
            embedding = model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        else:
            return self._embed_with_gemini(text)
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        """
        model = self._load_model()
        
        if self.use_local:
            embeddings = model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        else:
            return [self._embed_with_gemini(text) for text in texts]
    
    def _embed_with_gemini(self, text: str) -> List[float]:
        """Generate embedding using Gemini."""
        import google.generativeai as genai
        import os
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        
        genai.configure(api_key=api_key)
        
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        
        return result["embedding"]
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
        
        Returns:
            Similarity score (0-1)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def find_similar(
        self,
        query_embedding: List[float],
        embeddings: List[List[float]],
        top_k: int = 5
    ) -> List[tuple]:
        """
        Find most similar embeddings to query.
        
        Args:
            query_embedding: Query embedding
            embeddings: List of embeddings to search
            top_k: Number of results to return
        
        Returns:
            List of (index, similarity_score) tuples
        """
        similarities = []
        
        for i, emb in enumerate(embeddings):
            sim = self.similarity(query_embedding, emb)
            similarities.append((i, sim))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        self._load_model()
        return self._dimension
