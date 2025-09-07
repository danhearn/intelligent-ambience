import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.local_context_tools import get_local_context_tools
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
load_dotenv()

class LocalContextAgent:
    def __init__(self):
        self.tools = get_local_context_tools()
        self.llm = ChatOllama(model="gpt-oss:20b", temperature=0.3)
        
        self.system_prompt = """You are an autonomous agent that can use the following tools to answer questions:
        get_image_caption: Get the caption of an image uploaded by the user to understand the environment the user is in. This tool is a image to text model that can caption images with a conditioning prompt.

        Your goal is to understand the environment the user is in. You should always use the get_image_caption tool to understand the environment the user is in.
        You can call this tool a MAXIMUM of 3 times. You can use a prompt to get specific information about the environment the user is in.
        After an initial prompt, you can use the get_image_caption tool to get more specific information about the environment the user is in.
        You should return a response that the supervisor agent can use to understand the environment the user is in and generate music for. 

        Return your response in ONLY the following format:
        "The environment the user is in is [environment]. There is [specific information about the environment]."

        """

    def get_agent(self):
        """Get the local context agent instance"""
        return create_react_agent(
            model=self.llm.bind_tools(self.tools),
            prompt=self.system_prompt,
            tools=self.tools,
            name="local_context_agent"
        )