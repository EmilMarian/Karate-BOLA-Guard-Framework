Feature: Security Test for Broken Authentication/Authorization 
  Scenario: Verify that the authentication endpoint
  Given url "http://192.168.1.112:8888/workshop/api/merchant/contact_mechanic"
  And header Authorization = ""
  And request { "requestedMechanicId": 12345 } 
  When method post
  Then status is between 400 and 600