# -*- coding: utf-8 -*-
Feature: Get the list of users from the IdM.

    Scenario:  01: Get the list of trial users
      Given a user with name "trial1", password "trial" and role "trial"
      Given a user with name "trial2", password "trial" and role "trial"
      Given a user with name "basic1", password "trial" and role "basic"
      When I request a list of trial users from the Keystone
      Then the Keystone returns a list with "2" trial users

    Scenario: 02: Get the list of community users
      Given a user with name "community1", password "password" and role "community"
      Given a user with name "community2", password "password" and role "community"
      Given a user with name "basic1", password "password" and role "basic"
      When I request a list of community users from the Keystone
      Then the Keystone returns a list with "2" community users

    Scenario Outline: 03: Get list of several users
      Given a user with name "<username>", password "<password>" and role "<role>"
      When I request a list of trial users from the Keystone
      Then the Keystone returns a list with "<listtrial>" trial users
      When I request a list of community users from the Keystone
      Then the Keystone returns a list with "<listcommunity>" community users

      Examples:
      | username | password  | role       | listtrial  |  listcommunity |
      | qa1      | fake      | trial      | 1          | 0              |
      | qa2      | fake      | community  | 0          | 1              |
      | qa3      | admin     | basic      | 0          | 0              |
      | qa4      | admin     | community  | 0          | 1              |

    Scenario Outline: 04: Get the list of expired users
      Given a user with name "new", password "new" and role "admin"
      When a user with name "new", password "new" and role "admin" is created
      Then the component return an exception with the message "<message>"

      Examples:
      | tenantName  | username  | password  | message                                            |
      | admin       | fake      | fake      | The request you have made requires authentication. |
