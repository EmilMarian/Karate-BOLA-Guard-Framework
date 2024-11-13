import os
import json
from typing import List, Dict, Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from chromadb import Client, Settings
from config import CHROMA_URL


CHROMA_CLIENT = Client(Settings(chroma_server_host=CHROMA_URL, chroma_server_http_port="8000"))
EMBEDDINGS = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

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
    return fragments

def embed_and_store_fragments(fragments: List[Dict[str, Any]], collection_name: str):
    texts = [fragment['content'] for fragment in fragments]
    metadatas = [fragment['metadata'] for fragment in fragments]
    
    collection = Chroma.from_texts(
        texts=texts,
        embedding=EMBEDDINGS,
        metadatas=metadatas,
        collection_name=collection_name,
        client=CHROMA_CLIENT
    )
    
    print(f"Embedded and stored {len(fragments)} fragments in collection '{collection_name}'")