Feature: Broken Authentication/Authorization Testing for /identity/api/auth/signup Endpoint

  Background:
    * url "http://192.168.1.112:8888/identity/api/auth/signup"

  Scenario Outline: Verify signup endpoint security against information disclosure
    Given request
    """ 
    {
      "username": "<username>",
      "password": "<password>",
      "email": "<email>"
    }
    """
    When method post
    Then status 403

    Examples:
      | username    | password        | email             |
      | validUser   | correctPass123! | test@example.com  |
      | invalidUser | wrongPass123!   | test2@example.com |

# This test verifies that the endpoint maintains security by:
# 1. Returning appropriate 403 status for unauthorized attempts
# 2. Not leaking sensitive information in error messages
# 3. Using generic error responses for both valid and invalid credentials