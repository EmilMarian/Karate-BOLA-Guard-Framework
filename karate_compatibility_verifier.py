import requests
from datetime import datetime
import time
import os
import chromadb
from langfuse import Langfuse
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from config import SESSION_ID, OUTPUT_LOG, LANGFUSE_URL, OPEN_LLM_URL, KARATE_DSL_COLLECTION, TRACE_ID, LANGUAGE_MODEL, CHROMA_URL, langfuse, configure_logging
import logging

# Configure logging and get the log object
log = configure_logging(__name__)

CHROMA_CLIENT = chromadb.HttpClient(host=CHROMA_URL, port=8000)
EMBEDDINGS = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def get_relevant_examples(feature_content: str, k: int = 3) -> list:
    collection = Chroma(client=CHROMA_CLIENT, collection_name=KARATE_DSL_COLLECTION, embedding_function=EMBEDDINGS)
    results = collection.similarity_search(feature_content, k=k)
    return [doc.page_content for doc in results]

def read_karate_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def call_llm(q_name="Default", messages="Default", trace_id=None, span_id=None):

    trace = langfuse.trace(
        id=TRACE_ID,
        session_id=SESSION_ID
    )
    span_name = q_name
    span = langfuse.span(
        id=span_id,
        trace_id=trace_id,
        name=q_name
    )

    payload = {
        "temperature": 0.3,
        "model": LANGUAGE_MODEL,
        "max_tokens": 1000,
        "messages": messages
    }
    try:
        start_time = time.time()
        response = requests.post(OPEN_LLM_URL, json=payload)
        end_time = time.time()
        response_json = response.json()
        content = response_json['choices'][0]['message']['content']

        span.update(input=payload)
        span.update(output=content)
        
        if trace_id and span_id:
            generation = trace.generation(
                session_id = SESSION_ID,
                trace_id=trace_id,
                parent_id=span_id,
                input=str(messages),
                name=span_name,
                output=content,
                model=LANGUAGE_MODEL,
                model_parameters={"maxTokens": 1000, "temperature": "0.3"},
            )
                    
            generation.update(
                start_time=start_time,
                end_time=end_time,
            )
  
            generation.end(
                usage={
                    "input": len(str(messages)),
                    "output": len(content),
                    "unit":"TOKENS"
                }
            )
        
        return content
    except Exception as e:
        log.error(f"An error occurred while calling the LLM: {str(e)}")
        return None

def verify_karate_compatibility(file_path:str, feature_content: str, trace_id: str, span_id: str) -> str:
    relevant_examples = get_relevant_examples(feature_content)
    
    prompt = f"""
        You are a Karate DSL expert. Your task is to generate or correct Karate DSL test scripts.

        Please adhere to the following guidelines:
        1. Use only valid Karate DSL and Gherkin syntax.
        2. Do not include any explanatory text within the script itself.
        3. Use single quotes for strings.
        4. Use proper Karate DSL methods like 'Given', 'When', 'Then', 'And'.
        5. For HTTP methods, use syntax like 'method POST' instead of descriptive phrases.
        6. Use 'status' to check response codes, e.g., 'Then status 401'.
        7. Include necessary headers and request bodies where appropriate.

        Very important: IF The Karate DSL script provided is already correct and does not require any corrections, just output the same test as it is, without any modifications.

        
        Here are some relevant examples of valid Karate DSL syntax:

        {'-' * 40}
        {'\n'.join(relevant_examples)}
        {'-' * 40}

        Based on these guidelines and examples, please generate or correct the following Karate test script, outputting only the corrected Karate DSL script:

        {feature_content}
        """

    messages = [
        {"role": "system", "content": "You are an expert in Karate DSL syntax. Generate or correct Karate DSL scripts without including any explanations or non-DSL text in the output."},
        {"role": "user", "content": prompt}
    ]
        
    return call_llm(f"compat-{file_path}", messages, trace_id, span_id)

def verify_karate_syntax(file_path:str, content: str, trace_id: str, span_id: str) -> str:
    messages = [
        {"role": "system", "content": 
        """You are an AI assistant specializing in code formatting and syntax correction. 
        Your task is to modify the following Karate DSL code snippets. Follow these rules strictly:

        IF The Karate DSL script provided is already correct and does not require any corrections, just output the same test as it is, without any modifications.

        Example of correct Karate DSL syntax:

        Feature: Sample API Test

        Scenario: Basic GET request
          Given url 'https://api.example.com'
          And path '/users'
          When method GET
          Then status 200
          And match response == 'expectedResponse'
        """},
        {"role": "user", "content": f"Outputting only the corrected Karate DSL script:\n\n{content}"}
    ]
    
    return call_llm(f"syntax-{file_path}", messages, trace_id, span_id)

def process_karate_file(file_path):
    from config import SESSION_ID

    trace = langfuse.trace(
        id = TRACE_ID,
        session_id = SESSION_ID
        )
    
    content = read_karate_file(file_path)
    log.info("Original content:")
    log.info(content)
    
    # Step 1: Verify compatibility
    compatibility_span = trace.span(name=f"Verify Compatibility-{file_path}")
    compatibility_span.update(input=content)
    compatible_content = verify_karate_compatibility(file_path, content, TRACE_ID, compatibility_span.id)
    if compatible_content:
        log.info("\nContent after compatibility check:")
        log.info(compatible_content)
        compatibility_span.update(output=compatible_content)
    else:
        log.error("\nCompatibility check failed. Using original content for syntax verification.")
        compatible_content = content
        compatibility_span.update(output="Failed, using original content")
    compatibility_span.end()
    
    # Step 2: Verify syntax
    syntax_span = trace.span(name=f"Verify Syntax-{file_path}")
    verified_content = verify_karate_syntax(file_path, compatible_content, TRACE_ID, syntax_span.id)
    if verified_content:
        log.info("\nFinal verified content:")
        log.info(verified_content)
        syntax_span.update(output=verified_content)
        
        # Write the verified content to a new file with a '_verified' suffix
        verified_file_path = file_path.rsplit('.', 1)[0] + '_verified.' + file_path.rsplit('.', 1)[1]
        os.makedirs(os.path.dirname(verified_file_path), exist_ok=True)
        with open(verified_file_path, 'w') as file:
            file.write(verified_content)
        log.info(f"\nVerified content written to: {verified_file_path}")
    else:
        log.error("\nSyntax verification failed. No changes were made.")
        syntax_span.update(output="Failed, no changes made")
    syntax_span.end()

    
    return verified_content if verified_content else content