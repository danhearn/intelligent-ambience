from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools import tool
from datetime import datetime


class VectorMemory:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorMemory, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            import os
            # Ensure the directory exists
            os.makedirs("./chroma_langchain_db", exist_ok=True)
            
            self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
            self.vector_store = Chroma(
                collection_name="intelligent_ambience_memory",
                embedding_function=self.embeddings,
                persist_directory="./chroma_langchain_db",
            )
            self._initialized = True
            print(f"Vector memory initialized. Database location: {os.path.abspath('./chroma_langchain_db')}")

    def add_to_vector_store(self, text: str, metadata: dict = None):
        if metadata:
            self.vector_store.add_texts([text], metadatas=[metadata])
        else:
            self.vector_store.add_texts([text])
        return "Text added to vector store"
    
    def search_vector_store(self, text: str, k: int = 5):
        return self.vector_store.similarity_search(text, k=k)
    
    def search_with_metadata(self, text: str, k: int = 5):
        return self.vector_store.similarity_search_with_score(text, k=k)

@tool
def add_to_vector_store(text: str):
    """
    Add text to the vector store
    Args:
        text: The text to add to the vector store
    Returns:
        "Text added to vector store"
    """
    return vector_memory_instance.add_to_vector_store(text)

@tool
def search_vector_store(text: str, k: int = 5):
    """
    Search the vector store for similar text
    Args:
        text: The text to search for
        k: Number of similar results to return
    Returns:
        The most similar texts in the vector store
    """
    results = vector_memory_instance.search_vector_store(text, k)
    return [doc.page_content for doc in results]

@tool
def add_music_generation_memory(context: str, environment: str, music_prompt: str, user_feedback: str = ""):
    """
    Add a music generation to memory with metadata
    Args:
        context: The emotional/global context used
        environment: The local environment description
        music_prompt: The music generation prompt used
        user_feedback: Any feedback from the user (optional)
    Returns:
        Confirmation that the generation was recorded
    """
    text = f"Music generation: {music_prompt} for {environment} with context: {context}"
    metadata = {
        "type": "music_generation",
        "context": context,
        "environment": environment,
        "music_prompt": music_prompt,
        "user_feedback": user_feedback,
        "timestamp": datetime.now().isoformat()
    }
    vector_memory_instance.add_to_vector_store(text, metadata)
    return f"Recorded music generation: {music_prompt} for {environment}"

@tool
def search_music_memory(query: str, k: int = 5):
    """
    Search for similar music generations
    Args:
        query: Search query (e.g., 'morning coffee music', 'relaxing evening')
        k: Number of results to return
    Returns:
        Similar music generations with context
    """
    results = vector_memory_instance.search_with_metadata(query, k)
    if not results:
        return f"No similar music found for query: {query}"
    
    response = f"Found {len(results)} similar music generations for '{query}':\n\n"
    for i, (doc, score) in enumerate(results, 1):
        metadata = doc.metadata
        response += f"{i}. Music: {metadata.get('music_prompt', 'N/A')}\n"
        response += f"   Context: {metadata.get('context', 'N/A')}\n"
        response += f"   Environment: {metadata.get('environment', 'N/A')}\n"
        response += f"   Similarity: {1-score:.2f}\n"
        if metadata.get('user_feedback'):
            response += f"   Feedback: {metadata['user_feedback']}\n"
        response += f"   Date: {metadata.get('timestamp', 'N/A')}\n\n"
    
    return response

@tool
def add_user_preference(key: str, value: str, category: str = "general"):
    """
    Add a user preference to memory
    Args:
        key: The preference key (e.g., 'music_style', 'volume_level')
        value: The preference value (e.g., 'ambient', 'low')
        category: The category of preference (e.g., 'music', 'environment')
    Returns:
        Confirmation that the preference was saved
    """
    text = f"User preference: {key} = {value} in category {category}"
    metadata = {
        "type": "user_preference",
        "key": key,
        "value": value,
        "category": category,
        "timestamp": datetime.now().isoformat()
    }
    vector_memory_instance.add_to_vector_store(text, metadata)
    return f"Remembered preference: {key} = {value} in category {category}"

