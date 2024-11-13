Feature: Verify authentication and authorization
  Scenario: Verify that the /identity/api/auth/verify endpoint requires a valid token
    Given url "http://192.168.1.112:3133/identity/api/auth/verify"
    And request { "token": "invalid_token" }
    When method post
    Then status 401
    And match response contains "Unauthorized"