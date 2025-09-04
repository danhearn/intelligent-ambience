from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing import Annotated
from typing_extensions import TypedDict
from tools.custom_tools import get_tools

class State(TypedDict):
    messages: Annotated[list, add_messages]

class ChatbotAgent:
    def __init__(self):
        self.tools = get_tools()
        self.llm = ChatOllama(
            model="gpt-oss:20b",
            temperature=0
        ).bind_tools(self.tools)
        
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        graph_builder = StateGraph(State)
        
        # Add the chatbot node
        def chatbot(state: State):
            return {"messages": [self.llm.invoke(state["messages"])]}
        
        graph_builder.add_node("chatbot", chatbot)
        
        # Add the tools node
        tool_node = ToolNode(tools=self.tools)
        graph_builder.add_node("tools", tool_node)
        
        # Add conditional edges
        graph_builder.add_conditional_edges(
            "chatbot",
            tools_condition,
        )
        
        # Add regular edges
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.add_edge(START, "chatbot")
        
        return graph_builder.compile()
    
    def stream_response(self, user_input: str):
        """Stream the agent's response"""
        print("Assistant:", end=" ")
        for event in self.graph.stream({"messages": [{"role": "user", "content": user_input}]}):
            for value in event.values():
                if "messages" in value and value["messages"]:
                    print(value["messages"][-1].content, end="")
        print()  # New line after response