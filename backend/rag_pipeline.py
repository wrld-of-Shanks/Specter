from typing import List, Dict, Any, Optional
import re
from collections import defaultdict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Initialize sentence transformer model for semantic search
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

class LegalRAGPipeline:
    def __init__(self):
        self.embedding_model = EMBEDDING_MODEL
        self.context_window = 3000  # Max tokens for context
        
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into smaller chunks for better embedding"""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a given text"""
        return self.embedding_model.encode(text, convert_to_tensor=False)
    
    def _calculate_similarity(self, query_embedding: np.ndarray, context_embeddings: List[np.ndarray]) -> List[float]:
        """Calculate cosine similarity between query and context embeddings"""
        if not context_embeddings:
            return []
        return cosine_similarity(
            query_embedding.reshape(1, -1),
            np.array(context_embeddings)
        )[0]
    
    def _retrieve_relevant_context(self, query: str, context_data: Dict[str, str], top_k: int = 3) -> List[str]:
        """Retrieve most relevant context for the query"""
        # Generate query embedding
        query_embedding = self._get_embedding(query)
        
        # Prepare context chunks with embeddings
        context_chunks = []
        for key, text in context_data.items():
            chunks = self._chunk_text(text)
            for chunk in chunks:
                context_chunks.append({
                    'key': key,
                    'text': chunk,
                    'embedding': self._get_embedding(chunk)
                })
        
        # Calculate similarities
        context_embeddings = [c['embedding'] for c in context_chunks]
        similarities = self._calculate_similarity(query_embedding, context_embeddings)
        
        # Sort by similarity and get top-k
        sorted_indices = np.argsort(similarities)[::-1][:top_k]
        return [context_chunks[i]['text'] for i in sorted_indices]
    
    def build_prompt(
        self,
        query: str,
        context_data: Dict[str, str],
        chat_history: Optional[List[Dict[str, str]]] = None,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Build an enhanced RAG prompt with relevant context
        
        Args:
            query: User's query
            context_data: Dictionary of legal context data
            chat_history: List of previous messages in the conversation
            include_sources: Whether to include source information
            
        Returns:
            Dictionary containing the prompt and metadata
        """
        # Retrieve relevant context
        relevant_contexts = self._retrieve_relevant_context(query, context_data)
        
        # Build system message
        system_prompt = """You are SPECTER, an AI legal assistant specialized in Indian law. 
        Provide accurate, clear, and concise legal information based on the provided context. 
        If you're unsure about any information, clearly state that."""
        
        # Format context
        context_str = "\n\n".join([f"Context {i+1}: {ctx}" for i, ctx in enumerate(relevant_contexts)])
        
        # Build user message with context
        user_message = f"""Legal Query: {query}
        
        Relevant Legal Context:
        {context_str}
        
        Please provide a comprehensive and accurate response based on the above context and your knowledge of Indian law.
        """
        
        # Build messages list
        messages = [
            {"role": "system", "content": system_prompt},
            *([] if not chat_history else chat_history),
            {"role": "user", "content": user_message}
        ]
        
        # Prepare metadata
        metadata = {
            "context_sources": list(context_data.keys())[:3] if include_sources else [],
            "context_count": len(relevant_contexts),
            "query_terms": query.lower().split(),
            "system_prompt": system_prompt
        }
        
        return {
            "messages": messages,
            "metadata": metadata
        }
    
    def post_process_response(
        self,
        response: str,
        metadata: Dict[str, Any],
        include_sources: bool = True
    ) -> str:
        """Post-process the model response"""
        if not include_sources or not metadata.get('context_sources'):
            return response
            
        sources = ", ".join(metadata['context_sources'])
        return f"""{response}
        
        Sources: {sources}
        """.strip()

# Singleton instance
rag_pipeline = LegalRAGPipeline()

def build_prompt_for_query(query: str, context: dict) -> dict:
    """Legacy function for backward compatibility"""
    return rag_pipeline.build_prompt(query, context)
