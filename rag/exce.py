import pandas as pd
import numpy as np
import faiss
import json
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load your dataset
file_path = 'C:/Users/Prachi/OneDrive/Desktop/rag/rag_training_data.xlsx'
df = pd.read_excel(file_path)

# Step 1: Generate Embeddings for Descriptions using Sentence-BERT
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Generate embeddings for the descriptions
descriptions = df['Description'].tolist()
description_embeddings = model.encode(descriptions)

# Convert embeddings to float32 as FAISS requires this format
description_embeddings = np.array(description_embeddings).astype('float32')

# Step 2: Build FAISS Index
faiss_index = faiss.IndexFlatL2(description_embeddings.shape[1])  # L2 distance for similarity search
faiss_index.add(description_embeddings)  # Add embeddings to the index

# Step 3: Retrieve relevant description for the user's query
def retrieve_relevant_description(query):
    # Convert the query into an embedding
    query_embedding = model.encode([query])
    
    # Search for the closest match using FAISS
    D, I = faiss_index.search(np.array(query_embedding).astype('float32'), k=1)  # Retrieve top 1 match
    
    # Get the most relevant description from the dataset
    relevant_description = descriptions[I[0][0]]
    return relevant_description, I[0][0]

# Step 4: Extract Visualization Type and Scale Information
def extract_visualization_info(index):
    # Get the row based on the index
    row = df.iloc[index]
    
    # Extract chart type and scale
    vis_type = row['Visualisation Type']
    scale = row['Scale']
    
    return vis_type, scale

# Step 5: Generate Visualization based on Chart Type and Scale
def generate_visualization(index, vis_type, scale):
    # Extract relevant data from the "Table" column (in JSON format)
    data = json.loads(df.loc[index, 'Table'])
    x_values = [entry[list(entry.keys())[0]] for entry in data]
    y_values = [entry[list(entry.keys())[1]] for entry in data]
    
    # Apply the scale (for demonstration purposes, we won't perform complex scale conversion here)
    print(f"Scale Info: {scale}")
    
    # Create a Bar or Line chart based on the Visualisation Type
    plt.figure(figsize=(8, 6))
    if vis_type.lower() == 'line':
        plt.plot(x_values, y_values, marker='o')
        plt.title("Line Chart")
    elif vis_type.lower() == 'bar':
        plt.bar(x_values, y_values)
        plt.title("Bar Chart")
    
    # Add labels and show the chart
    plt.xlabel(df.loc[index, 'X-Axis Label'])
    plt.ylabel(df.loc[index, 'Y-Axis Label'])
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# Step 6: Combine Everything into a User Query Process
def process_query():
    # Take the user's query as input
    query = input("Please enter your query: ")

    # Step 6.1: Retrieve the most relevant description
    relevant_description, index = retrieve_relevant_description(query)
    print("Relevant Description:", relevant_description)

    # Step 6.2: Extract the visualization type and scale for the relevant description
    vis_type, scale = extract_visualization_info(index)
    print(f"Visualization Type: {vis_type}")
    print(f"Scale: {scale}")

    # Step 6.3: Generate the corresponding visualization
    generate_visualization(index, vis_type, scale)

# Run the process_query function to interact with the user
process_query()
