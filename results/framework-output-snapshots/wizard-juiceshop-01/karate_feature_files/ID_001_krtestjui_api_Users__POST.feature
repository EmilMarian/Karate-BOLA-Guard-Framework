Here are the Karate DSL test scripts for checking potential Broken Authentication/Authorization vulnerabilities:

1. **Testing for Improper Authorization on User Documents Access**
```karate
Feature: Test for Improper Authorization on User Documents Access
Scenario: Attempt to access a document without being an 'admin' or 'editor'
Given url 'http://api.example.com/documents/12345'
And header Authorization = 'Bearer <regular_user_token>'
When method get
Then status 403
And match response contains 'You do not have permission to access this document.'
* def adminAccess = callonce read('classpath:helpers/adminAccess.feature'),
* switch adminAccess.status,
  case 200:
    * assert adminAccess.response == 'Document details'
  case 403:
    fail 'Admin should have access'
```
1. **Testing for User Enumeration**
```karate
Feature: Testing for User Enumeration
Scenario: Verify the `/user/login` endpoint does not allow user enumeration
Given url 'http://api.example.com/user/login'
And request { username: 'nonexistent_user', password: 'Password123' }
When method post
Then status 401
And match response.contains('Incorrect username or password.')
And request { username: 'existing_user', password: 'WrongPassword' }
When method post
Then status 401
And match response.contains('Incorrect username or password.')
```
1. **Test API for Account Enumeration during Signup**
```karate
Feature: Test API for Account Enumeration during Signup
Scenario: Verify that the signup process does not allow account enumeration
Given url 'http://api.example.com/auth/signup'
And request { username: 'existingUser', password: 'Password123!', email: 'existing@example.com' }
When method post
Then status 200
And match response contains 'A verification email has been sent. Please check your inbox.'
* def signUpNewUser = function(response){ return response.contains('A verification email has been sent. Please check your inbox.') },
* assert signUpNewUser(response) == true
```