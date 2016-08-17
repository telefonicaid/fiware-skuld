Feature: Get the list of expired users from the IdM.

  Scenario: 01: Get the list of expired trial users
    Given I created several users with values:
    | name | password   | role  | expired |
    | qa1  |  password1 | trial | True    |
    | qa2  | password2  | trial | True    |
    | qa3  | password2  | trial | False    |
    When I request a list of expired "trial" users
    Then the component returns a list with "2" expired users
    Then I delete a set of users:
    | name  |
    | qa1   |
    | qa2   |
    | qa3   |

  Scenario: 02: Get the list of expired community users
    Given I created several users with values:
    | name | password   | role      | expired |
    | qa1  |  password1 | community | True    |
    | qa2  | password2  | community | True    |
    When I request a list of expired "community" users
    Then the component returns a list with "2" expired users
    Then I delete a set of users:
    | name  |
    | qa1   |
    | qa2   |

  Scenario: 03: several
    Given I created several users with values:
    | name | password | role | expired |
    | qa1trial | new2 | trial | True |
    | qa2trial | new3 | trial | False |
    | qa3trial | new3 | trial | False |
    | qacommu1 | new2 | community | True |
    | qacommu2 | new2 | community | True |
    | qacommu3 | new2 | community | False |
    When I request a list of expired "community" users
    Then the component returns a list with "2" expired users
    When I request a list of expired "trial" users
    Then the component returns a list with "1" expired users
    Then I delete a set of users:
    | name          |
    | qa1trial      |
    | qa2trial      |
    | qa3trial      |
    | qacommu1      |
    | qacommu2      |
    | qacommu3      |

  Scenario: 04: no expired users
    Given I created several users with values:
    | name | password | role | expired |
    | qa1trial | new2 | trial | False |
    | qa2trial | new3 | trial | False |
    | qa3trial | new3 | trial | False |
    | qacommu1 | new2 | community | False |
    | qacommu2 | new2 | community | False |
    | qacommu3 | new2 | community | False |
    When I request a list of expired "community" users
    Then the component returns a list with "0" expired users
    When I request a list of expired "trial" users
    Then the component returns a list with "0" expired users
    Then I delete a set of users:
    | name          |
    | qa1trial      |
    | qa2trial      |
    | qa3trial      |
    | qacommu1      |
    | qacommu2      |
    | qacommu3      |

  Scenario: 05: yellow red trial users
    Given I created several users with values:
    | name | password | role | expired |  notified |
    | qa1trial | new2 | trial | False | True  |
    | qa2trial | new3 | trial | False | True   |
    | qa3trial | new3 | trial | True | False |
    | qa4trial | new3 | trial | True | False |
    | qa5trial | new3 | trial | True | False |
    When I request a list of expired yellow-red "trial" users
    Then the component returns a list with "2" yellow users
    Then the component returns a list with "3" red users
    Then I delete a set of users:
    | name          |
    | qa1trial      |
    | qa2trial      |
    | qa3trial      |
    | qa4trial      |
    | qa5trial      |

  Scenario: 06: yellow red community users
    Given I created several users with values:
    | name | password | role | expired |  notified |
    | qa1trial | new2 | community | False | True  |
    | qa2trial | new3 | community | False | True   |
    | qa3trial | new3 | community | True | True |
    When I request a list of expired yellow-red "community" users
    Then the component returns a list with "2" yellow users
    Then the component returns a list with "1" red users
    Then I delete a set of users:
    | name          |
    | qa1trial      |
    | qa2trial      |
    | qa3trial      |
