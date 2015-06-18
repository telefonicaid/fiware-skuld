# -*- coding: utf-8 -*-
Feature: Get the list of expired users from the IdM.
    As a fiware lab administrator
    I want to be able to get the list of expired users from the IdM
    so that I can delete the resources associated to them.


    @scenario_01
    Scenario: 01: Verify the obtention of administrator token
      Given a valid tenantName, username and password
      And a connectivity to the Keystone service
      When I request a token to the Keystone
      Then the keystone return me a json message with a valid token


