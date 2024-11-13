Feature: Testing for Broken Authentication/Authorization
Scenario: Verify that the registration process does not allow account enumeration
Given url "http://192.168.1.106:5080/users/v1/register"
And request { username: "existingUser", password: "Password123!", email: "existing@example.com" }
When method post
Then status 200
And match response contains "A verification email has been sent. Please check your inbox."

Scenario: Test for user enumeration vulnerabilities on the registration endpoint
Given url "http://192.168.1.106:5080/users/v1/register"
And request { "username": "nonexistent_user", "password": "Password123!" }
When method post
Then status 401

Scenario: Test for user enumeration vulnerabilities on the registration endpoint (again)
Given url "http://192.168.1.106:5080/users/v1/register"
And request { "username": "existing_user", "password": "WrongPassword" }
When method post
Then status 401

Scenario: Verify that an unauthorized user cannot register a new account
Given url "http://192.168.1.106:5080/users/v1/register"
When method post
Then status 403
And match response contains "Unauthorized access denied"