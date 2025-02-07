import json
import os
import uuid
from typing import List, Dict, Any
from oas_fragment_retriever import OASFragmentRetriever
from karate_security_test_template import generate_prompt
from karate_llm_test_gen import generate_karate_test
from karate_compatibility_verifier import process_karate_file
from oas_fragment_store import embed_and_store_fragments
from langfuse import Langfuse
from config import SESSION_ID, TRACE_ID, langfuse, OUTPUT_DIR, OUTPUT_LOG, TEST_CASE_NUMBER, OAS_FILE_PATH, BOLA_MAIN_QUERY, ERROR_CHECK_NR,ARHITECTURE,  configure_logging
import sys
import logging
import shutil


def ensure_output_directory(directory):
    """Ensure that the output directory exists."""
    os.makedirs(directory, exist_ok=True)

def sanitize_filename(filename):
    """Sanitize the filename to ensure it's valid."""
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c in ['-', '_']]).rstrip()

def clean_output_directory(directory):
    """Clean the output directory by removing all files."""
    if os.path.exists(directory):
        shutil.rmtree(directory)  # Remove the directory and all its contents
    os.makedirs(directory)  # Recreate the directory

# Ensure the output log directory exists
ensure_output_directory(OUTPUT_LOG)  # Ensure the output log directory exists

log = configure_logging(__name__)

def main():
    # Check if the skip flag is provided
    trace = langfuse.trace(name=f"Test_{TRACE_ID}", session_id = SESSION_ID, id = TRACE_ID, tags=[ARHITECTURE])

    skip_fragment_creation = len(sys.argv) > 1 and sys.argv[1] == "skipFragmentCreation"
    log.info(f"Skipping fragment creation: {skip_fragment_creation}")
    api_name =  os.path.splitext(OAS_FILE_PATH)[0]
    collection_name =  f"{api_name}_fragments"
    context_span = trace.span(name="retrive oas fragments")
    retriever = OASFragmentRetriever(collection_name)
    context_span.update(input = f"retrive oas fragments: {collection_name}")

    # Clean the output directory before ensuring it exists
    clean_output_directory(OUTPUT_DIR)

    if not skip_fragment_creation:
        # Example: Generate tests for authentication-related endpoints
        log.debug("Starting fragment retrieval process.")
        query = BOLA_MAIN_QUERY

        fragments = retriever.retrieve_fragments(query, n_results=TEST_CASE_NUMBER)
        log.debug(f"Retrieved fragments: {fragments}, form collection {collection_name}")

        context_span.update(output = f"{collection_name}: {fragments}")

        context_span.end()
        if len(fragments) > 0:
            for i, fragment in enumerate(fragments):
                endpoint_info = json.loads(fragment['content'])
                
                endpoint_str = f"""
                Path: {endpoint_info['path']}
                Method: {endpoint_info['method']}
                Description: {endpoint_info.get('description', 'No description available')}
                Authentication: {endpoint_info.get('security', 'Not specified')}
                """

                initial_test_span = trace.span(name="Initial test")
                
                prompt = generate_prompt(endpoint_str)
                initial_test_span.update(input=prompt)
                karate_test = generate_karate_test(prompt)
                initial_test_span.update(output=karate_test)

                # Create a sanitized filename
                sanitized_path = sanitize_filename(endpoint_info['path'].replace('/', '_'))
                oas_prefix = OAS_FILE_PATH[:3]
                file_name = f"ID_{i+1:03d}_krtest{oas_prefix}{sanitized_path}_{endpoint_info['method']}.feature"
                file_path = os.path.join(OUTPUT_DIR, file_name)

                with open(file_path, 'w') as f:
                    f.write(karate_test)

                log.info(f"Generated Karate test for {endpoint_info['path']} {endpoint_info['method']} at {file_path}")

                # Add compatibility verification here
                compatibility_issues = process_karate_file(file_path)
                if compatibility_issues:
                    log.warning(f"Compatibility issues found in {file_path}: {compatibility_issues}")
                else:
                    log.info(f"No compatibility issues found in {file_path}")
                # Continue with the rest of the script
            log.info("Moving generated Karate feature files...")
            from karate_test_framework import KarateTestFramework
            log.info("Creating the Karate Test Framework with generated feature files")
            framework = KarateTestFramework()
            log.info("Skipping karate test run.")

            # framework.run()
        else:
            # create fragments
            # embed_and_store_fragments(fragments, collection_name)
            log.warning("No fragments found, skipped test running.")

if __name__ == "__main__":
    main()
