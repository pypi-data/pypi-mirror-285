"""
Module for making the tests for ScriptGeneratorGraph
"""
import pytest
from scrapegraphai.graphs import ScriptCreatorGraph
from scrapegraphai.utils import prettify_exec_info

@pytest.fixture
def graph_config():
   """
   Configuration of the graph
   """
   return {
       "llm": {
           "model": "ollama/mistral",
           "temperature": 0,
           "format": "json",
           "base_url": "http://localhost:11434",
           "library": "beautifulsoup",
       },
       "embeddings": {
           "model": "ollama/nomic-embed-text",
           "temperature": 0,
           "base_url": "http://localhost:11434",
       },
       "library": "beautifulsoup"
   }

def test_script_creator_graph(graph_config: dict):
   """
   Test the ScriptCreatorGraph
   """
   smart_scraper_graph = ScriptCreatorGraph(
       prompt="List me all the news with their description.",
       source="https://perinim.github.io/projects",
       config=graph_config
   )
   result = smart_scraper_graph.run()
   assert result is not None, "ScriptCreatorGraph execution failed to produce a result."
