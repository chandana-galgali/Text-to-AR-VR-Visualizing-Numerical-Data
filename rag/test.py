import time
import openai

def get_embeddings_with_retry(texts, retries=3, delay=5):
    for attempt in range(retries):
        try:
            # Your embedding request
            embeddings = OpenAIEmbeddings(openai_api_key="ssk-1234abcd5678efgh1234abcd5678efgh1234abcd")
            return embeddings.embed_documents(texts)  # Example of the embedding request
        except openai.error.RateLimitError as e:
            print(f"Rate limit error: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)  # Wait before retrying
        except Exception as e:
            print(f"Error occurred: {e}")
            break
    return None

# Call the function to get embeddings with retry
texts = ["Example text"]
embeddings = get_embeddings_with_retry(texts)
