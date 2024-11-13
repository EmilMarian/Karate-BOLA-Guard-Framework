Feature: Test for Broken Authentication/Authorization on /users/v1/register Endpoint
  Scenario: Attempt to register with invalid credentials
    Given url "http://192.168.1.106:5080/users/v1/register"
    And request { username:"invalid_user", password:"password" }
    When method post
    Then status 401
    And match response contains 'Invalid credentials'