Feature: Test for Broken Authentication/Authorization on Contact Mechanic Endpoint
  Scenario: Attempt to contact a mechanic without proper authentication
    Given url "http://192.168.1.112:8888/workshop/api/merchant/contact_mechanic"
    And request
    """
    {
      "name": "'John Doe'",
      "email": "'johndoe@example.com'",
      "phone": "'555-555-1234'"
    }
    """
    When method post
    Then status 401
    And match response contains "Unauthorized"
  
  Scenario: Attempt to contact a mechanic with invalid authentication credentials
    Given url "http://192.168.1.112:8888/workshop/api/merchant/contact_mechanic"
    And request
    """
    {
      "name": "'John Doe'",
      "email": "'johndoe@example.com'",
      "phone": "'555-555-1234'"
    }
    """
    When method post
    Then status 401
    And match response contains "Invalid token"