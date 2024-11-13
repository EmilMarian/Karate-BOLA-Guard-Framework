
# Instructions > Running the Karate Testing Framework inside Docker

Here are the required commands to build the docker image and run the docker container/tests:

Build the Docker image
```bash
docker build -t karatetestframework .
```

Run the tests


```bash
sudo docker run --rm \
  -v $(pwd)/bolatestingframework/target/karate-reports:/app/target/karate-reports \
  -v $(pwd)/bolatestingframework/src/test:/app/src/test \
  -v $HOME/.m2:/root/.m2 \
  karatetestframework
```

With this setup:
1. The Docker image contains the compiled application code but not the test resources.
2. Test resources (feature files) are mounted at runtime, allowing you to modify tests without rebuilding the image.
3. The Maven local repository is mounted to cache dependencies between runs.
4. You only need to rebuild the Docker image if you change the application code or `pom.xml`.

This approach allows for faster iteration on your tests while keeping the benefits of running in a containerized environment.

