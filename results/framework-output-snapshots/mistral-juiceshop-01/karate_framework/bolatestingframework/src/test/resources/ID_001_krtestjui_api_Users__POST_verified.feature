Feature: Test for Broken Authentication/Authorization Vulnerabilities
  Scenario: Attempt to access protected resource without authentication
    Given url "http://192.168.1.112:3133/api/Users/"
    And request method POST
    When status code is not 401
    Then match response contains "Unauthorized"