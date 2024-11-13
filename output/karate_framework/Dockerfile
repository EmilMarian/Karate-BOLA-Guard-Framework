FROM maven:3.8.4-openjdk-17

WORKDIR /app

# Copy pom.xml separately to cache dependencies
COPY bolatestingframework/pom.xml .
RUN mvn dependency:go-offline

# Copy the entire project structure
COPY bolatestingframework .

# Build the application
RUN mvn clean package -DskipTests

# Set the entry point to run tests
CMD ["mvn","test"]