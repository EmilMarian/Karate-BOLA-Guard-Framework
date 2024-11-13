import requests
import json
import os
import argparse
from typing import List, Dict, Any
from config import OAS_PARSER_URL

def check_service_status():
    try:
        response = requests.get(f"http://localhost:5111/heartbeat")
        if response.status_code == 200:
            print("OAS Parser service is online.")
        else:
            print("OAS Parser service is not responding correctly.")
            exit(1)
    except requests.ConnectionError:
        print("Could not connect to OAS Parser service. Make sure it's running.")
        exit(1)

def parse_oas_file(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(OAS_PARSER_URL, files=files)
    
    if response.status_code == 200:
        return response.json()['fragments']
    else:
        print(f"Error parsing OAS file: {response.text}")
        exit(1)

def save_fragments(fragments: List[Dict[str, Any]], oas_service_name: str):
    output_dir = os.path.join('output', oas_service_name)
    os.makedirs(output_dir, exist_ok=True)

    for fragment in fragments:
        file_name = fragment['file_name']
        content = fragment['content']
        file_path = os.path.join(output_dir, file_name)

        with open(file_path, 'w') as f:
            json.dump(content, f, indent=2)
    
    print(f"Saved {len(fragments)} fragments to {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Process OAS YAML file and save fragments.")
    parser.add_argument("file_path", help="Path to the OAS YAML file")
    args = parser.parse_args()

    check_service_status()

    fragments = parse_oas_file(args.file_path)

    oas_service_name = os.path.splitext(os.path.basename(args.file_path))[0]
    save_fragments(fragments, oas_service_name)

if __name__ == "__main__":
    main()