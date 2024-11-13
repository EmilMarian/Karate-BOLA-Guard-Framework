Feature: Security Test for Broken Authentication/Authorization on /identity/api/auth/verify Endpoint

  Background:
    * url "http://192.168.1.112:8888/identity/api/auth/verify"

  Scenario: Verify authentication endpoint security - non-existent user
    Given request 
    """ 
    {
      "username": "non_user",
      "password": "wrongpassword123!"
    }
    """
    When method post
    Then status 401

  Scenario: Verify authentication endpoint security - wrong password for existing user
    Given request 
    """ 
    {
      "username": "existing_user",
      "password": "wrongpassword123!"
    }
    """
    When method post
    Then status 401

# Security test goals:
# 1. Verify no information disclosure through error messages
# 2. Ensure consistent responses for all failed attempts
# 3. Prevent user enumeration attacks
# 4. Maintain compliance with security best practices