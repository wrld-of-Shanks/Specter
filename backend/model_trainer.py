#!/usr/bin/env python3
"""
Advanced Model Training and Accuracy Optimization System
for SPECTER Legal Assistant
"""

import asyncio
import json
import logging
import time
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
import requests
from datetime import datetime
from sklearn.metrics import precision_score, recall_score, f1_score
from sentence_transformers import SentenceTransformer
import torch
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

# Local imports
from local_llm import chat_with_ollama, generate_with_context
from rag_pipeline import LegalRAGPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('model_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_MODELS = ["lawman-legal-max-accuracy", "lawman-legal-v2", "qwen2.5:7b-instruct"]
DEFAULT_BATCH_SIZE = 8
MAX_SEQ_LENGTH = 2048
LEARNING_RATE = 5e-5
NUM_EPOCHS = 3
EVAL_STEPS = 100
SAVE_STEPS = 500

@dataclass
class TrainingExample:
    question: str
    ideal_answer: str
    category: str
    difficulty: str
    keywords: List[str]
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'question': self.question,
            'ideal_answer': self.ideal_answer,
            'category': self.category,
            'difficulty': self.difficulty,
            'keywords': self.keywords,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TrainingExample':
        return cls(
            question=data['question'],
            ideal_answer=data['ideal_answer'],
            category=data.get('category', 'general'),
            difficulty=data.get('difficulty', 'medium'),
            keywords=data.get('keywords', []),
            metadata=data.get('metadata', {})
        )

@dataclass
class ModelPerformance:
    model_name: str
    accuracy_score: float = 0.0
    response_time: float = 0.0
    token_efficiency: float = 0.0
    legal_accuracy: float = 0.0
    overall_score: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    evaluation_metrics: dict = field(default_factory=dict)
    
    def calculate_overall_score(self) -> float:
        """Calculate weighted overall score based on metrics"""
        weights = {
            'accuracy': 0.4,
            'legal_accuracy': 0.3,
            'response_time': 0.1,
            'token_efficiency': 0.1,
            'f1': 0.1
        }
        
        # Normalize response time (lower is better)
        normalized_response_time = 1.0 / (1.0 + self.response_time)
        
        self.overall_score = (
            weights['accuracy'] * self.accuracy_score +
            weights['legal_accuracy'] * self.legal_accuracy +
            weights['response_time'] * normalized_response_time +
            weights['token_efficiency'] * self.token_efficiency +
            weights['f1'] * self.f1
        )
        return self.overall_score

class LegalDataset(Dataset):
    """Dataset for legal Q&A training"""
    
    def __init__(self, examples: List[TrainingExample], tokenizer, max_length=512):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        example = self.examples[idx]
        encoding = self.tokenizer(
            example.question,
            example.ideal_answer,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'labels': encoding['input_ids'].squeeze()
        }

class LegalModelTrainer:
    """Advanced model trainer for legal domain fine-tuning"""
    
    def __init__(
        self,
        model_names: List[str] = None,
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
    ):
        self.models = model_names or DEFAULT_MODELS
        self.device = device
        self.rag_pipeline = LegalRAGPipeline()
        self.training_data = self._load_training_data()
        self.performance_metrics = {model: [] for model in self.models}
        self.current_model = None
        self.tokenizer = None
        self.model = None
        
    def _load_training_data(self, data_path: Optional[str] = None) -> List[TrainingExample]:
        """Load training data from file or use default dataset"""
        if data_path and Path(data_path).exists():
            with open(data_path, 'r') as f:
                data = json.load(f)
            return [TrainingExample.from_dict(item) for item in data]
            
        # Default training data if no file provided
        return [
            TrainingExample(
                question="What are the essential elements of a valid contract?",
                ideal_answer="A valid contract requires: 1) Offer and acceptance, 2) Consideration, 3) Legal capacity, "
                           "4) Legal purpose, 5) Mutual consent. These elements must be present for enforceability.",
                category="Contract Law",
                difficulty="Basic",
                keywords=["contract", "offer", "acceptance", "consideration", "capacity"]
            ),
            TrainingExample(
                question="What is the difference between civil and criminal law?",
                ideal_answer="Civil law deals with disputes between individuals/organizations where compensation is awarded, while criminal law involves prosecution by the state for offenses against society, with penalties including imprisonment and fines.",
                category="Legal System",
                difficulty="Basic", 
                keywords=["civil", "criminal", "law", "prosecution", "compensation"]
            ),
            TrainingExample(
                question="What are the key provisions of the Information Technology Act 2000?",
                ideal_answer="The IT Act 2000 covers: 1) Digital signatures and electronic records, 2) Cyber crimes and penalties, 3) Data protection and privacy, 4) Intermediary guidelines, 5) Cyber appellate tribunal establishment.",
                category="Cyber Law",
                difficulty="Intermediate",
                keywords=["IT Act", "digital signatures", "cyber crimes", "data protection", "intermediary"]
            ),
            TrainingExample(
                question="Explain the concept of corporate governance in Indian context.",
                ideal_answer="Corporate governance in India involves: 1) Board composition and independence, 2) Shareholder rights protection, 3) Transparency and disclosure norms, 4) Audit committee requirements, 5) Compliance with Companies Act 2013 and SEBI regulations.",
                category="Corporate Law",
                difficulty="Advanced",
                keywords=["corporate governance", "board", "shareholders", "transparency", "SEBI"]
            ),
            TrainingExample(
                question="What are the grounds for divorce under Hindu Marriage Act?",
                ideal_answer="Grounds for divorce under Hindu Marriage Act include: 1) Adultery, 2) Cruelty, 3) Desertion for 2+ years, 4) Conversion to another religion, 5) Unsoundness of mind, 6) Virulent disease, 7) Renunciation of worldly life.",
                category="Family Law",
                difficulty="Intermediate",
                keywords=["divorce", "Hindu Marriage Act", "adultery", "cruelty", "desertion"]
            )
        ]
        
    def load_model(self, model_name: str):
        """Load the specified model and tokenizer"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            logger.info(f"Loading model: {model_name}")
            self.current_model = model_name
            
            if 'gpt' in model_name.lower() or 'openai' in model_name.lower():
                # For OpenAI models, we'll use the API
                self.model = None
                self.tokenizer = None
                self.use_api = True
            else:
                # For local models
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if 'cuda' in self.device else torch.float32,
                    device_map="auto" if 'cuda' in self.device else None
                )
                self.use_api = False
                
            logger.info(f"Successfully loaded model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {str(e)}")
            return False
    
    def train(self, model_name: str, output_dir: str = "trained_models"):
        """Train the specified model on the training data"""
        if not self.load_model(model_name):
            return False
            
        logger.info(f"Starting training for model: {model_name}")
        output_dir = Path(output_dir) / model_name.replace("/", "_")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Prepare datasets
            train_size = int(0.9 * len(self.training_data))
            train_data = self.training_data[:train_size]
            val_data = self.training_data[train_size:]
            
            train_dataset = LegalDataset(train_data, self.tokenizer, MAX_SEQ_LENGTH)
            val_dataset = LegalDataset(val_data, self.tokenizer, MAX_SEQ_LENGTH)
            
            # Create data loaders
            train_loader = DataLoader(
                train_dataset,
                batch_size=DEFAULT_BATCH_SIZE,
                shuffle=True,
                num_workers=4
            )
            
            val_loader = DataLoader(
                val_dataset,
                batch_size=DEFAULT_BATCH_SIZE,
                num_workers=4
            )
            
            # Set up optimizer and learning rate scheduler
            optimizer = torch.optim.AdamW(
                self.model.parameters(),
                lr=LEARNING_RATE,
                weight_decay=0.01
            )
            
            # Training loop
            best_val_loss = float('inf')
            global_step = 0
            
            for epoch in range(NUM_EPOCHS):
                self.model.train()
                total_loss = 0
                
                for batch in tqdm(train_loader, desc=f"Epoch {epoch + 1}/{NUM_EPOCHS}"):
                    # Move batch to device
                    input_ids = batch['input_ids'].to(self.device)
                    attention_mask = batch['attention_mask'].to(self.device)
                    labels = batch['labels'].to(self.device)
                    
                    # Forward pass
                    outputs = self.model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        labels=labels
                    )
                    
                    loss = outputs.loss
                    total_loss += loss.item()
                    
                    # Backward pass and optimize
                    optimizer.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                    optimizer.step()
                    
                    global_step += 1
                    
                    # Log training progress
                    if global_step % EVAL_STEPS == 0:
                        avg_train_loss = total_loss / EVAL_STEPS
                        val_loss = self.evaluate(val_loader)
                        logger.info(
                            f"Step {global_step}: "
                            f"Train Loss: {avg_train_loss:.4f}, "
                            f"Val Loss: {val_loss:.4f}"
                        )
                        
                        # Save best model
                        if val_loss < best_val_loss:
                            best_val_loss = val_loss
                            self.save_model(output_dir / "best_model")
                        
                        total_loss = 0
                
                # Save model at the end of each epoch
                self.save_model(output_dir / f"epoch_{epoch + 1}")
            
            logger.info(f"Training completed for model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error during training: {str(e)}")
            return False
    
    def evaluate(self, data_loader):
        """Evaluate the model on the given data loader"""
        self.model.eval()
        total_loss = 0
        
        with torch.no_grad():
            for batch in data_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                total_loss += outputs.loss.item()
        
        return total_loss / len(data_loader)
    
    def save_model(self, output_dir):
        """Save the model and tokenizer to the specified directory"""
        if not self.model or not self.tokenizer:
            return False
            
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            self.model.save_pretrained(output_dir)
            self.tokenizer.save_pretrained(output_dir)
            
            logger.info(f"Model saved to {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    async def evaluate_model_performance(
        self,
        model_name: str,
        test_data: Optional[List[TrainingExample]] = None,
        num_samples: int = 10
    ) -> ModelPerformance:
        """Comprehensive evaluation of model performance"""
        if not test_data:
            test_data = self.training_data[:num_samples]
        
        performance = ModelPerformance(model_name=model_name)
        correct = 0
        total_time = 0
        total_tokens = 0
        
        # Load model if not already loaded
        if not self.model or self.current_model != model_name:
            if not self.load_model(model_name):
                return performance
        
        for example in tqdm(test_data, desc=f"Evaluating {model_name}"):
            try:
                start_time = time.time()
                
                # Generate response
                if self.use_api:
                    # For API-based models
                    messages = [
                        {"role": "system", "content": "You are a legal assistant providing accurate and concise legal information."},
                        {"role": "user", "content": example.question}
                    ]
                    response = await chat_with_ollama(messages, model=model_name)
                    response_text = response
                else:
                    # For local models
                    input_ids = self.tokenizer.encode(
                        f"Question: {example.question}\nAnswer:",
                        return_tensors="pt"
                    ).to(self.device)
                    
                    outputs = self.model.generate(
                        input_ids,
                        max_length=MAX_SEQ_LENGTH,
                        num_return_sequences=1,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                    
                    response_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                    total_tokens += len(self.tokenizer.tokenize(response_text))
                
                # Calculate metrics
                elapsed = time.time() - start_time
                total_time += elapsed
                
                # Simple accuracy check (can be enhanced with more sophisticated metrics)
                if any(keyword.lower() in response_text.lower() for keyword in example.keywords):
                    correct += 1
                
            except Exception as e:
                logger.error(f"Error during evaluation: {str(e)}")
        
        # Calculate metrics
        performance.accuracy_score = correct / len(test_data)
        performance.response_time = total_time / len(test_data) if test_data else 0
        performance.token_efficiency = total_tokens / len(test_data) if test_data else 0
        
        # Calculate F1 score (simplified)
        performance.precision = performance.accuracy_score
        performance.recall = performance.accuracy_score
        performance.f1 = 2 * (performance.precision * performance.recall) / (performance.precision + performance.recall + 1e-10)
        
        # Calculate overall score
        performance.calculate_overall_score()
        
        # Store metrics
        self.performance_metrics[model_name].append(performance)
        
        return performance
    
    def optimize_model(self, model_name: str):
        """Optimize the model using various techniques"""
        logger.info(f"Optimizing model: {model_name}")
        
        # Load model if not already loaded
        if not self.model or self.current_model != model_name:
            if not self.load_model(model_name):
                return False
        
        try:
            # Apply optimization techniques
            if hasattr(self.model, 'to'):
                # Enable gradient checkpointing if available
                if hasattr(self.model, 'gradient_checkpointing_enable'):
                    self.model.gradient_checkpointing_enable()
                
                # Move to half precision for faster training
                if 'cuda' in self.device:
                    self.model = self.model.half()
            
            logger.info(f"Applied optimizations to model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error optimizing model: {str(e)}")
            return False
    
    def compare_models(self) -> Dict[str, float]:
        """Compare performance of all models"""
        results = {}
        
        for model_name in self.models:
            if model_name in self.performance_metrics and self.performance_metrics[model_name]:
                latest_perf = self.performance_metrics[model_name][-1]
                results[model_name] = {
                    'overall_score': latest_perf.overall_score,
                    'accuracy': latest_perf.accuracy_score,
                    'response_time': latest_perf.response_time,
                    'f1_score': latest_perf.f1
                }
        
        return results
    
    async def evaluate_model_response(self, model: str, question: str, ideal_answer: str) -> Dict:
        """Evaluate model response against ideal answer"""
        start_time = time.time()
        
        try:
            # Generate response using Ollama generate API
            system_prompt = "You are an expert Indian legal assistant. Provide accurate, comprehensive legal information."
            payload = {
                "model": model,
                "prompt": f"{system_prompt}\n\nQuestion: {question}",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 1024,
                }
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate", 
                json=payload, 
                timeout=120
            )
            response.raise_for_status()
            data = response.json()
            generated_text = data.get("response", "")
            
            response_time = time.time() - start_time
            
            # Calculate accuracy metrics
            accuracy_score = self._calculate_accuracy(generated_text, ideal_answer)
            legal_accuracy = self._calculate_legal_accuracy(generated_text, question)
            token_efficiency = self._calculate_token_efficiency(generated_text, ideal_answer)
            
            return {
                "response": generated_text,
                "response_time": response_time,
                "accuracy_score": accuracy_score,
                "legal_accuracy": legal_accuracy,
                "token_efficiency": token_efficiency,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error evaluating model {model}: {e}")
            return {
                "response": None,
                "response_time": float('inf'),
                "accuracy_score": 0.0,
                "legal_accuracy": 0.0,
                "token_efficiency": 0.0,
                "error": str(e)
            }
    
    def _calculate_accuracy(self, response: str, ideal_answer: str) -> float:
        """Calculate semantic accuracy score"""
        if not response or not ideal_answer:
            return 0.0
        
        # Simple keyword matching for now (can be enhanced with embeddings)
        response_words = set(response.lower().split())
        ideal_words = set(ideal_answer.lower().split())
        
        if not ideal_words:
            return 0.0
            
        intersection = response_words & ideal_words
        accuracy = len(intersection) / len(ideal_words)
        
        # Bonus for complete sentences and structure
        if '.' in response and len(response.split()) > 10:
            accuracy += 0.1
            
        return min(accuracy, 1.0)
    
    def _calculate_legal_accuracy(self, response: str, question: str) -> float:
        """Calculate legal-specific accuracy"""
        legal_keywords = ["law", "legal", "act", "section", "court", "jurisdiction", "statute", "regulation", "compliance", "penalty"]
        response_lower = response.lower()
        
        legal_score = sum(1 for keyword in legal_keywords if keyword in response_lower) / len(legal_keywords)
        
        # Check for structured legal responses
        structure_bonus = 0
        if any(marker in response for marker in ["1)", "2)", "•", "-"]):
            structure_bonus += 0.2
        if any(term in response.lower() for term in ["according to", "under the", "as per", "section"]):
            structure_bonus += 0.1
            
        return min(legal_score + structure_bonus, 1.0)
    
    def _calculate_token_efficiency(self, response: str, ideal_answer: str) -> float:
        """Calculate response efficiency"""
        if not response:
            return 0.0
            
        response_tokens = len(response.split())
        ideal_tokens = len(ideal_answer.split())
        
        if ideal_tokens == 0:
            return 0.0
            
        # Optimal range is 0.8x to 1.5x the ideal length
        ratio = response_tokens / ideal_tokens
        
        if 0.8 <= ratio <= 1.5:
            return 1.0
        elif ratio < 0.8:
            return ratio / 0.8
        else:
            return max(0.3, 1.5 / ratio)
    
    async def train_and_test_model(self, model: str) -> ModelPerformance:
        """Comprehensive training and testing for a model"""
        logger.info(f"🧪 Testing model: {model}")
        
        total_accuracy = 0
        total_response_time = 0
        total_token_efficiency = 0
        total_legal_accuracy = 0
        successful_tests = 0
        
        for example in self.training_data:
            logger.info(f"📝 Testing: {example.category} - {example.question[:50]}...")
            
            result = await self.evaluate_model_response(model, example.question, example.ideal_answer)
            
            if result["error"] is None:
                total_accuracy += result["accuracy_score"]
                total_response_time += result["response_time"]
                total_token_efficiency += result["token_efficiency"]
                total_legal_accuracy += result["legal_accuracy"]
                successful_tests += 1
                
                logger.info(f"✅ Accuracy: {result['accuracy_score']:.2f}, Legal: {result['legal_accuracy']:.2f}")
            else:
                logger.error(f"❌ Test failed: {result['error']}")
        
        if successful_tests == 0:
            return ModelPerformance(
                model_name=model,
                accuracy_score=0.0,
                response_time=float('inf'),
                token_efficiency=0.0,
                legal_accuracy=0.0,
                overall_score=0.0
            )
        
        # Calculate averages
        avg_accuracy = total_accuracy / successful_tests
        avg_response_time = total_response_time / successful_tests
        avg_token_efficiency = total_token_efficiency / successful_tests
        avg_legal_accuracy = total_legal_accuracy / successful_tests
        
        # Calculate overall score (weighted)
        overall_score = (
            avg_accuracy * 0.3 +
            avg_legal_accuracy * 0.4 +
            avg_token_efficiency * 0.2 +
            (1 / (1 + avg_response_time)) * 0.1
        )
        
        return ModelPerformance(
            model_name=model,
            accuracy_score=avg_accuracy,
            response_time=avg_response_time,
            token_efficiency=avg_token_efficiency,
            legal_accuracy=avg_legal_accuracy,
            overall_score=overall_score
        )
    
    async def run_comprehensive_training(self) -> Dict[str, ModelPerformance]:
        """Run training on all models and return performance metrics"""
        logger.info("🚀 Starting comprehensive model training and testing...")
        
        results = {}
        
        for model in self.models:
            performance = await self.train_and_test_model(model)
            results[model] = performance
            logger.info(f"📊 {model} - Overall Score: {performance.overall_score:.3f}")
        
        # Find best model
        best_model = max(results.items(), key=lambda x: x[1].overall_score)
        logger.info(f"🏆 Best performing model: {best_model[0]} (Score: {best_model[1].overall_score:.3f})")
        
        return results
    
    def generate_training_report(self, results: Dict[str, ModelPerformance]) -> str:
        """Generate comprehensive training report"""
        report = []
        report.append("=" * 80)
        report.append("🧠 LEGAL MODEL TRAINING & ACCURACY REPORT")
        report.append("=" * 80)
        report.append(f"📅 Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"🔢 Models Tested: {len(results)}")
        report.append(f"📚 Training Examples: {len(self.training_data)}")
        report.append("")
        
        # Sort models by overall score
        sorted_results = sorted(results.items(), key=lambda x: x[1].overall_score, reverse=True)
        
        for i, (model, performance) in enumerate(sorted_results, 1):
            report.append(f"{i}. 📊 {model}")
            report.append(f"   🎯 Overall Score: {performance.overall_score:.3f}")
            report.append(f"   📈 Accuracy: {performance.accuracy_score:.3f}")
            report.append(f"   ⚖️  Legal Accuracy: {performance.legal_accuracy:.3f}")
            report.append(f"   ⚡ Response Time: {performance.response_time:.2f}s")
            report.append(f"   💬 Token Efficiency: {performance.token_efficiency:.3f}")
            report.append("")
        
        # Recommendations
        best_model = sorted_results[0]
        report.append("🎯 RECOMMENDATIONS:")
        report.append(f"✅ Use '{best_model[0]}' for production (Score: {best_model[1].overall_score:.3f})")
        
        if best_model[1].legal_accuracy < 0.8:
            report.append("⚠️  Consider additional legal domain fine-tuning")
        
        if best_model[1].response_time > 5.0:
            report.append("⚠️  Response time is high, consider optimization")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

async def main():
    """Main training function"""
    trainer = LegalModelTrainer()
    
    # Run comprehensive training
    results = await trainer.run_comprehensive_training()
    
    # Generate and save report
    report = trainer.generate_training_report(results)
    
    # Save report to file
    report_path = Path("/Users/shanks/Desktop/lawman-main/backend/training_report.txt")
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(report)
    print(f"\n📄 Detailed report saved to: {report_path}")
    
    # Save metrics as JSON for API consumption
    metrics_path = Path("/Users/shanks/Desktop/lawman-main/backend/model_metrics.json")
    metrics_data = {
        model: {
            "accuracy_score": perf.accuracy_score,
            "response_time": perf.response_time,
            "token_efficiency": perf.token_efficiency,
            "legal_accuracy": perf.legal_accuracy,
            "overall_score": perf.overall_score
        }
        for model, perf in results.items()
    }
    
    with open(metrics_path, 'w') as f:
        json.dump(metrics_data, f, indent=2)
    
    print(f"📊 Metrics saved to: {metrics_path}")

if __name__ == "__main__":
    asyncio.run(main())
