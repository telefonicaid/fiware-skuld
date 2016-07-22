Feature: Get the list of expired users from the IdM.

  Scenario: 01: Get resources created for trial
    Given I created several users with values:
    | name      | password | role  |
    | qatrial   | password | trial |
    When a set of resources for the user
    | user_id |  vms | security groups | name |
    | qatrial |  2   | 1               | qa   |
    When I request for showing resources for user "qatrial"
    Then the component returns a list with "1" security groups and "2" vms for user "qatrial"

  Scenario: 02: Get resources created for community
    Given I created several users with values:
    | name    | password | role      |
    | qatrial | password | community |
    When a set of resources for the user
    | user_id |vms  | security groups | name |
    | qatrial |3    | 1               | qa   |
    When I request for showing resources for user "qatrial"
    Then the component returns a list with "1" security groups and "3" vms for user "qatrial"

  Scenario: 03: Get resources created for basic
    Given I created several users with values:
    | name | password | role  |
    | qatrial   | password | basic |
    When a set of resources for the user
    | user_id |vms  | security groups | name |
    | qatrial |2    | 1               | qa   |
    Then the component return an exception with the message "Maximum number of ports exceeded"

  Scenario: 04: Get resources created trial exceeded quotas
    Given I created several users with values:
    | name | password | role  |
    | qatrial   | password | trial |
    When a set of resources for the user
    | user_id |vms  | security groups | name |
    | qatrial |6    | 1               | qa   |
    Then the component return an exception with the message "Quota exceeded for instances: Requested 1, but already used 3 of 3 instances"

  Scenario: 05: Delete VMs
    Given I created several users with values:
    | name | password | role  |
    | qatrial   | password | trial |
    When a set of resources for the user
    | user_id |vms  | security groups | name |
    | qatrial |2    | 0               | qa   |
    When I request for deleting the VMs for user "qatrial"
    When I request for showing resources for user "qatrial"
    Then the component returns a list with "0" security groups and "0" vms for user "qatrial"

  Scenario: 06: Delete security groups
    Given I created several users with values:
    | name    | password | role  |
    | qatrial | password | trial |
    When a set of resources for the user
    | user_id |vms  | security groups | name |
    | qatrial |0    | 2               | qa   |
    When I request for deleting the security groups for user "qatrial"
    When I request for showing resources for user "qatrial"
    Then the component returns a list with "0" security groups and "0" vms for user "qatrial"
