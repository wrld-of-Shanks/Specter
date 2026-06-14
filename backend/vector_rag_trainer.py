"""
Production-Grade Vector RAG System for Indian Law FAQ Bot
Uses sentence transformers and ChromaDB for semantic search
"""

import json
import logging
import re
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer, util
import chromadb
import numpy as np
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorRAGTrainer:
    """Production-grade RAG system with vector embeddings"""
    
    def __init__(self, model_name="all-MiniLM-L6-v2", similarity_threshold=0.65):
        """
        Initialize the RAG system
        
        Args:
            model_name: Sentence transformer model name (default: all-MiniLM-L6-v2 for memory efficiency)
            similarity_threshold: Minimum similarity score for accepting answers
        """
        logger.info(f"Initializing Vector RAG with model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold
        
        # Initialize ChromaDB with new API
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="indian_law_faq",
            metadata={"description": "Indian Law FAQ with vector embeddings"}
        )
        
        # Auto-train if empty
        if self.collection.count() == 0:
            logger.info("Collection is empty. Starting auto-training...")
            try:
                dataset = self.build_dataset()
                self.train(dataset)
            except Exception as e:
                logger.error(f"Failed to auto-train: {e}")
        
        logger.info(f"ChromaDB collection initialized with {self.collection.count()} documents")
    
    def parse_faq_file(self, file_path: str) -> List[Dict]:
        """Parse FAQ text file into structured data"""
        logger.info(f"Parsing FAQ file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by Q: and A: patterns
        qa_pairs = []
        lines = content.split('\n')
        
        current_question = None
        current_answer = []
        current_category = "General"
        
        for line in lines:
            line = line.strip()
            
            # Detect category headers
            if line.isupper() and len(line) > 5 and not line.startswith('Q:') and not line.startswith('A:'):
                if '(' not in line and ')' not in line:
                    current_category = line.replace('=', '').strip()
                    continue
            
            # Detect questions
            if line.startswith('Q:'):
                # Save previous Q&A pair
                if current_question and current_answer:
                    qa_pairs.append({
                        'question': current_question,
                        'answer': ' '.join(current_answer).strip(),
                        'category': current_category
                    })
                
                # Start new question
                current_question = line[2:].strip()
                current_answer = []
            
            # Detect answers
            elif line.startswith('A:'):
                current_answer.append(line[2:].strip())
            
            # Continue answer
            elif current_answer and line and not line.startswith('Q:'):
                current_answer.append(line)
        
        # Add last Q&A pair
        if current_question and current_answer:
            qa_pairs.append({
                'question': current_question,
                'answer': ' '.join(current_answer).strip(),
                'category': current_category
            })
        
        logger.info(f"Parsed {len(qa_pairs)} Q&A pairs from {file_path}")
        return qa_pairs
    
    def add_comprehensive_legal_db(self):
        """Add comprehensive legal database to FAQ dataset"""
        from comprehensive_legal_db import COMPREHENSIVE_LEGAL_FAQ, get_comprehensive_legal_info
        
        qa_pairs = []
        
        # 1. Add main topics
        for key, answer in COMPREHENSIVE_LEGAL_FAQ.items():
            # Generate question from key
            question = key.replace('_', ' ').title()
            
            # Add variations
            variations = [
                f"What is {question}?",
                f"Tell me about {question}",
                f"Explain {question}",
                f"How to {question}",
                question
            ]
            
            for var in variations:
                qa_pairs.append({
                    'question': var,
                    'answer': answer,
                    'category': 'Comprehensive Legal Database'
                })

        # 2. Add keyword mappings (Crucial for abbreviations like DL, FIR)
        # We manually define common mappings here to ensure they are captured
        abbreviations = {
            "dl": "driving_license",
            "driving licence": "driving_license",
            "fir": "fir_filing",
            "first information report": "fir_filing",
            "pil": "public_interest_litigation",
            "rti": "rti_filing",
            "pf": "provident_fund",
            "gst": "gst_registration",
            "posh": "posh_act",
            "ipc": "indian_penal_code",
            "crpc": "criminal_procedure_code"
        }
        
        for abbr, target_key in abbreviations.items():
            if target_key in COMPREHENSIVE_LEGAL_FAQ:
                answer = COMPREHENSIVE_LEGAL_FAQ[target_key]
                
                # Add specific queries for these abbreviations
                abbr_variations = [
                    f"What is {abbr.upper()}?",
                    f"How to apply {abbr.upper()}",
                    f"How to get {abbr.upper()}",
                    f"{abbr.upper()} application",
                    f"{abbr.upper()} procedure",
                    abbr.upper()
                ]
                
                for var in abbr_variations:
                    qa_pairs.append({
                        'question': var,
                        'answer': answer,
                        'category': 'Legal Abbreviations'
                    })
        
        logger.info(f"Added {len(qa_pairs)} Q&A pairs from comprehensive legal database (including abbreviations)")
        return qa_pairs
    
    def build_dataset(self) -> List[Dict]:
        """Build comprehensive FAQ dataset from all sources"""
        dataset = []
        
        # Add from FAQ file
        faq_file = Path("../data/raw_laws/comprehensive_legal_faq.txt")
        if faq_file.exists():
            dataset.extend(self.parse_faq_file(str(faq_file)))
        
        # Add from comprehensive legal database
        dataset.extend(self.add_comprehensive_legal_db())
        
        # Remove duplicates
        seen = set()
        unique_dataset = []
        for item in dataset:
            key = (item['question'].lower(), item['answer'][:100])
            if key not in seen:
                seen.add(key)
                unique_dataset.append(item)
        
        logger.info(f"Built dataset with {len(unique_dataset)} unique Q&A pairs")
        return unique_dataset
    
    def train(self, dataset: List[Dict]):
        """Train the RAG system by adding FAQ pairs to vector database"""
        logger.info(f"Training RAG system with {len(dataset)} Q&A pairs...")
        
        # Clear existing collection
        try:
            self.client.delete_collection("indian_law_faq")
            self.collection = self.client.get_or_create_collection(
                name="indian_law_faq",
                metadata={"description": "Indian Law FAQ with vector embeddings"}
            )
        except:
            pass
        
        # Batch processing for efficiency
        batch_size = 100
        for i in range(0, len(dataset), batch_size):
            batch = dataset[i:i+batch_size]
            
            # Generate embeddings
            questions = [item['question'] for item in batch]
            embeddings = self.model.encode(questions, show_progress_bar=True)
            
            # Add to ChromaDB
            ids = [f"faq_{i+j}" for j in range(len(batch))]
            metadatas = [
                {
                    'question': item['question'],
                    'answer': item['answer'],
                    'category': item.get('category', 'General')
                }
                for item in batch
            ]
            
            self.collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                metadatas=metadatas
            )
            
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(dataset)-1)//batch_size + 1}")
        
        logger.info(f"✅ Training complete! Total documents in database: {self.collection.count()}")
    
    def get_answer(self, user_query: str, top_k: int = 3) -> Dict:
        """
        Get answer for user query using vector similarity search
        
        Args:
            user_query: User's question
            top_k: Number of similar questions to retrieve
            
        Returns:
            Dict with answer, similarity score, and sources
        """
        # Generate query embedding
        query_embedding = self.model.encode(user_query)
        
        # Search in vector database
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        if not results['metadatas'] or len(results['metadatas'][0]) == 0:
            return {
                'answer': "I don't have specific information about that topic. Please try asking about: bail, divorce, FIR filing, driving license, property law, employment rights, or other Indian legal topics.",
                'similarity': 0.0,
                'sources': [],
                'matched_question': None
            }
        
        # Get best match
        best_metadata = results['metadatas'][0][0]
        best_distance = results['distances'][0][0]
        
        # Convert distance to similarity (ChromaDB uses L2 distance)
        # For cosine similarity: similarity = 1 - (distance / 2)
        similarity = 1 - (best_distance / 2)
        
        logger.info(f"Query: '{user_query}' | Best match: '{best_metadata['question']}' | Similarity: {similarity:.3f}")
        
        # Check threshold
        if similarity < self.similarity_threshold:
            return {
                'answer': f"I couldn't find an exact answer (confidence: {similarity:.1%}). Please try rephrasing your question or ask about specific Indian legal topics.",
                'similarity': similarity,
                'sources': [],
                'matched_question': best_metadata['question']
            }
        
        return {
            'answer': best_metadata['answer'],
            'similarity': similarity,
            'sources': [best_metadata.get('category', 'Legal Database')],
            'matched_question': best_metadata['question']
        }
    
    def evaluate(self, test_dataset: List[Dict]) -> Dict:
        """
        Evaluate RAG system on test dataset
        
        Returns:
            Dict with accuracy metrics
        """
        logger.info(f"Evaluating on {len(test_dataset)} test cases...")
        
        correct = 0
        total = len(test_dataset)
        similarities = []
        
        for item in test_dataset:
            result = self.get_answer(item['question'])
            
            # Check if answer matches (exact or contains key information)
            if result['answer'] == item['answer'] or item['answer'][:50] in result['answer']:
                correct += 1
            
            similarities.append(result['similarity'])
        
        accuracy = correct / total if total > 0 else 0
        avg_similarity = np.mean(similarities) if similarities else 0
        
        metrics = {
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'avg_similarity': avg_similarity,
            'threshold': self.similarity_threshold
        }
        
        logger.info(f"📊 Evaluation Results:")
        logger.info(f"   Accuracy: {accuracy:.2%} ({correct}/{total})")
        logger.info(f"   Average Similarity: {avg_similarity:.3f}")
        logger.info(f"   Threshold: {self.similarity_threshold}")
        
        return metrics
    
    def save_metrics(self, metrics: Dict, output_file: str = "rag_metrics.json"):
        """Save evaluation metrics to file"""
        with open(output_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Metrics saved to {output_file}")


def main():
    """Main training and evaluation pipeline"""
    logger.info("=" * 80)
    logger.info("🚀 PRODUCTION-GRADE VECTOR RAG TRAINING PIPELINE")
    logger.info("=" * 80)
    
    # Initialize RAG system
    rag = VectorRAGTrainer(
        model_name="all-mpnet-base-v2",  # Best balance of speed and accuracy
        similarity_threshold=0.75  # 75% similarity threshold
    )
    
    # Build dataset
    dataset = rag.build_dataset()
    
    # Split into train/test (80/20)
    split_idx = int(len(dataset) * 0.8)
    train_dataset = dataset[:split_idx]
    test_dataset = dataset[split_idx:]
    
    logger.info(f"📚 Dataset split: {len(train_dataset)} train, {len(test_dataset)} test")
    
    # Train
    rag.train(train_dataset)
    
    # Evaluate
    metrics = rag.evaluate(test_dataset)
    
    # Save metrics
    rag.save_metrics(metrics)
    
    # Test with sample queries
    logger.info("\n" + "=" * 80)
    logger.info("🧪 TESTING WITH SAMPLE QUERIES")
    logger.info("=" * 80)
    
    test_queries = [
        "What is a DL?",
        "How to file FIR?",
        "What is bail?",
        "Grounds for divorce?",
        "What is Section 420?",
        "How to get driving license?",
        "What are consumer rights?"
    ]
    
    for query in test_queries:
        result = rag.get_answer(query)
        logger.info(f"\nQ: {query}")
        logger.info(f"Similarity: {result['similarity']:.3f}")
        logger.info(f"A: {result['answer'][:200]}...")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ TRAINING AND EVALUATION COMPLETE!")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
