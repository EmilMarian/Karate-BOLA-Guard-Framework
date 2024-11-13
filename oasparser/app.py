import yaml
import json
import os
import re
from typing import Dict, Any
from flask import Flask, request, jsonify
from io import StringIO

app = Flask(__name__)

class OASParserAgent:
    def __init__(self):
        pass

    def load_yaml(self, yaml_content: str) -> Dict[str, Any]:
        return yaml.safe_load(yaml_content)

    def resolve_ref(self, ref: str, openapi_data: Dict[str, Any]) -> Dict[str, Any]:
        parts = ref.replace('#/', '').split('/')
        schema = openapi_data
        for part in parts:
            schema = schema.get(part)
        return schema

    def find_and_resolve_refs(self, obj: Any, openapi_data: Dict[str, Any]) -> Any:
        if isinstance(obj, dict):
            if '$ref' in obj:
                return self.resolve_ref(obj['$ref'], openapi_data)
            else:
                return {k: self.find_and_resolve_refs(v, openapi_data) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.find_and_resolve_refs(item, openapi_data) for item in obj]
        return obj

    def process_openapi_content(self, openapi_content: str):
        openapi_data = self.load_yaml(openapi_content)
        paths = openapi_data['paths']
        api_name = openapi_data.get('info', {}).get('title', 'api').replace(' ', '_')
        id_counter = 1
        fragments = []

        for path, methods in paths.items():
            for method, spec in methods.items():
                spec_resolved = self.find_and_resolve_refs(spec, openapi_data)

                for status_code, response in spec.get('responses', {}).items():
                    id_prefix = str(id_counter).zfill(4)
                    id_counter += 1

                    file_name_parts = [
                        id_prefix,
                        path.strip('/').replace('/', '_'),
                        method,
                        status_code
                    ]

                    file_name = '_'.join(file_name_parts) + '.json'
                    file_name = re.sub(r'[^a-zA-Z0-9_.]', '', file_name)

                    method_data = {
                        'path': path,
                        'method': method.upper(),
                        'responses': {status_code: self.find_and_resolve_refs(response, openapi_data)},
                        'requestBody': self.find_and_resolve_refs(spec.get('requestBody', {}), openapi_data),
                        'parameters': self.find_and_resolve_refs(spec.get('parameters', []), openapi_data)
                    }

                    fragments.append({
                        'file_name': file_name,
                        'content': method_data
                    })

        return fragments

@app.route('/parse', methods=['POST'])
def parse_oas():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        yaml_content = file.read().decode('utf-8')
        parser = OASParserAgent()
        fragments = parser.process_openapi_content(yaml_content)
        return jsonify({'fragments': fragments})

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return jsonify({
        'status': 'online',
        'version': '0.0.1',
        'message': 'OAS Parser service is running'
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)