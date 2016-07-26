Feature: Get the list of expired users from the IdM.

  Scenario: 01: Get the list of expired trial users
    Given I created several users with values:
    | name | password   | role  | expired |
    | qa1  |  password1 | trial | True    |
    | qa2  | password2  | trial | True    |
    | qa3  | password2  | trial | False    |
      When I request a list of expired "trial" users
      Then the component returns a list with "2" expired users


    Scenario: 02: Get the list of expired community users
       Given I created several users with values:
       | name | password   | role      | expired |
       | qa1  |  password1 | community | True    |
       | qa2  | password2  | community | True    |
      When I request a list of expired "community" users
      Then the component returns a list with "2" expired users

    Scenario: 03: several
      Given I created several users with values:
     | name | password | role | expired |
     | qatrial1 | new2 | trial | True |
     | qatrial2 | new3 | trial | False |
     | qatrial3 | new3 | trial | False |
     | qacommu1 | new2 | community | True |
     | qacommu2 | new2 | community | True |
     | qacommu3 | new2 | community | False |
      When I request a list of expired "community" users
      Then the component returns a list with "2" expired users
      When I request a list of expired "trial" users
      Then the component returns a list with "1" expired users

    Scenario: 04: no expired users
      Given I created several users with values:
     | name | password | role | expired |
     | qatrial1 | new2 | trial | False |
     | qatrial2 | new3 | trial | False |
     | qatrial3 | new3 | trial | False |
     | qacommu1 | new2 | community | False |
     | qacommu2 | new2 | community | False |
     | qacommu3 | new2 | community | False |
      When I request a list of expired "community" users
      Then the component returns a list with "0" expired users
      When I request a list of expired "trial" users
      Then the component returns a list with "0" expired users

    Scenario: 05: yellow red trial users
      Given I created several users with values:
      | name | password | role | expired |  notified |
      | qatrial1 | new2 | trial | False | True  |
      | qatrial2 | new3 | trial | False | True   |
      | qatrial3 | new3 | trial | True | False |
      | qatrial4 | new3 | trial | True | False |
      | qatrial5 | new3 | trial | True | False |
      When I request a list of expired yellow-red "trial" users
      Then the component returns a list with "2" yellow users
      Then the component returns a list with "3" red users

    Scenario: 06: yellow red community users
      Given I created several users with values:
      | name | password | role | expired |  notified |
      | qatrial1 | new2 | community | False | True  |
      | qatrial2 | new3 | community | False | True   |
      | qatrial3 | new3 | community | True | True |
      When I request a list of expired yellow-red "community" users
      Then the component returns a list with "2" yellow users
      Then the component returns a list with "1" red users
