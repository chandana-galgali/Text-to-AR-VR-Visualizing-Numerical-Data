import sys
import json
import ollama
from chromadb import Client
import pandas as pd
import matplotlib.pyplot as plt

# ---- ensure UTF‑8 stdout on Windows ----
sys.stdout.reconfigure(encoding="utf-8")

# ---- 1. Init ChromaDB collection for chart‐type examples ----
chroma = Client()
try:
    collection = chroma.create_collection(name="chart_type_examples")
except:
    collection = chroma.get_collection(name="chart_type_examples")

# ---- 2. Ingest only chart‐type metadata from your Dataset.xlsx ----
def ingest_dataset(excel_path: str):
    """
    Reads Dataset.xlsx with columns:
      - 'Table' (JSON array string)
      - 'Visualisation Type' ('Bar' or 'Line')
    and stores each row’s JSON + chart_type metadata.
    """
    df = pd.read_excel(excel_path)
    for idx, row in df.iterrows():
        table_json = row["Table"].strip()
        emb = ollama.embed(
            model="nomic-embed-text",
            input=table_json
        ).embeddings[0]
        collection.add(
            ids=[f"ex_{idx}"],
            documents=[table_json],
            embeddings=[emb],
            metadatas=[{"chart_type": row["Visualisation Type"].lower()}]
        )

# Run once to populate ChromaDB, then comment out on future runs:
ingest_dataset("C:/Users/Prachi/OneDrive/Documents/mini project ty/Text-to-VR-Visualizing-Numerical-Data/rag/rag_training_data.xlsx")


# ---- 3. Given JSON → retrieve chart_type via RAG, then ask LLM for axes, then plot ----
def rag_and_plot(table_json: str):
    # parse
    data = json.loads(table_json)

    # 3a) embed & retrieve nearest example’s chart_type
    qemb = ollama.embed(
        model="nomic-embed-text",
        input=json.dumps(data)
    ).embeddings[0]
    res = collection.query(
        query_embeddings=[qemb],
        n_results=1,
        include=["metadatas"]
    )
    chart_type = res["metadatas"][0][0]["chart_type"]

    # 3b) ask LLM to choose axes
    axes_prompt = f"""
Given this JSON array of objects:
{table_json}

You should plot a '{chart_type}' chart.
Reply ONLY with JSON:
{{
  "x_column": "name_of_column",
  "y_column": "name_of_column"
}}
"""
    chat = ollama.chat(
        model="llama3.1",
        messages=[{"role": "user", "content": axes_prompt}]
    )
    axes = json.loads(chat["message"]["content"].strip())

    # 3c) render with matplotlib
    df = pd.DataFrame(data)
    plt.figure(figsize=(8,5))
    x, y = axes["x_column"], axes["y_column"]
    if chart_type == "line":
        plt.plot(df[x], df[y], marker="o")
    else:
        plt.bar(df[x], df[y])
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(f"{chart_type.title()} of {y} vs {x}")
    plt.tight_layout()
    plt.show()

# ---- 4. Interactive entry point taking raw JSON from user ----
def pipeline_json():
    print("Paste your JSON array of objects (e.g. [{\"month\":\"Jan\",\"sales\":100},…]):")
    raw = []
    while True:
        line = input()
        if not line.strip():
            break
        raw.append(line)
    table_json = "\n".join(raw).strip()
    # echo and plot
    print("\nReceived JSON table:\n", table_json, "\n")
    rag_and_plot(table_json)

if __name__ == "__main__":
    pipeline_json()
