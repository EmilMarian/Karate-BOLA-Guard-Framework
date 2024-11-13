import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from chromadb.utils import embedding_functions

from typing import List, Dict, Any
from config import CHROMA_URL

# EMBEDDINGS = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
EMBEDDINGS = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

class OASFragmentRetriever:
    def __init__(self, collection_name: str):
        self.client = chromadb.HttpClient(host=CHROMA_URL, port=8000)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=EMBEDDINGS
        )

    def retrieve_fragments(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=['documents', 'metadatas']
        )

        fragments = []
        for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
            fragments.append({
                'content': doc,
                'metadata': metadata
            })

        return fragments