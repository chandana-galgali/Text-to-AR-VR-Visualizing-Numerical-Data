import json
import ollama
from chromadb import Client
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------------------------
# 1. Init ChromaDB vector store & ingest visualization‐rules
# ------------------------------------------------------------------------------
chroma = Client()
try:
    collection = chroma.create_collection(name="viz_guidelines")
except Exception:
    collection = chroma.get_collection(name="viz_guidelines")

guidelines = [
    "If the table’s first column is a date or time series, use a line chart.",
    "If the table has discrete categories with numeric values, use a bar chart.",
    "If there are more than 10 categories, consider grouping or using a bar chart."
]

for idx, rule in enumerate(guidelines):
    resp = ollama.embed(model="nomic-embed-text", input=rule)
    emb = resp.embeddings[0]
    collection.add(ids=[f"rule_{idx}"], documents=[rule], embeddings=[emb])

# ------------------------------------------------------------------------------
# 2. Convert user prompt → JSON table
# ------------------------------------------------------------------------------
def text_to_json_table(user_prompt: str) -> str:
    """
    Uses the LLM to turn a textual description into a JSON array of objects.
    """
    conv_prompt = f"""
Convert the following textual description of numerical data into a JSON array of objects.
Output **only** valid JSON—no commentary.

TEXT:
{user_prompt}
"""
    chat = ollama.chat(
        model="llama3.1",
        messages=[{"role":"user","content":conv_prompt}]
    )
    return chat["message"]["content"].strip()

# ------------------------------------------------------------------------------
# 3. RAG + chart‐creation
# ------------------------------------------------------------------------------
def rag_and_plot(table_json: str):
    # a) Retrieve best guideline
    query = f"Which chart type for this data? {table_json}"
    qresp = ollama.embed(model="nomic-embed-text", input=query)
    qvec  = qresp.embeddings[0]
    res   = collection.query(query_embeddings=[qvec], n_results=1)
    guideline = res["documents"][0][0]

    # b) Ask LLM for chart decision
    decision_prompt = f"""
You are given this guideline:
“{guideline}”

And this table in JSON:
{table_json}

Reply **ONLY** with JSON:
{{
  "chart_type": "<bar|line>",
  "x_column": "name_of_column",
  "y_column": "name_of_column"
}}
"""
    chat    = ollama.chat(
        model="llama3.1",
        messages=[{"role":"user","content":decision_prompt}]
    )
    decision = json.loads(chat["message"]["content"])

    # c) Plot it
    df = pd.DataFrame(json.loads(table_json))
    plt.figure(figsize=(8,5))
    if decision["chart_type"] == "line":
        plt.plot(df[decision["x_column"]], df[decision["y_column"]], marker="o")
    else:
        plt.bar(df[decision["x_column"]], df[decision["y_column"]])
    plt.xlabel(decision["x_column"])
    plt.ylabel(decision["y_column"])
    plt.title(f"{decision['chart_type'].title()} of {decision['y_column']} vs {decision['x_column']}")
    plt.tight_layout()
    plt.show()

# ------------------------------------------------------------------------------
# 4. End‑to‑end pipeline
# ------------------------------------------------------------------------------
def pipeline(user_prompt: str):
    # 1) Text → JSON table
    table_json = text_to_json_table(user_prompt)
    print(" Generated JSON table:")
    print(table_json)

    # 2) RAG + plot
    rag_and_plot(table_json)

# ------------------------------------------------------------------------------
# 5. Example usage
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    user_input = (
        "In Q1 2025, product A sold 100 units in January, 120 in February, "
        "and 90 in March; product B sold 80, 95, and 110 respectively."
    )
    pipeline(user_input)
