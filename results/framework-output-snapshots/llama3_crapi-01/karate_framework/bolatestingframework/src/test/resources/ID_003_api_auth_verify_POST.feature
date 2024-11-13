Feature: Test API for Broken Authentication/Authorization

Scenario: Verify that the /auth/verify endpoint does not allow unauthorized access
Given url "http://192.168.1.112:8888"
And request { "username" : "", "password": "" }
When method post
Then status 401
And match response == {"error": "Invalid credentials"}

Scenario: Attempt to verify an existing user with incorrect password
Given url "http://192.168.1.112:8888"
And request { "username": "existingUser", "password": "wrongPassword" }
When method post
Then status 401
And match response == {"error": "Invalid credentials"}

Scenario: Verify that the /auth/verify endpoint returns a specific error message for incorrect usernames
Given url "http://192.168.1.112:8888"
And request { "username": "nonExistingUser", "password": "Password123!" }
When method post
Then status 401
And match response == {"error": "Invalid credentials"}

Scenario: Verify that the /auth/verify endpoint returns a specific error message for incorrect passwords
Given url "http://192.168.1.112:8888"
And request { "username": "existingUser", "password": "wrongPassword" }
When method post
Then status 401
And match response == {"error": "Invalid credentials"}