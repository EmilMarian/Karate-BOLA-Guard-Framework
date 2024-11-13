Feature: Test for Improper Authorization on User Documents Access
    Scenario: Attempt to access user documents without being an 'admin' or 'editor'
        Given url "http://192.168.1.112:3133/api/Users/"
        And header Authorization = "Bearer <regular_user_token>"
        When method post
        Then status 403
        And match response contains "You do not have permission to access this document."