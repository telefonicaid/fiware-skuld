Changelog
=========

v1.3.0 (2016-07-06)
-------------------
New
~~~
- Add docker files.
- Create docker files to deploy a testing environment of Skuld.
- Add new tests for deployment of two testbeds.
- Add Unit Tests associated to check users and rotated files.
- Separate the management of Skuld Testing Deployment to fiware-testeb-deploy component (https://github.com/telefonicaid/fiware-testbed-deploy/tree/develop).
- Update documentation and README file.

Fix
~~~

- Coding style configuration in Travis CI tool.
- Run test from main folder.
- Fix imports and requirements.
- Generalize Region name in testing environment.
- Obtain public IP from endpoints in the testing environment.

Bug
~~~

- Resolve not service entrypoint for missing FIWARE services.


v1.2.0 (2016-03-07)
-------------------

New
~~~

- Script to install a testbed used by the tests.
- Create script to recover all the user from one region.
- Improve osclients.py

Fix
~~~

- Add docstings to python file.
- Support domain with v3 API and fix Default name.
- Issue/change readme.
- Adding library to the requirements file.

v1.1.0 (2016-02-03)
-------------------

New
~~~

- Improve OSClients
- New tests to cover change_password script
- Adding unit test for nova_resources, change_password and impersonate functionality
- Obtain community & trial users for a region
- Adding coveralls to the repository
- Minor change in description of feature and correction of CI
- Added new tests to cover openstackmap scripts
- Allow multiregion management
- Unit tests for OSClients
- Changing stackoverflow reference and adding support section besides with internal links @minor.
- Classify resources by owner
- Support loading only the declared OpenStack modules
- Configuring travis
- Configuring Sonar to show code quality
- Create jenkins job

Bug
~~~

- Fix a bug introduced in last pull request @minor
- Fix a problem with APIv2 detected implementing Keystone API v3
- Fixing requirements for tests

v1.0.0 (2015-10-01)
-------------------

New
~~~

- Code reorganisation: scripts are adapted to be invoked as an only daily task via cron:

    - Every day users close to expiration are notified (but only once).
    - Every day expired accounts are changed to basic and the users' VMs are stopped.
    - Every day resources of users expired some days ago are definitively cleaned.

- Full documentation at README.
- Lots of bugfixes and improvements in logging.
- Add utility to extract information from report files.
