Feature: Test for Broken Authentication/Authorization on Contact Mechanic API Endpoint
  Scenario: Attempt to contact a mechanic without proper authentication
    Given url "http://192.168.1.112:3133/workshop/api/merchant/contact_mechanic"
    And request
    """
    {
      "name": "John Doe",
      "email": "johndoe@example.com",
      "phone": "555-555-5555"
    }
    """
    When method post
    Then status code is 401
    And match response contains "Unauthorized"