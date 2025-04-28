import ollama
import pandas as pd
from typing import List

# Initialize the Ollama chat model with the model name (replace "llama-2" with the actual model you want to use)
model = ollama.chat(model="llama-2")

# Step 1: Function to Retrieve Relevant Data
def retrieve_data(query: str, dataset: List[str]) -> List[str]:
    """
    Retrieve relevant data based on a simple keyword match.
    In practice, you could use more advanced retrieval techniques such as embeddings.
    """
    relevant_data = [doc for doc in dataset if query.lower() in doc.lower()]
    return relevant_data

# Step 2: Function to Generate Response Using Ollama's Model
def generate_response(retrieved_data: List[str], query: str) -> str:
    """
    Generate a response based on retrieved data and the query.
    The retrieved data is provided as context for the model's generation.
    """
    # Concatenate the retrieved data into a single string
    context = " ".join(retrieved_data)
    
    # Generate the response using Ollama
    prompt = f"Given the following data: {context}, generate a response for the query: {query}"
    response = model(prompt)
    
    return response

# Step 3: Full RAG Model
def rag_model(query: str, dataset: List[str]) -> str:
    """
    Full Retrieval-Augmented Generation (RAG) pipeline:
    1. Retrieve relevant data based on the query
    2. Generate a response using the retrieved data
    """
    # Step 1: Retrieve relevant data
    retrieved_data = retrieve_data(query, dataset)
    
    # If no relevant data is found, handle the case gracefully
    if not retrieved_data:
        return "Sorry, no relevant data found."
    
    # Step 2: Generate a response using Ollama
    response = generate_response(retrieved_data, query)
    return response

# Example dataset (list of documents or statements)
dataset = [
    "Sales increased by 20% in Q1 2025",
    "The average temperature in January was 5°C",
    "In Q2 2025, the company expects a revenue increase of 10%",
    "The company had a revenue growth of 15% in Q3 2024"
]

# Example queries
queries = [
    "What were the sales trends for Q1 2025?",
    "What was the temperature in January?",
    "What is the company's growth expectation for Q2?"
]

# Process each query and generate responses
for query in queries:
    print(f"Query: {query}")
    print(f"Response: {rag_model(query, dataset)}\n")
