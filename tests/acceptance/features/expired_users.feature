Feature: Get the list of expired users from the IdM.

    Scenario: 01: Get the list of expired trial users
      Given an expired user with name "qa1", password "new2" and role "trial"
      Given an expired user with name "qa2", password "new3" and role "trial"
      When I request a list of expired trial users
      Then the component returns a list with "2" expired trial users


    Scenario: 02: Get the list of expired community users
      Given an expired user with name "qa1", password "new2" and role "community"
      Given an expired user with name "qa2", password "new3" and role "community"
      When I request a list of expired community users
      Then the component returns a list with "2" expired community users

     Scenario: 03: several
      Given an expired user with name "qatrial1", password "new2" and role "trial"
      Given a user with name "qatrial2", password "new3" and role "trial"
      Given a user with name "qatrial3", password "new3" and role "trial"
      Given an expired user with name "qacommu1", password "new2" and role "community"
      Given an expired user with name "qacommun2", password "new2" and role "community"
      Given a user with name "qacommun3", password "new2" and role "community"
      When I request a list of expired community users
      Then the component returns a list with "2" expired community users
      When I request a list of expired trial users
      Then the component returns a list with "1" expired trial users