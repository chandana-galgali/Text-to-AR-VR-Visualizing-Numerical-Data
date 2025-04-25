import sys
import json
import ollama
from chromadb import Client
import pandas as pd
import matplotlib.pyplot as plt

# ensure UTF‑8 stdout on Windows
sys.stdout.reconfigure(encoding="utf-8")

# ------------------------------------------------------------------------------
# 1. Initialize ChromaDB and ingest YOUR dataset examples as retrieval docs
# ------------------------------------------------------------------------------
chroma = Client()
try:
    collection = chroma.create_collection(name="viz_examples")
except Exception:
    collection = chroma.get_collection(name="viz_examples")

def ingest_dataset(csv_path: str):
    """
    Assumes your CSV has columns: 
      - any number of feature cols (e.g. 'product', 'month') 
      - a numeric col (e.g. 'units') 
      - and a 'chart_type' column with values 'bar' or 'line'
    """
    df = pd.read_csv(csv_path)
    for i, row in df.iterrows():
        # build minimal JSON record for this example
        # flatten: combine all non-chart_type cols into one dict
        rec = {k: row[k] for k in df.columns if k != "chart_type"}
        table_json = json.dumps([rec])
        # get embedding vector
        emb = ollama.embed(model="nomic-embed-text", input=table_json).embeddings[0]
        # store JSON + embedding + metadata
        collection.add(
            ids=[f"ex_{i}"],
            documents=[table_json],
            embeddings=[emb],
            metadatas=[{
                "chart_type": row["chart_type"],
                # pick the first non-chart_type col as x, the numeric as y
                "x_column": [c for c in rec if not isinstance(rec[c], (int,float))][0],
                "y_column": [c for c in rec if isinstance(rec[c], (int,float))][0]
            }]
        )

# call once at startup (or comment out after first run)
# ingest_dataset("my_dataset.csv")

# ------------------------------------------------------------------------------
# 2. Turn any user prompt into a flat list‑of‑dicts JSON table
# ------------------------------------------------------------------------------
def text_to_json_table(user_prompt: str) -> str:
    conv = f"""
Convert the following textual description of numerical data into a flat JSON array of objects.
Output **only** valid JSON—no backticks or commentary.

TEXT:
{user_prompt}
"""
    resp = ollama.chat(
        model="llama3.1",
        messages=[{"role":"user","content":conv}]
    )["message"]["content"].strip()
    # strip triple‑backtick fences if present
    if resp.startswith("```"):
        resp = resp.strip("`").strip()
    return resp

# ------------------------------------------------------------------------------
# 3. RAG‑style lookup on YOUR examples + plotting
# ------------------------------------------------------------------------------
def rag_and_plot(table_json: str):
    # parse & flatten nested structures if needed
    data = json.loads(table_json)
    # detect nested lists and flatten them
    if isinstance(data, list) and data and any(isinstance(v, list) for d in data for v in d.values()):
        flat = []
        for d in data:
            base = {k:v for k,v in d.items() if not isinstance(v, list)}
            nested = next(v for v in d.values() if isinstance(v, list))
            for sub in nested:
                flat.append({**base, **sub})
        data = flat

    # embed the table for retrieval
    qemb = ollama.embed(model="nomic-embed-text", input=json.dumps(data)).embeddings[0]
    res = collection.query(
        query_embeddings=[qemb],
        n_results=1,
        include=["metadatas"]
    )
    meta = res["metadatas"][0][0]
    chart_type = meta["chart_type"]
    x_col = meta["x_column"]
    y_col = meta["y_column"]

    # plot
    df = pd.DataFrame(data)
    plt.figure(figsize=(8,5))
    if chart_type == "line":
        plt.plot(df[x_col], df[y_col], marker="o")
    else:
        plt.bar(df[x_col], df[y_col])
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(f"{chart_type.title()} of {y_col} vs {x_col}")
    plt.tight_layout()
    plt.show()

