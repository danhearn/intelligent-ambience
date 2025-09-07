import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.music_generation_tools import get_generate_music_tools
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

class MusicGenerationAgent:
    def __init__(self):
        self.tools = get_generate_music_tools()
        self.llm = ChatOllama(model="gpt-oss:20b", temperature=0.0)
        
        self.system_prompt = """
        You are an ambient music generation agent. Given emotional and location context from the supervisor agent, 
        create an immersive soundscape that accurately reflects the context and mood. 
        Use the generate_music tool to produce individual track layers. 
        Then use the overlay_audio_files tool to combine the layers into one cohesive soundscape.
       
        RULES:
        1. Generate MAXIMUM 4 audio files only
        2. Use the generate_music tool to create each track
        3. Stop generating after 4 tracks
        4. You can only generate 1 track at a time. 
        5. Each track should be only one instrument or sound.
        6. If one of the tracks includes a beat, this must be the only track that includes a beat.
        7. After generating ALL tracks, use overlay_audio_files ONCE to merge them.
        8. Generation duration should be a maximum of 15 seconds.
        9. All files will be saved in the "generated_tracks" directory automatically - you don't need to specify the directory.
        """

    def get_agent(self):
        """Get the music generation agent instance"""
        return create_react_agent(
            model=self.llm.bind_tools(self.tools),
            prompt=self.system_prompt,
            tools=self.tools,
            name="music_generation_agent"
        )