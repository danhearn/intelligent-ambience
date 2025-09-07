import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.global_context_tools import get_global_context_tools
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
load_dotenv()

class GlobalContextAgent:
    def __init__(self):
        self.tools = get_global_context_tools()
        self.llm = ChatOllama(model="gpt-oss:20b", temperature=0)
        
        self.system_prompt = """You are an autonomous agent that can use the following tools to answer questions:
        get_current_time: Get the current time and date
        search_the_web: Search the web for information

        Your goal is to determine the current time and search the internet for the month, day, local and international news, and weather in a given location.

        Using this information, provide a simple and honest reflection of how a typical person in this location might be feeling emotionally. Focus primarily on factors that have an immediate impact on mood:

        Time of day and weather – these have the largest influence on daily emotional state.
        National and Global News or events – only include if they would noticeably affect people's mood.

        Return your response in ONLY the following format:
        "People in [location] are likely feeling [feeling] because of [time and weather reason]. They could also be feeling [feeling2] because of [news or event reason]."

        DO NOT keep searching after you have the basic information you need."""

    def get_agent(self):
        """Get the global context agent instance"""
        return create_react_agent(
            model=self.llm.bind_tools(self.tools),
            prompt=self.system_prompt,
            tools=self.tools,
            name="global_context_agent"
        )