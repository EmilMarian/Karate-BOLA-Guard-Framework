import os
import re
import shutil
import subprocess
import webbrowser
import logging
import stat
from karate_compatibility_verifier import CHROMA_CLIENT, call_llm, verify_karate_syntax
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

TEST_RESULTS_COLLECTION = "test_results"
from config import SESSION_ID, OUTPUT_LOG, OUTPUT_DIR, langfuse, TRACE_ID, ERROR_CHECK_NR, configure_logging

# Configure logging and get the log object
log = configure_logging(__name__)


class KarateTestFramework:

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.collection = Chroma(client=CHROMA_CLIENT, collection_name=TEST_RESULTS_COLLECTION, embedding_function=self.embeddings)
        self.source_dir = "./output/karate_feature_files"
        self.destination_dir = "./output/karate_framework/bolatestingframework/src/test/resources"
        self.docker_context = "./output/karate_framework"
        self.reports_dir = os.path.abspath(f"./output/karate_framework/target/karate-reports_{TRACE_ID}")

    def parse_docker_logs(self, log_file_path):
        test_results = {}
        with open(log_file_path, 'r') as log_file:
            current_feature = None
            for line in log_file:
                feature_match = re.search(r'not a valid feature file: (.+\.feature)', line)
                if feature_match:
                    current_feature = feature_match.group(1)
                    test_results[current_feature] = {'status': 'failed', 'errors': []}
                
                if current_feature:
                    if 'passed' in line.lower():
                        test_results[current_feature]['status'] = 'passed'
                    elif 'failed' in line.lower():
                        test_results[current_feature]['status'] = 'failed'
                    
                    error_match = re.search(r'(Syntax error at line \d+:|mismatched input .* expecting <EOF>|Error: .+)', line)
                    if error_match:
                        test_results[current_feature]['errors'].append(error_match.group(1))

        return test_results
    
    def store_results_in_chroma(self, test_results):
        for feature, result in test_results.items():
            self.collection.add_texts(
                texts=[str(result['errors'])],
                metadatas=[{
                    "feature": feature,
                    "status": result['status'],
                    "errors": ", ".join(result['errors'])
                }],
                ids=[feature]
            )

    def get_relevant_errors(self, feature_content: str, k: int = 3) -> list:
        results = self.collection.similarity_search(feature_content, k=k)
        # Prioritize "status": "verified" errors
        errors = [(doc.metadata['status'], doc.metadata['errors']) for doc in results]
        log.info(f"errors found: {errors}")
        return errors

    def move_feature_files(self):
        os.makedirs(self.destination_dir, exist_ok=True)
        # Clear the destination directory before moving files
        for filename in os.listdir(self.destination_dir):
            file_path = os.path.join(self.destination_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                log.info(f"Removed {filename} from {self.destination_dir}")
        
        for filename in os.listdir(self.source_dir):
            if filename.endswith("_verified.feature"):
                source_file = os.path.join(self.source_dir, filename)
                destination_file = os.path.join(self.destination_dir, filename)
                shutil.move(source_file, destination_file)
                log.info(f"Moved {filename} to {self.destination_dir}")

    def retrieve_and_analyze_results(self):
        results = self.collection.get(
            where={"status": "failed"}
        )
        tests_to_rewrite = []
        for id, metadata in zip(results['ids'], results['metadatas']):
            if metadata['errors']:
                tests_to_rewrite.append((id, metadata['errors'].split(', ')))
        return tests_to_rewrite
    
    def rewrite_failed_tests(self, tests_to_rewrite):
        for feature_file, errors in tests_to_rewrite:

            trace = langfuse.trace(
                session_id = SESSION_ID,
                id = TRACE_ID,
            )

            span = trace.span(
                name=feature_file
            )

            file_path = os.path.join(self.destination_dir, feature_file)
            with open(file_path, 'r') as file:
                original_content = file.read()

            relevant_errors = self.get_relevant_errors(original_content)
            # Prioritize "status": "verified" errors
            verified_errors = [error for status, error in relevant_errors if status == "verified"]
            other_errors = [error for status, error in relevant_errors if status != "verified"]
            prioritized_errors = verified_errors + other_errors
            
            prompt = f"""
            This Karate DSL test script failed with the following errors:
            {errors}

            Here are some relevant errors from similar tests:
            {prioritized_errors}

            Please rewrite the test script to fix these errors. Here's the original content:

            {original_content}

            Provide only the corrected Karate DSL script without any explanations. Remove any code block delimiters especially the backticks ones before the Feature keyword or the ones at the end of the file. Ensure all URLs and request bodies are properly enclosed in quotes.
            """

            messages = [
                {"role": "system", "content": "You are an expert in Karate DSL and Java. Rewrite the given test script to fix the specified errors."},
                {"role": "user", "content": prompt}
            ]

            span.update(input = messages)

            rewritten_content = call_llm(feature_file, messages, trace_id=TRACE_ID, span_id="error-span-check")
            verified_content = verify_karate_syntax(feature_file, rewritten_content, TRACE_ID, "error-span-check")
            # Prepare the result to store in Chroma
            verified_result = {
                "feature": feature_file,
                "status": "verified",  
                "errors": errors,  
                "rewritten_content": verified_content
            }
            # Storing the verified rewritten test script in Chroma
            self.store_results_in_chroma({feature_file: verified_result})
            
            if verified_content.startswith("Here is the corrected Karate DSL script:"):
                verified_content = verified_content.replace("Here is the corrected Karate DSL script:", "", 1).strip()
            if verified_content.endswith('"') and verified_content.count('"') % 2 != 0:
                verified_content = verified_content.rstrip('"')
            span.update(output = verified_content) 
            if verified_content:
                with open(file_path, 'w') as file:
                    file.write(verified_content)
                log.info(f"Updated test script: {feature_file}")
            else:
                log.error(f"Failed to verify rewritten content for: {feature_file}")

    def open_report(self):
        report_path = os.path.join(self.reports_dir, "karate-summary.html")
        if os.path.exists(report_path):
            webbrowser.open(f"file://{report_path}")
            log.info(f"Opened test report: {report_path}")
        else:
            log.error("Test report not found. Make sure tests have been run.")

    def change_permissions(self, file_path):
        """Change file permissions to allow deletion."""
        try:
            os.chmod(file_path, stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        except Exception as e:
            log.error(f"Error changing permissions for {file_path}: {e}")

    def clear_reports_directory(self):
        """Clear the reports directory."""
        if os.path.exists(self.reports_dir):
            for filename in os.listdir(self.reports_dir):
                file_path = os.path.join(self.reports_dir, filename)
                self.change_permissions(file_path)  # Change permissions before removal
                try:
                    os.remove(file_path)  # Attempt to remove the file
                except PermissionError:
                    log.warning(f"Permission denied: {file_path}. Skipping.")
                except Exception as e:
                    log.error(f"Error removing {file_path}: {e}")
            shutil.rmtree(self.reports_dir)  # Remove the directory after files are deleted
        os.makedirs(self.reports_dir, exist_ok=True)

    def clear_target_directory(self):
        """Clear the target directory."""
        if os.path.exists(self.reports_dir):
            for filename in os.listdir(self.reports_dir):
                file_path = os.path.join(self.reports_dir, filename)
                self.change_permissions(file_path)  # Change permissions before removal
                try:
                    os.remove(file_path)  # Attempt to remove the file
                except PermissionError:
                    log.warning(f"Permission denied: {file_path}. Skipping.")
                except Exception as e:
                    log.error(f"Error removing {file_path}: {e}")
            shutil.rmtree(self.reports_dir)  # Remove the directory after files are deleted
        os.makedirs(self.reports_dir, exist_ok=True)

    def run_docker_tests(self):
        # self.clear_target_directory()  # Clear the target directory before running tests
        log.info("Building Docker image...")
        subprocess.run(["docker", "build", "-t", "karatetestframework", self.docker_context], check=True)

        log.info("Running Karate tests in Docker...")
        os.makedirs(self.reports_dir, exist_ok=True)
        result = subprocess.run([
            "docker", "run", "--rm",
            "-v", f"{os.path.abspath(self.docker_context)}/target/karate-reports_{TRACE_ID}:/app/target/karate-reports",
            "-v", f"{os.path.abspath(self.docker_context)}/bolatestingframework/src/test/:/app/src/test",
            "-v", f"{os.path.expanduser('~')}/.m2:/root/.m2",
            "karatetestframework"
        ], capture_output=True, text=True, check=False)

        # Store logs with unique log file name including TRACE_ID
        log_file_path = os.path.join(self.reports_dir, f"docker_run_logs_{TRACE_ID}.txt")
        with open(log_file_path, "w") as log_file:
            log_file.write(result.stdout)
            log_file.write(result.stderr)

        log.info(f"Docker run logs saved to: {log_file_path}")
        log.info(f"Test reports are available in: {self.reports_dir}")
        test_results = self.parse_docker_logs(log_file_path)
        self.store_results_in_chroma(test_results)

        return log_file_path

    def run(self, executeManual=False):
        if not executeManual:
            log.info("Starting to move Karate feature files...")
            self.move_feature_files()
            log.info("Finished moving Karate feature files.")
        
        log.info("Running Karate tests in Docker...")
        self.run_docker_tests()
        max_iterations = ERROR_CHECK_NR
        for iteration in range(1, max_iterations + 1):
            log.info(f"Starting iteration {iteration} of {max_iterations}")
            
            log_file_path = self.run_docker_tests()
            test_results = self.parse_docker_logs(log_file_path)
            self.store_results_in_chroma(test_results)
            tests_to_rewrite = self.retrieve_and_analyze_results()
            
            if not tests_to_rewrite:
                log.info(f"All tests passed in iteration {iteration}. Exiting loop.")
                break
            
            log.info(f"Rewriting {len(tests_to_rewrite)} broken tests in iteration {iteration}")
            self.rewrite_failed_tests(tests_to_rewrite)
            
            if iteration == max_iterations:
                log.error(f"Reached maximum iterations ({max_iterations}). Some tests may still be failing.")

        log.info("Opening final test report...")
        self.open_report()

if __name__ == "__main__":
    import sys
    executeManual = sys.argv[1] == "true" if len(sys.argv) > 1 else False
    framework = KarateTestFramework()
    framework.run(executeManual=True)  # Example usage with executeManual=True
