from datetime import datetime
import time
import os
import requests
from typing import List, Dict
import chromadb
import json

from langfuse import Langfuse
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from config import LANGFUSE_URL, OUTPUT_LOG, OUTPUT_DIR, OPEN_LLM_URL, LANGUAGE_MODEL, TRACE_ID, CHROMA_URL, langfuse, TEST_CASE_NUMBER, configure_logging

# Configure logging and get the log object
log = configure_logging(__name__)

CHROMA_CLIENT = chromadb.HttpClient(host=CHROMA_URL, port=8000)
EMBEDDINGS = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
BOLA_COLLECTION = "bola_kb"

def get_relevant_examples(feature_content: str, k: int = 3) -> list:
    log.info(f"Getting relevant examples for: {feature_content[:50]}...")
    from config import SESSION_ID

    trace = langfuse.trace(
        session_id = SESSION_ID,
        id = TRACE_ID
    )
    span = trace.span(
        name="embedding-search",
        metadata={"database": "chroma"},
        input = {'query': feature_content},
    )
    collection = Chroma(client=CHROMA_CLIENT, collection_name=BOLA_COLLECTION, embedding_function=EMBEDDINGS)
    results = collection.similarity_search(feature_content, k=k)
    span.end(
        output=results
    );
    log.info(f"Found {len(results)} relevant examples.")
    return [doc.page_content for doc in results]

def generate_karate_test(prompt: str, max_tokens: int = 1000) -> str:
    from config import SESSION_ID
    log.info(f"Generating Karate test for prompt: {prompt[:50]}...")

    trace = langfuse.trace(
        session_id = SESSION_ID,
        id = TRACE_ID
    )
    generation = trace.generation(
        session_id = SESSION_ID,
        input = prompt,
        name="initial-test-generation",
        model=LANGUAGE_MODEL,
        model_parameters={"maxTokens": max_tokens, "temperature": "0.3"},
    )
    span = trace.span(
        name="generate initial test case"
    )
    context = get_relevant_examples(prompt)
    enhanced_prompt = f"Context:\n{context}\n\nTask: {prompt}"
    messages = [
        {"role": "system", "content": "You are a security testing expert who generates Karate DSL test scripts."},
        {"role": "user", "content": enhanced_prompt}
    ]
    
    payload = {
        "temperature": 0.3,
        "model": LANGUAGE_MODEL,
        "max_tokens": max_tokens,
        "messages": messages
    }
    span.update(input = payload)

    try:
        log.info(f"Sending request to {OPEN_LLM_URL}")
        start_time = time.time()
        response = requests.post(OPEN_LLM_URL, json=payload)
        end_time = time.time()
        log.info(f"Response status code: {response.status_code}")
        response_json = response.json()
        
        # Check for validation errors in the response
        if 'errors' in response_json:
            error_messages = response_json['errors']
            raise ValueError(f"Validation errors occurred: {error_messages}")

        result = response_json['choices'][0]['message']['content']
        output_completion = response_json['usage']['completion_tokens']
        input_prompt = response_json['usage']['prompt_tokens']
        
        generation.update(
            start_time=start_time,
            end_time=end_time,
        )

        generation.end(
            output=result,
            usage={"input": input_prompt, "output": output_completion, "unit": "TOKENS"}
        )
        
        span.update(output = result)

        log.info(f"Generated test case: {result[:100]}...")
        return result.strip()
    except Exception as e:
        error_message = f"An error occurred while generating the Karate test: {str(e)}"
        log.error(f"Error: {error_message}")
        span.update(output = error_message)
        return error_message

def main():
    log.info("Starting main function...")
    sample_prompt = "Generate a Karate DSL test script for testing the login functionality of a web application."
    result = generate_karate_test(sample_prompt)
    log.info("Final result:")
    log.info(result)

if __name__ == "__main__":
    main()