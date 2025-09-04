from agents.chatbot_agent import ChatbotAgent
from dotenv import load_dotenv

load_dotenv()

def main():
    # Initialize the agent
    agent = ChatbotAgent()
    
    print("LangGraph Agent System")
    print("Type 'quit', 'exit', or 'q' to exit")
    print("-" * 40)
    
    # Main application loop
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            
            if user_input.strip():
                # Process through agent
                agent.stream_response(user_input)
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Shutting down...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Continuing...")

if __name__ == "__main__":
    main()