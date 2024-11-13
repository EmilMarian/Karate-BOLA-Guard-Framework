Feature: Broken Authentication/Authorization on User Registration

  Scenario: Attempt to register a user without proper authentication or authorization
    Given url "http://192.168.1.106:5080/users/v1/login"
    And request
    """
    {
      "username": "unauthorized_user",
      "password": "",
      "email": ""
    }
    """
    When method post
    Then status 403