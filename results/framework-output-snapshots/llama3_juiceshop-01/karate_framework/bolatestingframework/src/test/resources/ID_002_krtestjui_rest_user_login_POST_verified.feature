Feature: Testing User Enumeration and Session Management

Scenario: Verify user enumeration vulnerability
Given url 'http://192.168.1.112:3133/rest/user/login'
And request { username: 'nonexistent_user', password: 'Password123' }
When method post
Then status 401
And match response contains 'Incorrect username or password.'