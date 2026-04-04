"""
Vector store module for storing and retrieving movie embeddings.
Uses FAISS for efficient similarity search.
"""
import os
import pickle
import numpy as np
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
import faiss


class VectorStore:
    """Manages movie embeddings and similarity search using FAISS."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", vector_store_path: str = None):
        """
        Initialize the vector store.
        
        Args:
            model_name: Name of the SentenceTransformer model
            vector_store_path: Path to save/load the vector store
        """
        self.model_name = model_name
        self.vector_store_path = vector_store_path or "vector_store/faiss_index"
        self.embedding_model = None
        self.index = None
        self.documents = []
        self.dimension = 384  # Default for all-MiniLM-L6-v2
        
    def initialize_model(self):
        """Initialize the embedding model."""
        print(f"Loading embedding model: {self.model_name}")
        self.embedding_model = SentenceTransformer(self.model_name)
        # Get actual dimension from model
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        print(f"Model dimension: {self.dimension}")
    
    def create_embeddings(self, documents: List[Dict[str, Any]]) -> np.ndarray:
        """
        Create embeddings for all documents.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            Numpy array of embeddings
        """
        if self.embedding_model is None:
            self.initialize_model()
        
        texts = [doc['text'] for doc in documents]
        print(f"Creating embeddings for {len(texts)} documents...")
        
        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        print(f"Created embeddings of shape: {embeddings.shape}")
        return embeddings
    
    def build_index(self, documents: List[Dict[str, Any]], embeddings: np.ndarray):
        """
        Build FAISS index from embeddings.
        
        Args:
            documents: List of document dictionaries
            embeddings: Numpy array of embeddings
        """
        self.documents = documents
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Create FAISS index (using inner product for normalized vectors = cosine similarity)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings.astype('float32'))
        
        print(f"Built FAISS index with {self.index.ntotal} vectors")
    
    def save_index(self):
        """Save the FAISS index and documents to disk."""
        os.makedirs(os.path.dirname(self.vector_store_path), exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, f"{self.vector_store_path}.index")
        
        # Save documents
        with open(f"{self.vector_store_path}.pkl", 'wb') as f:
            pickle.dump(self.documents, f)
        
        print(f"Saved vector store to {self.vector_store_path}")
    
    def load_index(self) -> bool:
        """
        Load the FAISS index and documents from disk.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        index_path = f"{self.vector_store_path}.index"
        docs_path = f"{self.vector_store_path}.pkl"
        
        if not os.path.exists(index_path) or not os.path.exists(docs_path):
            return False
        
        try:
            self.index = faiss.read_index(index_path)
            with open(docs_path, 'rb') as f:
                self.documents = pickle.load(f)
            
            # Initialize model for query encoding
            if self.embedding_model is None:
                self.initialize_model()
            
            print(f"Loaded vector store with {self.index.ntotal} vectors")
            return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False
    
    def search(self, query: str, k: int = 10) -> List[Tuple[Dict[str, Any], float]]:
        """
        Search for similar movies given a query.
        
        Args:
            query: User query string
            k: Number of results to return
            
        Returns:
            List of tuples (document, similarity_score)
        """
        if self.index is None or self.embedding_model is None:
            raise ValueError("Vector store not initialized. Call build_index() or load_index() first.")
        
        # Encode query
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        # Search
        k = min(k, self.index.ntotal)
        similarities, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Return results with documents
        results = []
        for idx, score in zip(indices[0], similarities[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(score)))
        
        return results
