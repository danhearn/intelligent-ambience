from langchain_tavily import TavilySearch
from langchain.tools import Tool
from langchain_core.tools import tool
import datetime

def get_tools():
    """Get all available tools for the agent"""
    tools = []
    
    # Web search tool
    tavily_tool = TavilySearch(max_results=2)
    tools.append(tavily_tool)
    
    # Time tool - use the tool object, not call the function
    tools.append(get_current_time_tool)
    
    # You can add more custom tools here
    # Example: Weather tool, etc.
    
    return tools

def create_weather_tool():
    """Example weather tool (you can implement this later)"""
    def get_weather(location: str) -> str:
        """Get weather for a specific location"""
        # This would call a weather API
        return f"Weather data for {location} would go here"
    
    return Tool(
        name="get_weather",
        description="Get current weather for a location",
        func=get_weather
    )

def get_current_time(query: str = "") -> str:
    """Get current time and date"""
    now = datetime.datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

# Create the tool object
get_current_time_tool = Tool(
    name="get_current_time",
    description="Get current time and date",
    func=get_current_time
)

# Uncomment these lines when you want to add the tools:
# def get_tools():
#     tools = []
#     tools.append(TavilySearch(max_results=2))
#     tools.append(create_weather_tool())
#     tools.append(create_time_tool())
#     return tools