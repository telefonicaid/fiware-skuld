# -*- coding: utf-8 -*-
Feature: Get the list of expired users from the IdM.
    As a fiware lab administrator
    I want to be able to get the list of expired users from the IdM
    so that I can delete the resources associated to them.


    @basic
    Scenario: 01: Verify the obtention of administrator token
      Given a valid tenantName, username and password
      And a connectivity to the Keystone service
      When I request a valid token from the Keystone
      Then the keystone return me a json message with a valid token

    Scenario: 02: Get the list of trial users
      Given a valid token from the Keystone
      When I request a list of trial users from the Keystone
      Then the Keystone returns a list with all the trial users registered

    Scenario: 03: Get the list of expired users
      Given a valid token from the Keystone
      And a list of trial users from the Keystone
      When I request a list of expired users
      Then the component returns a list with all the expired trial users

    Scenario Outline: 04: Request a token with invalid data
      Given a wrong "<tenantName>", "<username>" and "<password>"
      And a connectivity to the Keystone service
      When I request a valid token from the Keystone
      Then the component return an exception with the message "<message>"

      Examples:
      | tenantName  | username  | password  | message                                            |
      | admin       | fake      | fake      | The request you have made requires authentication. |
      | fake        | admin     | fake      | The request you have made requires authentication. |
      | admin       | admin     | fake      | The request you have made requires authentication. |

