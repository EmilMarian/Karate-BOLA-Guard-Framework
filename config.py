import uuid
import logging
import os
from langfuse import Langfuse


# LANGUAGE_MODEL = "Phi-3 Mini Instruct"
# LANGUAGE_MODEL = "Llama 3 8B Instruct"
# LANGUAGE_MODEL = "Mistral Instruct"
LANGUAGE_MODEL = "Wizard v1.2"
# OAS_FILE_PATH = "crapi.yaml"
# OAS_FILE_PATH = "juiceshop.yaml"
OAS_FILE_PATH = "vampi.yaml"


def generate_prefixed_uuid(language_model):
    prefix_map = {
        "Llama 3 8B Instruct": "L3I",
        "Phi-3 Mini Instruct": "P3M",
        "Mistral Instruct": "MI",
        "Wizard v1.2": "W12"
    }
    prefix = prefix_map.get(language_model, "UNK")
    oas_prefix = OAS_FILE_PATH[:3]
    return f"{prefix}-{oas_prefix}-{uuid.uuid4()}"

SESSION_ID = generate_prefixed_uuid(LANGUAGE_MODEL)
TRACE_ID = generate_prefixed_uuid(LANGUAGE_MODEL) # Generate a new UUID for the session
# API Endpoints
# TEST_API_URL = "http://192.168.1.112:8888" # Crapi
# TEST_API_URL = "http://192.168.1.112:3133" # Juice Shop 
TEST_API_URL = "http://192.168.1.106:5080" # Vampi 
ERROR_CHECK_NR = 3


LANGFUSE_URL = "http://192.168.1.106:3015"
OPEN_LLM_URL = "http://192.168.1.106:4893/v1/chat/completions"
KARATE_DSL_COLLECTION = "karate_dsl_features"
CHROMA_URL = "localhost"

OAS_PARSER_URL = "http://localhost:5111/parse"
OUTPUT_DIR = "output/karate_feature_files"
OUTPUT_LOG = "output/logs"
TEST_CASE_NUMBER= 3

BOLA_MAIN_QUERY = "authorization authentication login register or signup"

langfuse = Langfuse(
    public_key="pk-lf-####################################",
    secret_key="sk-lf-#####################################",
    host=LANGFUSE_URL
)

def configure_logging(class_name:str = __name__):
    log = logging.getLogger(class_name)
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    
    log_file_path = os.path.join(OUTPUT_LOG, f'process_{TRACE_ID}.log')  # Define the log file path with TRACE_ID
    file_handler = logging.FileHandler(log_file_path)  # Create a file handler
    file_handler.setFormatter(formatter)  # Set the same formatter
    log.addHandler(file_handler)  # Add the file handler to the logger

    return log  # Return the log object

# Call this function to configure logging
log = configure_logging(__name__)  # Store the log object for use