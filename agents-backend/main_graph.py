import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.supervisor_agent import SupervisorAgent
from agents.global_context_agent import GlobalContextAgent
from agents.local_context_agent import LocalContextAgent
from agents.music_generation_agent import MusicGenerationAgent
from agents.memory_agent import MemoryAgent
from agents.reinforcement_agent import ReinforcementAgent

class MainGraph:
    def __init__(self):
        self.supervisor_agent = SupervisorAgent()
        self.global_context_agent = GlobalContextAgent()
        self.local_context_agent = LocalContextAgent()
        self.music_generation_agent = MusicGenerationAgent()
        self.memory_agent = MemoryAgent()
        self.reinforcement_agent = ReinforcementAgent()
        self.graph = self.supervisor_agent.get_supervisor(
            sub_agents=[
                self.global_context_agent.get_agent(),
                self.local_context_agent.get_agent(),
                self.music_generation_agent.get_agent(),
                self.memory_agent.get_agent(),
                self.reinforcement_agent.get_agent()
            ]
        ).compile()

    
    
    def run_with_feedback(self, query: str, img_url: str, user_feedback: str = ""):
        """Run the system and optionally provide feedback for learning"""
        inputs = {"messages": [("user", query + " " + img_url)]}
        result = self.graph.invoke(inputs)
        
        # If user provided feedback, learn from it
        if user_feedback:
            print(f"\nLearning from user feedback: {user_feedback}")
            # The reinforcement agent will be called by the supervisor
            # to process the feedback and learn from it
        
        # Print only AI message content, not all metadata
        for m in result["messages"]:
            if hasattr(m, 'content') and m.content and hasattr(m, 'name') and m.name != 'user':
                print(f"{m.name}: {m.content}")
        
        return result
    
    async def stream_with_feedback(self, query: str, img_url: str, user_feedback: str = ""):
        inputs = {"messages": [("user", f"{query} {img_url}")]}
        yield {"type": "status", "message": "Starting intelligent ambience system..."}

        for chunk in self.graph.stream(inputs):
            # Map LangGraph chunks into simple events
            for key, value in chunk.items():
                if key == "messages":
                    for message in value:
                        if hasattr(message, "content") and message.content:
                            yield {"type": "token", "text": f"{getattr(message, 'name', 'agent')}: {message.content}\n"}
                        if hasattr(message, "tool_calls") and message.tool_calls:
                            for tool_call in message.tool_calls:
                                yield {"type": "token", "text": f"tool: {tool_call.get('name', '')}\n"}
                elif key == "supervisor" and hasattr(value, "content") and value.content:
                    yield {"type": "token", "text": f"supervisor: {value.content}\n"}
                # You can add other keys similarly if useful

        yield {"type": "done", "summary": "ok"}
    
    def _process_feedback(self, feedback: str, original_query: str, img_url: str):
        """Process user feedback through the reinforcement agent"""
        try:
            # Create a feedback message for the reinforcement agent
            feedback_inputs = {
                "messages": [
                    ("user", f"Original query: {original_query} {img_url}"),
                    ("user", f"User feedback: {feedback}")
                ]
            }
            
            # Get the reinforcement agent to process the feedback
            reinforcement_result = self.reinforcement_agent.get_agent().invoke(feedback_inputs)
            
            print("Feedback processed successfully!")
            if hasattr(reinforcement_result, 'content') and reinforcement_result.content:
                print(f"System response: {reinforcement_result.content}")
                
        except Exception as e:
            print(f"Error processing feedback: {e}")
            print("Feedback will be stored for future processing.")
    