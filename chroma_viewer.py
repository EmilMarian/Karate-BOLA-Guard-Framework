import chromadb
import json
import sys  # Import sys to handle command line arguments
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from chromadb.utils import embedding_functions

from config import CHROMA_URL
# Initialize the ChromaDB client
CHROMA_CLIENT = chromadb.HttpClient(host=CHROMA_URL, port=8000)
# Create a proper ChromaDB embedding function wrapper
EMBEDDINGS_MODEL = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

def view_fragments(collection_name, n=5, q=""):
    # Get the collection
    collection = CHROMA_CLIENT.get_or_create_collection(
            name=collection_name,
            embedding_function=EMBEDDINGS_MODEL
        )

    # Query the collection
    results = collection.query(
        query_texts=[q],
        n_results=n,
        include=["documents", "metadatas"]
    )
    
    # Display the results
    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
        print(f"\nFragment {i}:")
        print(f"Metadata: {json.dumps(metadata, indent=2)}")
        print(f"Content: {doc}")
        print("-" * 50)

# Add a main function to run the script from the terminal
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 chroma_viewer.py oas_medium [n_results]")
        sys.exit(1)
    
    collection_name = sys.argv[1]
    n_results = int(sys.argv[2]) if len(sys.argv) > 2 else 5  # Default to 5 if not provided
    # query = sys.argv[2]
    view_fragments(collection_name, n_results, "user")