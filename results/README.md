# Results Directory

Several findings were concluded based on various artifacts (logs, LLM metrics, and others).

## Successful Test Runs with Associated Test Files

Although the framework produces quality test cases, it still requires manual intervention. As such, we have fixed a few test cases in order to run them against the API and produce a report. The full generated content for these test cases can be explored in the `framework-output-snapshots` directory.

If you wish to explore only the Karate Reports, they can be found in the `karate-reports` directory for easy access.

## Langfuse Snapshots

We used Langfuse for LLM observability. A few snapshots were generated and can be found in the `langfuse-dashboard-snapshots` directory.

## Raw Framework and Test Run Logs

If you wish to inspect the process from start to finish, we've also included a few raw logs from the framework that were gathered during our experiments (`raw-process-logs` directory). Additionally, the test run logs (`raw-test-run-docker-logs`) are available, where you can observe the most common causes of test run failures.
