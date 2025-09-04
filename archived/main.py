from agents.chatbot_agent import ChatbotAgent
from dotenv import load_dotenv

load_dotenv()

def main():
    # Initialize the agent
    agent = ChatbotAgent()
    
    print("🤖 Intelligent Agent System")
    print("Commands: start, stop, status, context, goals, quit")
    print("-" * 40)
    
    # Start autonomous mode
    agent.start_autonomous_mode()
    
    # Main application loop
    while True:
        try:
            user_input = input("User: ").strip().lower()
            
            if user_input == 'quit':
                agent.stop_autonomous_mode()
                print("👋 Goodbye! Shutting down...")
                break
            
            elif user_input == 'start':
                agent.start_autonomous_mode()
                print("🚀 Agent started in autonomous mode")
            
            elif user_input == 'stop':
                agent.stop_autonomous_mode()
                print("⏹️ Agent stopped")
            
            elif user_input == 'status':
                status = agent.get_agent_status()
                print(f"📊 Agent Status: {status['system_status']}")
                print(f"🎯 Current Task: {status['current_task']}")
                print(f"�� Autonomous Mode: {status['autonomous_mode']}")
                print(f"�� Context: {status['context']}")
            
            elif user_input == 'context':
                summary = agent.get_context_summary()
                print(f"📝 {summary}")
            
            elif user_input == 'goals':
                goals = agent.get_agent_status()["goals"]
                print("🎯 Agent Goals:")
                for i, goal in enumerate(goals, 1):
                    print(f"  {i}. {goal}")
            
            elif user_input:
                # Process through agent
                agent.stream_response(user_input)
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Shutting down...")
            agent.stop_autonomous_mode()
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Continuing...")

if __name__ == "__main__":
    main()