@tool
def search_preferences(query: str, category: str = "", k: int = 5):
    """
    Search for user preferences
    Args:
        query: Search query (e.g., 'morning music', 'relaxing sounds')
        category: Filter by category (optional)
        k: Number of results to return
    Returns:
        Found preferences with similarity scores
    """
    results = vector_memory_instance.search_with_metadata(query, k)
    if not results:
        return f"No preferences found for query: {query}"
    
    # Filter by category if specified
    filtered_results = []
    for doc, score in results:
        metadata = doc.metadata
        if metadata.get('type') == 'user_preference':
            if not category or metadata.get('category') == category:
                filtered_results.append((doc, score))
    
    if not filtered_results:
        return f"No preferences found for query: {query} in category: {category}"
    
    response = f"Found {len(filtered_results)} preferences for '{query}':\n\n"
    for i, (doc, score) in enumerate(filtered_results, 1):
        metadata = doc.metadata
        response += f"{i}. {metadata.get('key', 'N/A')}: {metadata.get('value', 'N/A')}\n"
        response += f"   Category: {metadata.get('category', 'N/A')}\n"
        response += f"   Similarity: {1-score:.2f}\n"
        response += f"   Date: {metadata.get('timestamp', 'N/A')}\n\n"
    
    return response

@tool
def add_environment_pattern(location: str, time_of_day: str, environment_description: str, preferred_music_style: str):
    """
    Learn from environment patterns
    Args:
        location: The location (e.g., 'Honolulu, Hawaii')
        time_of_day: The time of day (e.g., 'morning', 'evening')
        environment_description: Description of the environment
        preferred_music_style: The music style that worked well
    Returns:
        Confirmation that the pattern was learned
    """
    text = f"Environment pattern: {location} at {time_of_day} - {environment_description} prefers {preferred_music_style}"
    metadata = {
        "type": "environment_pattern",
        "location": location,
        "time_of_day": time_of_day,
        "environment_description": environment_description,
        "preferred_music_style": preferred_music_style,
        "timestamp": datetime.now().isoformat()
    }
    vector_memory_instance.add_to_vector_store(text, metadata)
    return f"Learned pattern: {preferred_music_style} works well for {environment_description} in {location} at {time_of_day}"

@tool
def search_environment_patterns(query: str, location: str = "", time_of_day: str = "", k: int = 5):
    """
    Search for environment patterns
    Args:
        query: Search query (e.g., 'morning work environment', 'evening relaxation')
        location: Filter by location (optional)
        time_of_day: Filter by time of day (optional)
        k: Number of results to return
    Returns:
        Found environment patterns with similarity scores
    """
    results = vector_memory_instance.search_with_metadata(query, k)
    if not results:
        return f"No environment patterns found for query: {query}"
    
    # Filter by type and optional filters
    filtered_results = []
    for doc, score in results:
        metadata = doc.metadata
        if metadata.get('type') == 'environment_pattern':
            if (not location or metadata.get('location') == location) and \
               (not time_of_day or metadata.get('time_of_day') == time_of_day):
                filtered_results.append((doc, score))
    
    if not filtered_results:
        return f"No environment patterns found for query: {query}"
    
    response = f"Found {len(filtered_results)} environment patterns for '{query}':\n\n"
    for i, (doc, score) in enumerate(filtered_results, 1):
        metadata = doc.metadata
        response += f"{i}. {metadata.get('location', 'N/A')} at {metadata.get('time_of_day', 'N/A')}\n"
        response += f"   Environment: {metadata.get('environment_description', 'N/A')}\n"
        response += f"   Preferred music: {metadata.get('preferred_music_style', 'N/A')}\n"
        response += f"   Similarity: {1-score:.2f}\n"
        response += f"   Date: {metadata.get('timestamp', 'N/A')}\n\n"
    
    return response

vector_memory_instance = VectorMemory()

def get_vector_memory_tools():
    """Get all vector memory tools for the intelligent ambience system"""
    vector_store_tools = [
        add_to_vector_store,
        search_vector_store,
        add_music_generation_memory,
        search_music_memory,
        add_user_preference,
        search_preferences,
        add_environment_pattern,
        search_environment_patterns,
    ]
    return vector_store_tools