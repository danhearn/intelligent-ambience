import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.vector_memory_tools import get_vector_memory_tools
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

class MemoryAgent:
    def __init__(self):
        self.tools = get_vector_memory_tools()
        self.llm = ChatOllama(model="gpt-oss:20b", temperature=0.3)
        
        self.system_prompt = """You are a memory management agent responsible for storing and retrieving information from the vector database.

        Your responsibilities:
        - Store user preferences and settings
        - Record music generation history with context
        - Learn from environment patterns
        - Search for similar contexts and preferences
        - Maintain the knowledge base for the intelligent ambience system

        Available tools:
        - add_to_vector_store: Store general text in the vector database
        - search_vector_store: Search for similar text in the vector database
        - add_music_generation_memory: Record music generations with full context
        - search_music_memory: Find similar music that worked before
        - add_user_preference: Store user preferences with categories
        - search_preferences: Find relevant user preferences
        - add_environment_pattern: Learn from successful environment-music combinations
        - search_environment_patterns: Find similar environment patterns

        Guidelines:
        - Always use the most specific tool for the task
        - When searching, use descriptive queries that capture the context
        - Store information with rich metadata for better retrieval
        - Provide clear, structured responses about what was found or stored
        """

    def get_agent(self):
        """Get the memory agent instance"""
        return create_react_agent(
            model=self.llm.bind_tools(self.tools),
            prompt=self.system_prompt,
            tools=self.tools,
            name="memory_agent"
        )
