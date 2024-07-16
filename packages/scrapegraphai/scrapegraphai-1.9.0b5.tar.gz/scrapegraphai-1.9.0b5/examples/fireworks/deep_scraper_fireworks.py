""" 
Basic example of scraping pipeline using SmartScraper
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import DeepScraperGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

fireworks_api_key = os.getenv("FIREWORKS_APIKEY")

graph_config = {
    "llm": {
        "api_key": fireworks_api_key,
        "model": "fireworks/accounts/fireworks/models/mixtral-8x7b-instruct"
    },
     "embeddings": {
        "model": "ollama/nomic-embed-text",
        "temperature": 0,
        # "base_url": "http://localhost:11434",  # set ollama URL arbitrarily
    },
    "verbose": True,
    "max_depth": 1
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

deep_scraper_graph = DeepScraperGraph(
    prompt="List me all the job titles and detailed job description.",
    # also accepts a string with the already downloaded HTML code
    source="https://www.google.com/about/careers/applications/jobs/results/?location=Bangalore%20India",
    config=graph_config
)

result = deep_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = deep_scraper_graph.get_execution_info()
print(deep_scraper_graph.get_state("relevant_links"))
print(prettify_exec_info(graph_exec_info))