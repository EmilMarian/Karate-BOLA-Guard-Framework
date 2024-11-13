Feature: Testing for Broken Authentication/Authorization Vulnerabilities
  Scenario: Verify that the login process requires valid credentials
    Given url http://192.168.1.112:3133/rest/user/login
    And request { username: 'valid_username', password: 'valid_password' }
    When method post
    Then status 200
    And match response contains 'Successfully logged in.'