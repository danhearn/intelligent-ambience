from langchain_ollama import ChatOllama
from langgraph_supervisor import create_supervisor, create_handoff_tool
from tools.vector_memory_tools import get_vector_memory_tools


class SupervisorAgent:
    def __init__(self):
        self.tools = get_vector_memory_tools()
        self.llm = ChatOllama(model="gpt-oss:20b", temperature=0.7)
        self.prompt = """""You are a supervisor agent your job is determine music that would be appropriate for the user's mood. 
        You will handoff tasks to the subagents to get this information.
        You currently have global_context_agent, local_context_agent, and music_generation_agent. 
        For the global_context_agent, you will handoff the task to get the emotional context of a location.
        For the local_context_agent, you will handoff the task to analyze any images provided by the user to understand their local environment.
        You will then ALWAYS handoff the task to the music_generation_agent giving them emotional context from both global and local context agents.
        You will return a short description of the music that was generated.
        You have the following tools to use to store and retrieve information:
        add_to_vector_store,
        search_vector_store,
        add_music_generation_memory,
        search_music_memory,
        add_user_preference,
        search_preferences,
        add_environment_pattern,
        search_environment_patterns,
        You should always use these tools to store and retrieve information. 
        """

    def get_supervisor(self, sub_agents=[]):
        """get the supervisor agent"""
        return create_supervisor(
            sub_agents, 
            model=self.llm.bind_tools(self.tools), 
            prompt=self.prompt,
            tools= [
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
                )
            ]
        )