# -*- coding: utf-8 -*-
Feature: Get the list of users from the IdM.

  Scenario:  01: Get the list of trial users
    Given I created several users with values:
    | name     | password | role  |
    | qatrial1 | new2     | trial |
    | qatrial2 | new3     | trial |
    | qabasic  | new3     | basic |
    When I request a list of "trial" users
    Then the component returns a list with "2" users

  Scenario: 02: Get the list of community users
    Given I created several users with values:
    | name         | password | role      |
    | qacommunity1 | new2     | community |
    | qacommunity2 | new3     | community |
    | qabasic      | new3     | basic     |
    When I request a list of "community" users
    Then the component returns a list with "2" users

  Scenario: 03: Get list of several users
    Given I created several users with values:
    | name         | password | role      |
    | qatrial      | new2     | trial     |
    | qacommunity1 | new3     | community |
    | qabasic      | new3     | basic     |
    | qacommunity2 | new3     | community |
    When I request a list of "trial" users
    Then the component returns a list with "1" users
    When I request a list of "community" users from the Keystone
    Then the component returns a list with "2" users
