import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.supervisor_agent import SupervisorAgent
from agents.global_context_agent import GlobalContextAgent
from agents.local_context_agent import LocalContextAgent
from agents.music_generation_agent import MusicGenerationAgent

class MainGraph:
    def __init__(self):
        self.supervisor_agent = SupervisorAgent()
        self.global_context_agent = GlobalContextAgent()
        self.local_context_agent = LocalContextAgent()
        self.music_generation_agent = MusicGenerationAgent()
        self.graph = self.supervisor_agent.get_supervisor(
            sub_agents=[self.global_context_agent.get_agent(),
                        self.local_context_agent.get_agent(),
                        self.music_generation_agent.get_agent()
            ]
        ).compile()

    def run(self, query: str, img_url: str):
        inputs = {"messages": [("user", query + " " + img_url)]}
        result = self.graph.invoke(inputs) 
        for m in result["messages"]:
            m.pretty_print()
    
img_url = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/demo.jpg' 

if __name__ == "__main__":
    main_graph = MainGraph()
    main_graph.run("Brighton Beach, UK", img_url=img_url)