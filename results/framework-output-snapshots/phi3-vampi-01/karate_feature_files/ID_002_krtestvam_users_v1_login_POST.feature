```json
{
  "feature": "Broken Authentication/Authorization",
  "scenario": "Verify login endpoint is vulnerable to unauthorized access attempts.",
    "steps": [
        {
            "Given url http://192.168.1.106:5080/users/v1/login",
            "When method post with body {'username': 'admin', 'password': ''}",
            "Then status 403"
        },
        {
            "Given url http://192.168.1.106:5080/users/v1/login",
            "When method post with body {'username': 'admin', 'password': 'wrongPassword'}",
            "Then status 403"
        },
        {
            "# Explanation": "This scenario checks for broken authentication by attempting to log in as an admin without a password and also using incorrect credentials, expecting the server to respond with unauthorized access error (status code 403).",
            "And match response.contains('Unauthorized')"
        }
    ]
}
```