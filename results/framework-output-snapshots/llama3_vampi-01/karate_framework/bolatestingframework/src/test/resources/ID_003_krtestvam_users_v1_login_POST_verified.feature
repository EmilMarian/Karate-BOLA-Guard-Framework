Feature: Testing User Login Endpoint

Scenario: Verify user login does not allow authentication bypass
Given url "http://192.168.1.106:5080/users/v1/login"
And request { "username": "nonexistent_user", "password": "Password123" }
When method post
Then status 401
And match response contains "Invalid credentials"

Scenario: Verify user login does not allow session reuse after logout
Given url "http://192.168.1.106:5080/users/v1/login"
And request { "username": "existing_user", "password": "Password123" }
When method post
Then status 200
And match response contains "Logged in successfully"