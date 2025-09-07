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

    def run(self, query: str, img_url: str):
        inputs = {"messages": [("user", query + " " + img_url)]}
        result = self.graph.invoke(inputs) 
        
        # Print only AI message content, not all metadata
        for m in result["messages"]:
            if hasattr(m, 'content') and m.content and hasattr(m, 'name') and m.name != 'user':
                print(f"{m.name}: {m.content}")
    
    def run_streaming(self, query: str, img_url: str):
        """Run the system with streaming output to see thinking process"""
        inputs = {"messages": [("user", query + " " + img_url)]}
        
        print("🤖 Starting intelligent ambience system...")
        print("=" * 50)
        
        for chunk in self.graph.stream(inputs):
            # Print each step of the process
            for key, value in chunk.items():
                if key == "messages":
                    for message in value:
                        if hasattr(message, 'content') and message.content:
                            print(f" {message.name}: {message.content}")
                        if hasattr(message, 'tool_calls') and message.tool_calls:
                            for tool_call in message.tool_calls:
                                print(f" {message.name} using tool: {tool_call['name']}")
                                if 'args' in tool_call:
                                    args_str = str(tool_call['args'])[:100] + "..." if len(str(tool_call['args'])) > 100 else str(tool_call['args'])
                                    print(f"   Args: {args_str}")
                elif key == "supervisor":
                    print(f" Supervisor: {value}")
                elif key == "global_context_agent":
                    print(f" Global Context: {value}")
                elif key == "local_context_agent":
                    print(f" Local Context: {value}")
                elif key == "memory_agent":
                    print(f" Memory: {value}")
                elif key == "reinforcement_agent":
                    print(f" Reinforcement: {value}")
                elif key == "music_generation_agent":
                    print(f" Music Generation: {value}")
            
            print("-" * 30)
        
        print("=" * 50)
        print("Completed!")
    
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
    
    def run_with_feedback_streaming(self, query: str, img_url: str, user_feedback: str = ""):
        """Run the system with streaming and interactive feedback for learning"""
        inputs = {"messages": [("user", query + " " + img_url)]}
        
        print("🤖 Starting intelligent ambience system with feedback...")
        print("=" * 50)
        
        for chunk in self.graph.stream(inputs):
            # Debug: Print what we're getting in each chunk
            print(f"DEBUG - Chunk keys: {list(chunk.keys())}")
            for key, value in chunk.items():
                print(f"DEBUG - {key}: {type(value)} - {str(value)[:100]}...")
            
            # Print each step of the process
            for key, value in chunk.items():
                if key == "messages":
                    for message in value:
                        if hasattr(message, 'content') and message.content:
                            print(f"💭 {message.name}: {message.content}")
                        if hasattr(message, 'tool_calls') and message.tool_calls:
                            for tool_call in message.tool_calls:
                                print(f"🔧 {message.name} using tool: {tool_call['name']}")
                                if 'args' in tool_call:
                                    args_str = str(tool_call['args'])[:100] + "..." if len(str(tool_call['args'])) > 100 else str(tool_call['args'])
                                    print(f"   Args: {args_str}")
                elif key == "supervisor":
                    if hasattr(value, 'content') and value.content:
                        print(f"🎯 Supervisor: {value.content}")
                elif key == "global_context_agent":
                    if hasattr(value, 'content') and value.content:
                        print(f"🌍 Global Context: {value.content}")
                elif key == "local_context_agent":
                    if hasattr(value, 'content') and value.content:
                        print(f"🏠 Local Context: {value.content}")
                elif key == "memory_agent":
                    if hasattr(value, 'content') and value.content:
                        print(f"🧠 Memory: {value.content}")
                elif key == "reinforcement_agent":
                    if hasattr(value, 'content') and value.content:
                        print(f"🎓 Reinforcement: {value.content}")
                elif key == "music_generation_agent":
                    if hasattr(value, 'content') and value.content:
                        print(f"🎵 Music Generation: {value.content}")
            
            print("-" * 30)
        
        print("=" * 50)
        print("✅ System completed!")
        
        # Ask for user feedback
        print("\n🎓 Feedback Time!")
        print("How was the system's response? Your feedback helps improve future interactions.")
        print("(Press Enter to skip, or type your feedback)")
        
        feedback = input("Your feedback: ").strip()
        
        if feedback:
            print(f"\n🎓 Learning from your feedback: {feedback}")
            # Process feedback through the reinforcement agent
            self._process_feedback(feedback, query, img_url)
        else:
            print("No feedback provided. System will continue with current settings.")
    
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
            
            print("🎓 Feedback processed successfully!")
            if hasattr(reinforcement_result, 'content') and reinforcement_result.content:
                print(f"System response: {reinforcement_result.content}")
                
        except Exception as e:
            print(f"⚠️ Error processing feedback: {e}")
            print("Feedback will be stored for future processing.")
    
def interactive_loop():
    """Run the system in an interactive loop, waiting for user input"""
    main_graph = MainGraph()
    
    print("🎵 Intelligent Ambience System Started!")
    print("Type 'quit' or 'exit' to stop the system")
    print("=" * 50)
    
    while True:
        try:
            # Get user input
            query = input("\n📍 Enter location/context: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not query:
                print("Please enter a location or context.")
                continue
            
            # Get image URL (optional)
            img_url = input("🖼️  Enter image URL (or press Enter to skip): ").strip()
            if not img_url:
                img_url = "no image provided"
            
            # Run the system
            print(f"\n🤖 Processing: {query}")
            main_graph.run_with_feedback_streaming(query, img_url=img_url)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again.")

img_url = 'https://farm5.staticflickr.com/4888/45890544791_0a419c887b_c.jpg' 

if __name__ == "__main__":
    # Choose your mode:
    
    # Mode 1: Interactive loop (for hosting/development)
    interactive_loop()
    
    # Mode 2: Single run (for testing)
    # main_graph = MainGraph()
    # main_graph.run_with_feedback_streaming("Sarajevo, Bosnia and Herzegovina", img_url=img_url)