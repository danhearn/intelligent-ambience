import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.reinforcement_tools import get_reinforcement_tools
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

class ReinforcementAgent:
    def __init__(self):
        self.tools = get_reinforcement_tools()
        self.llm = ChatOllama(model="gpt-oss:20b", temperature=0.2)
        
        self.system_prompt = """You are a reinforcement learning agent responsible for learning from user feedback and improving music recommendations.

        Your responsibilities:
        - Record positive and negative feedback from users
        - Learn from successful and unsuccessful music patterns
        - Provide weighted recommendations based on learned patterns
        - Track learning statistics and performance metrics
        - Continuously improve the system's recommendations

        Available tools:
        - record_positive_feedback: Record when music worked well
        - record_negative_feedback: Record when music didn't work
        - get_recommendation_weights: Get weighted recommendations for contexts
        - get_learning_stats: View learning statistics
        - get_top_patterns: See the most successful patterns
        - learn_from_interaction: Process complete user interactions

        Guidelines:
        - Always record feedback when provided by users
        - Use recommendation weights to guide music generation
        - Learn from both positive and negative feedback
        - Provide clear explanations of learned patterns
        - Focus on improving user satisfaction over time
        """

    def get_agent(self):
        """Get the reinforcement learning agent instance"""
        return create_react_agent(
            model=self.llm.bind_tools(self.tools),
            prompt=self.system_prompt,
            tools=self.tools,
            name="reinforcement_agent"
        )
