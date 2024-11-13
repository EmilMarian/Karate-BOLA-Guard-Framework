Feature: Broken Authentication/Authorization

  Scenario: Verify login endpoint is vulnerable to unauthorized access attempts - empty password
    Given url "http://192.168.1.106:5080/users/v1/login"
    And request
    """
    {
      "username": "admin",
      password: ""
    }
    """
    When method post
    Then status 403
    
  Scenario: Verify login endpoint is vulnerable to unauthorized access attempts - wrong password
    Given url "http://192.168.1.106:5080/users/v1/login"
    And request
    """
    {
      "username": "admin",
      "password": "wrongPassword"
    }
    """
    When method post
    Then status 403
    And match response.status == "#regex ^4[0-5]$"

# This scenario checks for broken authentication by attempting to log in as an admin 
# without a password and also using incorrect credentials, expecting the server to 
# respond with unauthorized access error (status code 403).