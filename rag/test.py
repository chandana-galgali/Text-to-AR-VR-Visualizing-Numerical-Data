import pandas as pd
import json
from sentence_transformers import SentenceTransformer  # Using SentenceTransformers for local embeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI  # Updated import for ChatOpenAI

# Load the custom dataset
custom_dataset_path = r'C:\Users\Prachi\OneDrive\Documents\mini project ty\Text-to-VR-Visualizing-Numerical-Data\rag\rag_training_data.xlsx'  # Update with the actual path
custom_dataset = pd.read_excel(custom_dataset_path)

# Convert the 'Table' column from string format to JSON (list of dictionaries)
def convert_to_json(table_str):
    try:
        return json.loads(table_str.replace("\n", "").replace("\r", ""))
    except json.JSONDecodeError:
        return None

# Apply the conversion to the 'Table' column
custom_dataset['Table'] = custom_dataset['Table'].apply(convert_to_json)

# Create a list of documents from the dataset (table rows and visualisation type)
docs = []
for _, row in custom_dataset.iterrows():
    table_repr = json.dumps(row['Table'])  # Use table as the content for similarity comparison
    docs.append(
        Document(
            page_content=table_repr,
            metadata={"chart": row['Visualisation Type']}
        )
    )

# Use SentenceTransformer for embeddings
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # You can change this to any other pre-trained model from HuggingFace
# Create the FAISS index using the SentenceTransformer model directly
vectorstore = FAISS.from_documents(docs, model)  # Pass the model directly here

# Set up the RAG prompt template for chart selection
chart_prompt = PromptTemplate(
    template=(
      "Given this JSON table:\n{query}\n\n"
      "And these similar examples:\n{context}\n\n"
      "Which chart type is most appropriate? Answer only 'bar' or 'line'."
    ),
    input_variables=["query", "context"]
)

# Set up the RAG chain using the FAISS retriever
chart_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0),  # Adjust the model if needed
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    chain_type="stuff",
    return_source_documents=False,
    chain_type_kwargs={"prompt": chart_prompt}
)

# Function to run the RAG model and predict the chart type
def predict_chart_type(table):
    table_json = json.dumps(table["rows"], ensure_ascii=False)  # Convert table rows to JSON string
    result = chart_chain.run({
        "query": table_json,  # The LLM-generated table (as JSON)
        "context": json.dumps(example_tables)  # The example tables (as context)
    })
    return result

# Example: Predicting chart type for a table
user_generated_table = {"columns": ["Year", "Revenue"], "rows": [[2018, 50], [2019, 65], [2020, 80], [2021, 95]]}
chart_type = predict_chart_type(user_generated_table)

print("Recommended chart type:", chart_type)
