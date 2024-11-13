```yaml
feature: Broken Authentication/Authorization on User Registration
scenario: Attempt to register a user without proper authentication or authorization
given url http://192.168.1.106:5080/users/v1/register
when request { username: 'unauthorized_user', password: '', email: '' }
then status 403
and response message contains "Unauthorized" or "Invalid credentials provided."
* def unauthenticatedAttempt = function(response) { return (response.status == 401 || response.message).toLowerCase().includes("unauthorized") }
then unauthenticatedAttempt(response) should be true
```