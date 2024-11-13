Feature: Testing for Broken Authentication/Authorization Vulnerabilities
  Scenario: Verify that authentication and authorization are properly implemented on the /users/v1/login endpoint
    Given url "http://192.168.1.106:5080/users/v1/login"
    And request { username: 'nonexistent_user', password: 'Password123' }
    When method post
    Then status 401
    And match response.contains('Invalid credentials')