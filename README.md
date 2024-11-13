# Karate BOLA-Guard Framework a Karate DSL Security Oriented Test Generator

**This project is currently in its early development stage and serves as a Proof of Concept (POC) to showcase how a RAG (Retrieve, Answer, Generate) framework can be used to generate security test scenarios. It takes an API Spec Yaml as input and leverages state-of-the-art open source RAG tools to produce security bola-oriented Karate DSL test scenarios. Please note that due to the experimental nature of this project, there might be instances of "spaghetti code" here and there. Your understanding and contributions are highly appreciated.**

This project is a Karate DSL test generator that uses AI to create and verify Karate test scripts for API endpoints.

In this project, there are particular scripts, that needs to be run prior to the main project script `rag_karate_test_gen.py` other than the perequisites for the environment, there are a few other requirments that are required for the script to correctly produce test cases.

This repository, also contains, utility scripts like `chroma_viewer.py` used to peak into different collections for self-check.

## Prerequisites

- Python 3.10+
- Java 11+ (for running Karate tests)
- ChromaDB
- Langfuse
- HuggingFace Embeddings
- GPT4ALL or other LLM Wrapper for Server integration
- Mistral 7B Model or other of choise
- Docker

## Setup

1. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

2. Set up the necessary instances and environment variables or update the configuration files with:
   - LLM API endpoint
   - Langfuse API keys
   - ChromaDB connection details

3. Ensure you have a running instance of ChromaDB with a collection named "karate_dsl_features".

## OAS Parser and Fragment Store
Before generating tests, you need to have the api framgments in the vectorDB.
1. Start the OasParser Service;
2. Run `python oasparser file.yaml` for parsing the file and producing the json file fragments;
3. Run the `oas_fragment_store.py` to store the fragments into the chromaDB. 

## RAG Test Gen Usage
1. Upload any relevant files to `knowledgebase` folder.
2. Run the `bola_store.py` for
3. Run the `oas_fragment_store.py` for API YAML parsing and storing the json framgents in the corresponding dir.

4. Generate Karate tests:
   ```
   python rag_karate_test_gen.py
   ```
   This will generate Karate test scripts based on the API endpoints in your OpenAPI specification.


## Project Structure

- `rag_karate_test_gen.py`: Main script for generating Karate tests
- `karate_compatibility_verifier.py`: Script for verifying and correcting Karate test syntax
- `karate_security_test_template.py`: Template for security-focused Karate tests
- `karate_llm_test_gen.py`: LLM integration for test generation
- `karate_test_framework.py`: Framework for running Karate tests

## Notes

- The project uses RAG (Retrieval-Augmented Generation) to create relevant test scenarios.
- Langfuse is used for tracing and monitoring the LLM calls.
- The generated tests are automatically verified for Karate DSL compatibility.
- Make sure to review and customize the generated tests as needed for your specific API endpoints.
- There are certain optional params, or other options in running and executing different parts of the project.

# Use Cases

For testing with the below use cases, please refer to their repositories, for guidance on instalation an usage.

## VAmPI use case example

Check https://github.com/erev0s/VAmPI for intalation and usage details.

## CrAPI use case example

Check https://github.com/OWASP/crAPI for intalation and usage details.

## JuiceShop use case example

Check https://github.com/juice-shop/juice-shop for intalation and usage details.

### Other options
- Running the karate test framework, skipping the fragment creation:

   ```
   python3 rag_karate_test_gen.py skipFragmentCreation
   ```
   This will run the Karate Test Framework with the generated and verified test scripts.

- Running the karate test framework docker file -> [See oasparser/README.md](oasparser/README.md)

## TODO/s  or nice to have features:
- [] Docker compose file with all the services and use cases;
- [] Support for Commercial LLMs;
- [] Tutorial on how to setup everything step by step locally.