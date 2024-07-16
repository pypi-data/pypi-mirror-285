"""
Example of custom graph using Gemini Google model
"""

import os
from dotenv import load_dotenv
from scrapegraphai.models import Gemini
from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import FetchNode, ParseNode, RAGNode, GenerateAnswerNode
load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

deepseek_key = os.getenv("DEEPSEEK_APIKEY")

graph_config = {
    "llm": {
        "model": "deepseek-chat",
        "openai_api_key": deepseek_key,
        "openai_api_base": 'https://api.deepseek.com/v1',
    },
     "embeddings": {
        "model": "ollama/nomic-embed-text",
        "temperature": 0,
        # "base_url": "http://localhost:11434",  # set ollama URL arbitrarily
    },
    "verbose": True,
}

# ************************************************
# Define the graph nodes
# ************************************************

llm_model = Gemini(graph_config["llm"])

# define the nodes for the graph
fetch_node = FetchNode(
    input="url | local_dir",
    output=["doc"],
)
parse_node = ParseNode(
    input="doc",
    output=["parsed_doc"],
    node_config={"chunk_size": 4096}
)
rag_node = RAGNode(
    input="user_prompt & (parsed_doc | doc)",
    output=["relevant_chunks"],
    node_config={"llm": llm_model},
)
generate_answer_node = GenerateAnswerNode(
    input="user_prompt & (relevant_chunks | parsed_doc | doc)",
    output=["answer"],
    node_config={"llm": llm_model},
)

# ************************************************
# Create the graph by defining the connections
# ************************************************

graph = BaseGraph(
    nodes={
        fetch_node,
        parse_node,
        rag_node,
        generate_answer_node,
    },
    edges={
        (fetch_node, parse_node),
        (parse_node, rag_node),
        (rag_node, generate_answer_node)
    },
    entry_point=fetch_node
)

# ************************************************
# Execute the graph
# ************************************************

result, execution_info = graph.execute({
    "user_prompt": "List me the projects with their description",
    "url": "https://perinim.github.io/projects/"
})

# get the answer from the result
result = result.get("answer", "No answer found.")
print(result)
