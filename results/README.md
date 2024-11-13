# Results Directory

Several findings were concluded based on various artifacts (logs, LLM metrics, and other). 

## Succesfull test runs with associated test files

Although, the framework produces quality test cases, stil requires manual intervention, as such, we have fixed a few test cases, in order to run them agains the API and produce a report. Full generated content for these such cases can be explored in `framework-output-snapshots` directory.

If you wish to explore only the Karate Reports, these can be found in the `karate-reports` for easy access.

## Langufse snapshots

We used Langufse for LLM observability, a few snapshots were generated and can be found in `langfuse-dashboard-snaphsots` directory.

## Raw Framwork and Test Run logs
If you wish to inspect the proccess for start to end, we've also included a few raw logs from the framework that were gathered during our experiments (`raw-proccess-logs` dir). And, also the test run logs (`raw-test-run-docker-logs`), in which, you can observe the most common causes of test run failure .