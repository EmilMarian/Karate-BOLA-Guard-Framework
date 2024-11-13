import os
import json
import csv
import chromadb
from typing import List, Dict
from langchain_huggingface import HuggingFaceEmbeddings
from chromadb.utils import embedding_functions
from langchain_community.vectorstores import Chroma

# Set up the embedding function
EMBEDDINGS_MODEL = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
CHROMA_CLIENT = chromadb.HttpClient(host="localhost", port=8000)

def scan_for_files(directory: str) -> List[str]:
    file_extensions = ('.txt', '.csv', '.json', '.jsonl', '.log', '.feature')
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(file_extensions):
                files.append(os.path.join(root, filename))
    return files

def parse_file(file_path: str) -> List[Dict[str, str]]:
    _, ext = os.path.splitext(file_path)
    with open(file_path, 'r') as file:
        if ext == '.txt':
            return [{"content": file.read(), "source": file_path}]
        elif ext == '.csv':
            reader = csv.DictReader(file)
            return [{"content": json.dumps(row), "source": file_path} for row in reader]
        elif ext == '.json':
            data = json.load(file)
            return [{"content": json.dumps(data), "source": file_path}]
        elif ext == '.log':
            data = json.load(file)
            return [{"content": json.dumps(data), "source": file_path}]
        elif ext == '.jsonl':
            return [{"content": line.strip(), "source": file_path} for line in file]
        elif ext == '.feature':
            return [{"content": file.read(), "source": file_path}]

def store_in_chroma(documents: List[Dict[str, str]], collection_name: str = "bola_kb"):
    """
    Store documents in ChromaDB with proper error handling and collection management.
    
    Args:
        documents: List of dictionaries containing 'content' and 'source' keys
        collection_name: Name of the ChromaDB collection to store documents in
    """
    try:
        # Prepare texts and metadata
        texts = [doc["content"] for doc in documents]
        metadatas = [{"source": doc["source"]} for doc in documents]
        
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
        
        print(f"Embedded and stored {len(documents)} documents in collection '{collection_name}'")
    except Exception as e:
        print(f"Error storing documents: {str(e)}")

def main():
    current_directory = os.getcwd()
    print(current_directory)
    files = scan_for_files(current_directory)
    
    all_documents = []
    for file in files:
        documents = parse_file(file)
        print(documents)
        all_documents.extend(documents)
    
    store_in_chroma(all_documents, "bola_kb")

if __name__ == "__main__":
    main()