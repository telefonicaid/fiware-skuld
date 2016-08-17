Feature: Get the list of expired users from the IdM.

  Scenario: 01: Saving trial users
    Given I created several users with values:
    | name     | password | role  | expired | notified |
    | qatrial  | password | trial | True    | False    |
    | qatrial1 | password | trial | False   | True     |
    | qatrial2 | password | trial | False   | False    |
    | qatrial3 | password | trial | True    | False     |
    When I request for saving expired "trial" users
    Then I obtain a file with "1" notified users and "2" deleted users
    Then I delete a set of users:
    | name     |
    | qatrial  |
    | qatrial1 |
    | qatrial2 |
    | qatrial3 |

  Scenario: 02: Saving community users
    Given I created several users with values:
    | name         | password | role      | expired | notified |
    | qacommunity  | password | community | True    | False    |
    | qacommunity1 | password | community | False   | True     |
    | qacommunity2 | password | community | False   | True     |
    | qacommunity3 | password | community | False   | False    |
    When I request for saving expired "community" users
    Then I obtain a file with "2" notified users and "1" deleted users
    Then I delete a set of users:
    | name         |
    | qacommunity  |
    | qacommunity1 |
    | qacommunity2 |
    | qacommunity3 |

  Scenario: 03: Get resources created
    Given I created several users with values:
    | name       | password | role   | expired | notified |
    | qatrial1   | password | trial  | True    | False    |
    | qatrial2   | password | trial  | True    | False    |
    | qatrial3   | password | trial  | False   | False    |
    When a set of resources for the user
    | user_id  | vms  | security groups | name       |
    | qatrial1 | 2    | 1               | qa         |
    | qatrial2 | 3    | 1               | qatrial2   |
    | qatrial3 | 2    | 2               | qatrial3   |
    When I request a list of expired yellow-red "trial" users
    Then the component returns a list with "0" yellow users
    Then the component returns a list with "2" red users
    Then the component returns a list with "1" security groups and "2" vms for user "qatrial1"
    Then the component returns a list with "1" security groups and "3" vms for user "qatrial2"
    Then the component returns a list with "2" security groups and "2" vms for user "qatrial3"
    When I request a list of expired "trial" users
    Then the component returns a list with "2" expired users
    When I request a list of expired yellow-red "trial" users
    Then the component returns a list with "0" yellow users
    Then the component returns a list with "2" red users
    When I request for deleting expired "trial" users
    Then the user "qatrial1" has role "basic"
    Then the user "qatrial2" has role "basic"
    Then the user "qatrial3" has role "trial"
    Then the component returns a list with "0" security groups and "0" vms for user "qatrial1"
    Then the component returns a list with "0" security groups and "0" vms for user "qatrial2"
    Then the component returns a list with "2" security groups and "2" vms for user "qatrial3"
    Then I delete a set of users:
    | name     |
    | qatrial1 |
    | qatrial2 |
    | qatrial3 |


