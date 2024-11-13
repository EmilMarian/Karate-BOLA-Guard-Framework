Feature: Test API for Broken Authentication/Authorization Vulnerabilities
  Scenario: Verify that the signup process does not allow account enumeration
    Given url "http://192.168.1.112:3133/identity/api/auth/signup"
    And request { username: "'existingUser'", password: "'Password123!', email: "'existing@example.com'" }
    When method post
    Then status 400
    And match response contains 'Invalid grant: username already exists.'