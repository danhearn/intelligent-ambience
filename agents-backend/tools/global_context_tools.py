from langchain_tavily import TavilySearch
from langchain_core.tools import tool
import datetime

def get_global_context_tools():
    """Get all the context tools for the agent"""
    tools = []
    tools.append(get_current_time)
    tools.append(search_the_web)
    return tools

@tool
def get_current_time(query: str = "") -> str:
    """Get current time and date"""
    now = datetime.datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

@tool
def search_the_web(query: str) -> str:
    """Search the web for information"""
    results = TavilySearch(max_results=5).run(query)
    return results