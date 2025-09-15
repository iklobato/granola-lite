"""
Prompt templates for the Notes App
Organized by functionality and use case
"""

from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate

# RAG System Prompts
RAG_SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on provided notes. 
Be concise, accurate, and helpful. If you cannot find the answer in the provided notes, 
clearly state that the information is not available in the notes."""

RAG_HUMAN_PROMPT = """Based on the following notes, please answer the question: "{question}"

Notes:
{context}

Please provide a helpful answer based on the information in the notes. 
If the answer cannot be found in the notes, please say so clearly."""

# Create the RAG prompt template
rag_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(RAG_SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template(RAG_HUMAN_PROMPT)
])

# Note Analysis Prompts
NOTE_ANALYSIS_SYSTEM = """You are a note analysis assistant. Analyze the provided note and extract key information, 
topics, and insights. Provide a structured analysis."""

NOTE_ANALYSIS_HUMAN = """Analyze the following note and provide:
1. Key topics and themes
2. Important information
3. Suggested tags
4. Summary

Note: {note_content}"""

note_analysis_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(NOTE_ANALYSIS_SYSTEM),
    HumanMessagePromptTemplate.from_template(NOTE_ANALYSIS_HUMAN)
])

# Conversation Prompts
CONVERSATION_SYSTEM = """You are a helpful assistant for a notes application. 
You help users manage their notes and answer questions about them. 
Maintain a friendly and professional tone."""

conversation_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(CONVERSATION_SYSTEM),
    HumanMessagePromptTemplate.from_template("{user_input}")
])

# Prompt registry for easy access
PROMPT_REGISTRY = {
    "rag": rag_prompt,
    "note_analysis": note_analysis_prompt,
    "conversation": conversation_prompt
}

def get_prompt(prompt_name: str) -> ChatPromptTemplate:
    """Get a prompt template by name"""
    if prompt_name not in PROMPT_REGISTRY:
        raise ValueError(f"Prompt '{prompt_name}' not found. Available prompts: {list(PROMPT_REGISTRY.keys())}")
    return PROMPT_REGISTRY[prompt_name]
