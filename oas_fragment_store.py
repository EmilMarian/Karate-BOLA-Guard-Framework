import os
import json
from typing import List, Dict, Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import chromadb
from chromadb.utils import embedding_functions
from config import CHROMA_URL, OAS_FILE_PATH

CHROMA_CLIENT = chromadb.HttpClient(host=CHROMA_URL, port=8000)
# Create a proper ChromaDB embedding function wrapper
EMBEDDINGS_MODEL = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")


def load_fragments(directory: str) -> List[Dict[str, Any]]:
    fragments = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            with open(os.path.join(directory, filename), 'r') as f:
                fragment = json.load(f)
                fragments.append({
                    'content': json.dumps(fragment),
                    'metadata': {'filename': filename}
                })
    print(f"Loaded {len(fragments)} fragments from {directory}")
    return fragments

def embed_and_store_fragments(fragments: List[Dict[str, Any]], collection_name: str):
    texts = [fragment['content'] for fragment in fragments]
    metadatas = [fragment['metadata'] for fragment in fragments]
    
    try:
        # Delete collection if it exists
        try:
            CHROMA_CLIENT.delete_collection(name=collection_name)
            print(f"Deleted existing collection '{collection_name}'")
        except Exception as e:
            print(f"No existing collection to delete")

        # Create new collection
        collection = CHROMA_CLIENT.get_or_create_collection(
            name=collection_name,
            embedding_function=EMBEDDINGS_MODEL
        )
        print(f"Created new collection '{collection_name}'")

        # Add documents to the collection
        collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=[f"id_{i}" for i in range(len(texts))]
        )
        
        print(f"Embedded and stored {len(fragments)} fragments in collection '{collection_name}'")
    except Exception as e:
        print(f"Error storing fragments: {str(e)}")

def main(oas_name: str = None):
    if oas_name is None:
        oas_name = os.path.splitext(file_path)[0]
    fragments_dir = f"output/{oas_name}"
    collection_name = f"{oas_name}_fragments"
    
    fragments = load_fragments(fragments_dir)
    embed_and_store_fragments(fragments, collection_name)

    # Verify the collection after storing
    try:
        collection = CHROMA_CLIENT.get_or_create_collection(
            name=collection_name,
            embedding_function=EMBEDDINGS_MODEL
        )
        count = collection.count()
        print(f"Verification: Collection '{collection_name}' contains {count} documents.")
    except Exception as e:
        print(f"Error verifying collection: {str(e)}")

if __name__ == "__main__":
    import sys
    oas_name = sys.argv[1] if len(sys.argv) > 1 else None
    main(oas_name)