Feature: test
Scenario: Attempt to exploit OAuth token generation with a stolen authorization code
Given url "http://192.168.1.112:8888/workshop/api/merchant/contact_mechanic"
And request
"""
{
    "grant_type": "authorization_code",
    "code": "stolen_code",
    "redirect_uri": "http://evil.example.com",
    "client_id": "client_id",
    "client_secret": "client_secret"
}
"""
When method post
Then status 400
And match response contains "Invalid grant: authorization code is invalid"