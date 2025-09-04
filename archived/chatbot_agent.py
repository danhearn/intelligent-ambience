from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing import Annotated
from typing_extensions import TypedDict
from tools.custom_tools import get_tools
import time
import threading
import random

class State(TypedDict):
    messages: Annotated[list, add_messages]
    context: dict
    goals: list
    current_task: str
    system_status: str
    autonomous_actions: list

class ChatbotAgent:
    def __init__(self):
        self.tools = get_tools()
        self.llm = ChatOllama(
            model="gpt-oss:20b",
            temperature=0.7
        ).bind_tools(self.tools)
        
        # Agent goals and capabilities
        self.goals = [
            "Monitor environmental conditions and adapt responses",
            "Proactively gather information to improve user experience",
            "Maintain context and suggest relevant actions",
            "Learn from interactions to provide better assistance"
        ]
        
        self.state = {
            "context": {},
            "goals": self.goals,
            "current_task": "idle",
            "system_status": "ready",
            "autonomous_actions": [],
            "user_preferences": {},
            "environmental_data": {}
        }
        
        self.running = False
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow with true agentic behavior"""
        graph_builder = StateGraph(State)
        
        # Enhanced agent node with autonomous decision making
        def agent_node(state: State):
            # Agent analyzes context and DECIDES what to do
            context = state.get("context", {})
            current_task = state.get("current_task", "idle")
            
            # Agent makes autonomous decisions about what information it needs
            autonomous_decisions = self._make_autonomous_decisions(context)
            
            # Create intelligent prompt that includes agent's decisions
            system_prompt = f"""
            You are an autonomous intelligent agent with these goals: {self.goals}
            Current context: {context}
            Current task: {current_task}
            
            Based on your analysis, you have decided to: {autonomous_decisions}
            
            Now analyze the user's request and:
            1. Determine if you need to use tools based on YOUR decisions
            2. Provide helpful, contextual responses
            3. Update the context based on the interaction
            4. Suggest proactive next steps based on your goals
            5. Take autonomous actions when appropriate
            """
            
            # Add system message to state
            enhanced_messages = [
                {"role": "system", "content": system_prompt},
                *state["messages"]
            ]
            
            response = self.llm.invoke(enhanced_messages)
            
            # Update context based on interaction and autonomous decisions
            new_context = self._update_context(state, response, autonomous_decisions)
            
            return {
                "messages": [response],
                "context": new_context,
                "current_task": self._determine_task(response),
                "system_status": "active",
                "autonomous_actions": autonomous_decisions
            }
        
        graph_builder.add_node("agent", agent_node)
        
        # Tools node
        tool_node = ToolNode(tools=self.tools)
        graph_builder.add_node("tools", tool_node)
        
        # Conditional edges
        graph_builder.add_conditional_edges(
            "agent",
            tools_condition,
        )
        
        # Regular edges
        graph_builder.add_edge("tools", "agent")
        graph_builder.add_edge(START, "agent")
        
        return graph_builder.compile()
    
    def _make_autonomous_decisions(self, context: dict) -> list:
        """Agent makes autonomous decisions about what to do"""
        decisions = []
        
        # Decision 1: Agent decides if it needs current time context
        if not context.get("time_context") or time.time() - context.get("last_time_check", 0) > 300:  # 5 minutes
            decisions.append("check_current_time_for_context")
            context["last_time_check"] = time.time()
        
        # Decision 2: Agent decides if it should gather environmental data
        if not context.get("environmental_data") or time.time() - context.get("last_env_check", 0) > 600:  # 10 minutes
            decisions.append("gather_environmental_data")
            context["last_env_check"] = time.time()
        
        # Decision 3: Agent decides if it should proactively search for relevant information
        if context.get("last_topic") and not context.get("proactive_search_done"):
            decisions.append("proactively_search_related_info")
            context["proactive_search_done"] = True
        
        # Decision 4: Agent decides if it should suggest next actions
        if context.get("user_interests") and not context.get("suggestions_given"):
            decisions.append("suggest_next_actions")
            context["suggestions_given"] = True
        
        return decisions
    
    def _update_context(self, state: State, response, autonomous_decisions: list) -> dict:
        """Update context based on interaction and autonomous decisions"""
        context = state.get("context", {})
        
        # Extract key information from response
        if hasattr(response, 'content'):
            content = response.content.lower()
            
            # Track user interests for proactive suggestions
            if "weather" in content:
                context["last_topic"] = "weather"
                context["user_interests"] = context.get("user_interests", []) + ["weather"]
            if "time" in content:
                context["last_topic"] = "time"
                context["user_interests"] = context.get("user_interests", []) + ["time"]
            if "search" in content:
                context["last_topic"] = "web_search"
                context["user_interests"] = context.get("user_interests", []) + ["information_gathering"]
        
        # Add autonomous decisions to context
        context["autonomous_decisions"] = autonomous_decisions
        context["last_interaction"] = time.time()
        
        return context
    
    def _determine_task(self, response) -> str:
        """Determine what task the agent is currently working on"""
        if hasattr(response, 'content'):
            content = response.content.lower()
            if "search" in content:
                return "web_search"
            elif "time" in content:
                return "time_inquiry"
            elif "weather" in content:
                return "weather_inquiry"
            elif "proactive" in content or "suggest" in content:
                return "proactive_assistance"
            else:
                return "general_conversation"
        return "unknown"
    
    def start_autonomous_mode(self):
        """Start the agent in truly autonomous mode"""
        self.running = True
        print("🤖 Agent starting TRULY autonomous mode...")
        
        # Start autonomous thread
        self.autonomous_thread = threading.Thread(target=self._autonomous_loop)
        self.autonomous_thread.daemon = True
        self.autonomous_thread.start()
    
    def _autonomous_loop(self):
        """Autonomous monitoring and proactive actions"""
        while self.running:
            try:
                # Agent takes proactive actions based on its goals
                self._take_proactive_actions()
                
                # Wait before next cycle
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"❌ Autonomous loop error: {e}")
                time.sleep(60)
    
    def _take_proactive_actions(self):
        """Agent takes proactive actions based on its goals"""
        context = self.state["context"]
        
        # Action 1: Agent proactively checks time context
        if not context.get("time_context") or time.time() - context.get("last_time_check", 0) > 300:
            current_time = time.localtime()
            hour = current_time.tm_hour
            
            if 6 <= hour < 12:
                context["time_context"] = "morning"
                print("🌅 Agent: Good morning! I've updated my context for the day.")
            elif 12 <= hour < 18:
                context["time_context"] = "afternoon"
                print("☀️ Agent: Afternoon mode - I'm ready to help with your tasks.")
            elif 18 <= hour < 22:
                context["time_context"] = "evening"
                print("🌆 Agent: Evening mode - time to wind down and reflect.")
            else:
                context["time_context"] = "night"
                print("🌙 Agent: Night mode - quiet assistance available.")
            
            context["last_time_check"] = time.time()
        
        # Action 2: Agent proactively suggests actions based on context
        if context.get("time_context") == "morning" and not context.get("morning_suggestions_given"):
            print("💡 Agent: Since it's morning, I could help you plan your day or check the weather for your commute.")
            context["morning_suggestions_given"] = True
        
        # Action 3: Agent proactively gathers information
        if not context.get("environmental_data") or time.time() - context.get("last_env_check", 0) > 600:
            print("🔍 Agent: I'm gathering some environmental data to better assist you...")
            # This is where the agent would use tools autonomously
            context["last_env_check"] = time.time()
    
    def stop_autonomous_mode(self):
        """Stop autonomous mode"""
        self.running = False
        print("🤖 Agent stopping autonomous monitoring...")
    
    def stream_response(self, user_input: str):
        """Stream the agent's response with autonomous behavior"""
        print("�� Agent:", end=" ")
        
        # Update current task
        self.state["current_task"] = "processing_user_input"
        
        # Process through graph
        for event in self.graph.stream({
            "messages": [{"role": "user", "content": user_input}],
            "context": self.state["context"],
            "goals": self.state["goals"],
            "current_task": self.state["current_task"],
            "system_status": self.state["system_status"],
            "autonomous_actions": []
        }):
            for value in event.values():
                if "messages" in value and value["messages"]:
                    print(value["messages"][-1].content, end="")
                
                # Update state from response
                if "context" in value:
                    self.state["context"] = value["context"]
                if "current_task" in value:
                    self.state["current_task"] = value["current_task"]
                if "system_status" in value:
                    self.state["system_status"] = value["system_status"]
                if "autonomous_actions" in value:
                    self.state["autonomous_actions"] = value["autonomous_actions"]
        
        print()  # New line after response
        
        # Update current task
        self.state["current_task"] = "idle"
    
    def get_agent_status(self):
        """Get current agent status and context"""
        return {
            "goals": self.state["goals"],
            "current_task": self.state["current_task"],
            "system_status": self.state["system_status"],
            "context": self.state["context"],
            "autonomous_mode": self.running,
            "autonomous_actions": self.state["autonomous_actions"]
        }
    
    def set_goal(self, new_goal: str):
        """Add a new goal for the agent"""
        self.state["goals"].append(new_goal)
        print(f"🎯 Agent: New goal added: {new_goal}")
    
    def get_context_summary(self):
        """Get a summary of current context"""
        context = self.state["context"]
        summary = f"Current context: {context.get('last_topic', 'general')}"
        if "time_context" in context:
            summary += f", Time context: {context['time_context']}"
        if "autonomous_actions" in context:
            summary += f", Autonomous actions: {context['autonomous_actions']}"
        return summary