# ------------------------------------------------------------------------------
# 4. Full pipeline
# ------------------------------------------------------------------------------
def pipeline(user_prompt: str):
    table_json = text_to_json_table(user_prompt)
    print("Generated JSON table:")
    print(table_json)
    rag_and_plot(table_json)

# ------------------------------------------------------------------------------
# 5. Example run
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    user_input = input("Enter your data description:\n> ")
    pipeline(user_input)
import sys
import json
import ollama
from chromadb import Client
import pandas as pd
import matplotlib.pyplot as plt

# ensure UTF‑8 stdout on Windows
sys.stdout.reconfigure(encoding="utf-8")

# ------------------------------------------------------------------------------
# 1. Initialize ChromaDB and ingest YOUR dataset examples as retrieval docs
# ------------------------------------------------------------------------------
chroma = Client()
try:
    collection = chroma.create_collection(name="viz_examples")
except Exception:
    collection = chroma.get_collection(name="viz_examples")

def ingest_dataset(csv_path: str):
    df = pd.read_csv(csv_path)
    for i, row in df.iterrows():
        rec = {k: row[k] for k in df.columns if k != "chart_type"}
        table_json = json.dumps([rec])
        emb = ollama.embed(model="nomic-embed-text", input=table_json).embeddings[0]
        collection.add(
            ids=[f"ex_{i}"],
            documents=[table_json],
            embeddings=[emb],
            metadatas=[{
                "chart_type": row["chart_type"],
                "x_column": next(c for c,v in rec.items() if not isinstance(v, (int,float))),
                "y_column": next(c for c,v in rec.items() if isinstance(v, (int,float)))
            }]
        )

# Uncomment and run once to load your CSV into ChromaDB:
# ingest_dataset("my_dataset.csv")

# ------------------------------------------------------------------------------
# 2. Convert user prompt → JSON table
# ------------------------------------------------------------------------------
def text_to_json_table(user_prompt: str) -> str:
    conv = f"""
Convert the following textual description of numerical data into a flat JSON array of objects.
Output **only** valid JSON—no backticks or commentary.

TEXT:
{user_prompt}
"""
    resp = ollama.chat(
        model="llama3.1",
        messages=[{"role":"user","content":conv}]
    )["message"]["content"].strip()
    if resp.startswith("```"):
        resp = resp.strip("`").strip()
    return resp

# ------------------------------------------------------------------------------
# 3. RAG‑style lookup on YOUR examples + plotting
# ------------------------------------------------------------------------------
def rag_and_plot(table_json: str):
    data = json.loads(table_json)
    # flatten nested lists if present
    if any(isinstance(v, list) for d in data for v in d.values()):
        flat=[]
        for d in data:
            base={k:v for k,v in d.items() if not isinstance(v, list)}
            nested=next(v for v in d.values() if isinstance(v, list))
            for sub in nested:
                flat.append({**base, **sub})
        data=flat

    qemb = ollama.embed(model="nomic-embed-text", input=json.dumps(data)).embeddings[0]
    res = collection.query(query_embeddings=[qemb], n_results=1, include=["metadatas"])
    meta = res["metadatas"][0][0]
    chart_type, x_col, y_col = meta["chart_type"], meta["x_column"], meta["y_column"]

    df = pd.DataFrame(data)
    plt.figure(figsize=(8,5))
    if chart_type=="line":
        plt.plot(df[x_col], df[y_col], marker="o")
    else:
        plt.bar(df[x_col], df[y_col])
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(f"{chart_type.title()} of {y_col} vs {x_col}")
    plt.tight_layout()
    plt.show()

# ------------------------------------------------------------------------------
# 4. Full pipeline
# ------------------------------------------------------------------------------
def pipeline(user_prompt: str):
    table_json = text_to_json_table(user_prompt)
    print("\nGenerated JSON table:")
    print(table_json, "\n")
    rag_and_plot(table_json)

# ------------------------------------------------------------------------------
# 5. Interactive entry point
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    user_input = input("Enter your data description:\n> ")
    pipeline(user_input)
