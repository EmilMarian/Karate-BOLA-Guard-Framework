from string import Template

from config import TEST_API_URL

KARATE_SECURITY_TEST_TEMPLATE = Template(f"""
Given the following API endpoint information:
$endpoint_info
Make sure to provide the following API url {TEST_API_URL} for each sceneario, along with the corresponding path, if that is the case. Do not use mockup URLs or paths.
Generate a Karate DSL test script to check for potential Broken Authentication/Authorization vulnerabilities. 

""")

def generate_prompt(endpoint_info: str) -> str:
    return KARATE_SECURITY_TEST_TEMPLATE.substitute(endpoint_info=endpoint_info)
