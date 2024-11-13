Here are the Karate DSL test scripts for each scenario:

**Scenario 1: OAuth Token Generation Flaw**
```karate
Feature: Test API for OAuth Token Generation Flaw

Scenario: Attempt to exploit OAuth token generation with a stolen authorization code
Given url 'http://192.168.1.112:8888/workshop/api/merchant/contact_mechanic'
And request {
  grant_type: 'authorization_code',
  code: 'stolen_code',
  redirect_uri: 'http://evil.example.com',
  client_id: 'client_id',
  client_secret: 'client_secret'
}
When method post
Then status 400
And match response contains 'Invalid grant: authorization code is invalid'
```

**Scenario 2: Improper Authorization on User Documents Access**
```karate
Feature: Test for Improper Authorization on User Documents Access

Scenario: Attempt to access a document without being an admin or editor
Given url 'http://192.168.1.112:8888/workshop/api/merchant/contact_mechanic'
And header Authorization = 'Bearer <regular_user_token>'
When method get
Then status 403
And match response contains 'You do not have permission to access this document.'

* def adminAccess = callonce read('classpath:helpers/adminAccess.feature')
* switch adminAccess.status
case 200:
  * assert adminAccess.response == 'Document details'
case 403:
  * fail 'Admin should have access'
```

**Scenario 3: Broken Object Level Authorization on Private Messages**
```karate
Feature: Test API for Broken Object Level Authorization on Private Messages

Scenario: Attempt to send a private message on behalf of another user
Given url 'http://192.168.1.112:8888/workshop/api/merchant/contact_mechanic'
And request {
  senderId: 'user7',
  receiverId: 'user8',
  messageContent: 'Hello from the other side!'
}
And header Authorization = 'Bearer <user7_token>'
When method post
Then status 403
And match response contains 'Unauthorized to send messages as another user.'
```

Note that I've used the provided API endpoint information and added the corresponding URL for each scenario.