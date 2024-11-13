Feature: Basket Items API Testing
  Scenario: Check for Broken Authentication/Authorization Vulnerabilities
    Given url http://192.168.1.112:3133/api/BasketItems/
    And request { "username": "admin", "password": "password" }
    When method post
    Then status 401
    And match response contains "Unauthorized"