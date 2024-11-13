Feature: Verify authentication and authorization
  Scenario: Verify that the /identity/api/auth/verify endpoint requires a valid token
    Given url http://192.168.1.112:8888/identity/api/auth/verify
    And request { "token": "invalid_token" }
    When method post
    Then status 401
    And match response contains "Unauthorized"
    
  Scenario: Verify that the /identity/api/auth/verify endpoint returns an error message when token is invalid
    Given url http://192.168.1.112:8888/identity/api/auth/verify
    And request { "token": "invalid_token" }
    When method post
    Then status 403
    And match response contains "Invalid token"