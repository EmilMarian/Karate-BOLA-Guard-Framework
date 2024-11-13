Here's the corrected Karate DSL script:
```karate
Feature: Testing for Broken Authentication and Authorization
  Scenario Outline: Verify proper authentication and authorization handling
    Given url 'http://192.168.1.106:5080/users/v1/login'
    Examples:
      | username | password | expected_status | expected_message |
      | admin     | wrongpass | 401            | Incorrect username or password. |
      | nonExist   | correctPass | 401            | Incorrect username or password. |
    And match response contains 'Incorrect username or password.'
```