"""
LLM Service using Ollama for local inference
Supports both chat and embedding models
"""

import ollama
from typing import List, Dict, Any, Optional
import os
import asyncio
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings

class LLMService:
    """Service for LLM operations using Ollama"""
    
    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
        # Smallest models for local inference
        self.chat_model = "phi3:mini"  # 3.8B parameters
        self.embedding_model = "nomic-embed-text"  # 137M parameters
        
        # Initialize LangChain components
        self.llm = Ollama(
            model=self.chat_model,
            base_url=self.ollama_host
        )
        
        self.embeddings = OllamaEmbeddings(
            model=self.embedding_model,
            base_url=self.ollama_host
        )
        
        # Embedding dimension for nomic-embed-text
        self.embedding_dimension = 768
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text using Ollama"""
        try:
            # Use LangChain embeddings
            embedding = await asyncio.get_event_loop().run_in_executor(
                None, self.embeddings.embed_query, text
            )
            return embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return None
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        """Generate response using Ollama chat model"""
        try:
            # Convert messages to Ollama format
            ollama_messages = []
            for msg in messages:
                ollama_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Call Ollama API
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ollama.chat(
                    model=self.chat_model,
                    messages=ollama_messages,
                    options={
                        "temperature": kwargs.get("temperature", 0.7),
                        "top_p": kwargs.get("top_p", 0.9),
                        "max_tokens": kwargs.get("max_tokens", 1000)
                    }
                )
            )
            
            return response["message"]["content"]
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return None
    
    async def generate_with_prompt(self, prompt: str, **kwargs) -> Optional[str]:
        """Generate response from a single prompt"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ollama.generate(
                    model=self.chat_model,
                    prompt=prompt,
                    options={
                        "temperature": kwargs.get("temperature", 0.7),
                        "top_p": kwargs.get("top_p", 0.9),
                        "max_tokens": kwargs.get("max_tokens", 1000)
                    }
                )
            )
            
            return response["response"]
            
        except Exception as e:
            print(f"Error generating with prompt: {e}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        try:
            models = ollama.list()
            return {
                "available_models": [model["name"] for model in models["models"]],
                "chat_model": self.chat_model,
                "embedding_model": self.embedding_model,
                "embedding_dimension": self.embedding_dimension,
                "ollama_host": self.ollama_host
            }
        except Exception as e:
            return {
                "error": str(e),
                "chat_model": self.chat_model,
                "embedding_model": self.embedding_model,
                "embedding_dimension": self.embedding_dimension,
                "ollama_host": self.ollama_host
            }
    
    async def health_check(self) -> bool:
        """Check if Ollama service is healthy"""
        try:
            # Try to list models to check connectivity
            await asyncio.get_event_loop().run_in_executor(None, ollama.list)
            return True
        except Exception as e:
            print(f"Ollama health check failed: {e}")
            return False
