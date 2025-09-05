from langchain_ollama import ChatOllama
from langgraph_supervisor import create_supervisor, create_handoff_tool


class SupervisorAgent:
    def __init__(self):
        self.llm = ChatOllama(model="gpt-oss:20b", temperature=0.7)
        self.prompt = """"
        You are the supervisor agent. Your role is to coordinate subagents so music is generated for the user’s mood and environment.
        
        Subagents:
        global_context_agent: emotional context from location, time, weather, culture.
        local_context_agent: emotional cues from user images (or “no local context available” if none).
        memory_agent: retrieve/store user preferences and past generations.
        music_generation_agent: generate music using context + memory.

        Process (always in order):
        Query global_context_agent.
        Query local_context_agent.
        Query memory_agent: pass retrieved preferences/history forward.
        Always hand off to music_generation_agent with:
        global context
        local context
        memory data
        Store new generation data in memory_agent.

        Rules:
        Never skip or reorder steps.
        Never generate music yourself.
        YOU MUST ALWAYS HANDOFF use the music_generation_agent to generate music.
        Return only a short description of the generated music to the user.
        """

    def get_supervisor(self, sub_agents=[]):
        """get the supervisor agent"""
        return create_supervisor(
            sub_agents, 
            model=self.llm, 
            prompt=self.prompt,
            tools=[
                create_handoff_tool(
                    agent_name="global_context_agent",
                    name="assign_to_global_context_agent",
                    description="An agent that can get the emotional context of a location",
                ),
                create_handoff_tool(
                    agent_name="local_context_agent",
                    name="assign_to_local_context_agent",
                    description="An agent that can analyze images to understand the user's local environment",
                ),
                create_handoff_tool(
                    agent_name="music_generation_agent",
                    name="assign_to_generate_music_agent",
                    description="An agent that can generate music",
                ),
                create_handoff_tool(
                    agent_name="memory_agent",
                    name="assign_to_memory_agent",
                    description="An agent that can store and retrieve information",
                )
            ]
        )