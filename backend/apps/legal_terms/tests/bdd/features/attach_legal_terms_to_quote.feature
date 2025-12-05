Feature: Attach Legal Terms to Quote
  As a system
  I want to attach legal terms to quotes
  So that every quote has immutable legal terms attached

  Background:
    Given an active legal template exists for jurisdiction "FR"
    And the template has mandatory and optional clauses

  Scenario: Successfully attach legal terms to quote with valid account data
    Given an account with ID "acc-123" exists
    And the account has all required legal fields
    And a legal profile exists for the account
    When I attach legal terms to quote "quote-456"
    Then the legal terms should be successfully attached
    And the attached terms should have a valid snapshot
    And the snapshot should contain all mandatory clauses
    And the snapshot should include the template version
    And the attached terms should be linked to quote "quote-456"

  Scenario: Fail to attach legal terms when template variables are missing
    Given an account with ID "acc-999" exists
    And the account is missing required field "siret"
    When I attempt to attach legal terms to quote "quote-789"
    Then the attach operation should fail
    And a MissingTemplateVariablesError should be raised
    And the error should mention "siret"
    And no attached terms should be created

  Scenario: Fail to attach legal terms when no active template exists
    Given no active legal template exists for jurisdiction "FR"
    And an account with ID "acc-456" exists
    When I attempt to attach legal terms to quote "quote-101"
    Then the attach operation should fail
    And a NoActiveTemplateError should be raised
    And no attached terms should be created

  Scenario: Attach legal terms with profile customizations
    Given an account with ID "acc-789" exists
    And the account has all required legal fields
    And a legal profile exists for the account
    And the profile has custom overrides for clause "warranty"
    When I attach legal terms to quote "quote-202"
    Then the legal terms should be successfully attached
    And the snapshot should reflect the custom overrides
    And the customized clause should have "was_customized" set to true
