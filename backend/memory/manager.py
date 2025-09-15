"""
Memory management for user conversations and context
Uses LangChain memory components for conversation history
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.llms.base import LLM
import json
import os

class ConversationManager:
    """Manages user conversations and context using LangChain memory"""
    
    def __init__(self, llm: LLM, max_token_limit: int = 2000):
        self.llm = llm
        self.max_token_limit = max_token_limit
        
        # Use ConversationSummaryMemory for long-term context
        self.summary_memory = ConversationSummaryMemory(
            llm=llm,
            max_token_limit=max_token_limit,
            return_messages=True
        )
        
        # Use ConversationBufferWindowMemory for recent context
        self.buffer_memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 exchanges
            return_messages=True
        )
        
        # User-specific memory storage
        self.user_memories: Dict[str, Dict[str, Any]] = {}
    
    def get_user_memory(self, user_id: str) -> Dict[str, Any]:
        """Get or create memory for a user"""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = {
                "summary_memory": ConversationSummaryMemory(
                    llm=self.llm,
                    max_token_limit=self.max_token_limit,
                    return_messages=True
                ),
                "buffer_memory": ConversationBufferWindowMemory(
                    k=10,
                    return_messages=True
                ),
                "conversations": [],
                "context": {}
            }
        return self.user_memories[user_id]
    
    def add_message(self, user_id: str, message: str, is_user: bool = True, conversation_id: str = "default"):
        """Add a message to user's conversation history"""
        user_memory = self.get_user_memory(user_id)
        
        # Create message object
        if is_user:
            message_obj = HumanMessage(content=message)
        else:
            message_obj = AIMessage(content=message)
        
        # Add to buffer memory (recent context)
        user_memory["buffer_memory"].save_context(
            {"input": message if is_user else ""},
            {"output": message if not is_user else ""}
        )
        
        # Add to conversation history
        conversation = {
            "id": conversation_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "is_user": is_user
        }
        user_memory["conversations"].append(conversation)
        
        # Keep only last 100 conversations per user
        if len(user_memory["conversations"]) > 100:
            user_memory["conversations"] = user_memory["conversations"][-100:]
    
    def get_conversation_history(self, user_id: str, conversation_id: str = "default", limit: int = 20) -> List[Dict[str, Any]]:
        """Get conversation history for a user"""
        user_memory = self.get_user_memory(user_id)
        
        # Filter by conversation_id and limit
        conversations = [
            conv for conv in user_memory["conversations"] 
            if conv["id"] == conversation_id
        ][-limit:]
        
        return conversations
    
    def get_recent_context(self, user_id: str) -> List[BaseMessage]:
        """Get recent conversation context for RAG"""
        user_memory = self.get_user_memory(user_id)
        return user_memory["buffer_memory"].chat_memory.messages
    
    def get_summary_context(self, user_id: str) -> str:
        """Get summarized conversation context"""
        user_memory = self.get_user_memory(user_id)
        return user_memory["summary_memory"].predict_new_summary(
            user_memory["summary_memory"].chat_memory.messages,
            ""
        )
    
    def update_user_context(self, user_id: str, context: Dict[str, Any]):
        """Update user-specific context information"""
        user_memory = self.get_user_memory(user_id)
        user_memory["context"].update(context)
    
    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user-specific context"""
        user_memory = self.get_user_memory(user_id)
        return user_memory["context"]
    
    def clear_user_memory(self, user_id: str):
        """Clear all memory for a user"""
        if user_id in self.user_memories:
            del self.user_memories[user_id]
    
    def get_conversation_stats(self, user_id: str) -> Dict[str, Any]:
        """Get conversation statistics for a user"""
        user_memory = self.get_user_memory(user_id)
        conversations = user_memory["conversations"]
        
        if not conversations:
            return {"total_messages": 0, "conversations": 0, "last_activity": None}
        
        # Count unique conversations
        conversation_ids = set(conv["id"] for conv in conversations)
        
        # Get last activity
        last_activity = max(conv["timestamp"] for conv in conversations)
        
        return {
            "total_messages": len(conversations),
            "conversations": len(conversation_ids),
            "last_activity": last_activity
        }
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export user data for backup or analysis"""
        user_memory = self.get_user_memory(user_id)
        return {
            "user_id": user_id,
            "conversations": user_memory["conversations"],
            "context": user_memory["context"],
            "stats": self.get_conversation_stats(user_id),
            "exported_at": datetime.utcnow().isoformat()
        }
