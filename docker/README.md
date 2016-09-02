# How to use Skuld with Docker

There are several options to use Skuld very easily using docker. These are (in order of complexity):

- _"Check the unit tests associated to the component"_. See Section **1. Run Unit Test of Skuld**.
- _"Check the acceptance tests are running properly"_ or _"I want to check that my Skuld instance run properly"_ . See Section **2. Run Acceptance tests**.

You do not need to do all of them, to check if your Skuld instance run properly. You do need to have docker in your machine. See the [documentation](https://docs.docker.com/installation/) on how to do this. Additionally, you can use the proper FIWARE Lab docker functionality to deploy dockers image there. See the [documentation](https://docs.docker.com/installation/).

Docker allows you to deploy a Skuld container in a few minutes. This method requires that you have installed docker or can deploy container into the FIWARE Lab (see previous details about it). Consider this method if you want to try Skuld and do not want to bother about losing data. Follow these steps:

1. Download [Skuld' source code](https://github.com/telefonicaid/fiware-skuld) from GitHub (`git clone https://github.com/telefonicaid/fiware-skuld.git`)
2. `cd fiware-skuld/docker`

----
## 1. Run Unit Test of Skuld

Taking into account that you download the repository from GitHub, this method will launch a container running Skuld, and execute the unit tests associated to the component. You should move to the UnitTests folder `cd UnitTests`. Just create a new docker image executing `docker build -t fiware-skuld-unittests -f Dockerfile .`. Please keep in mind that if you do not change the name of the image it will automatically create a new one for unit tests and change the previous one to tag none.

To see that the image is created run `docker images` and you see something like this:

    REPOSITORY                TAG                 IMAGE ID            CREATED             SIZE
    fiware-skuld-unittests   latest              103464a8ede0        30 seconds ago      551.3 MB

To execute the unit tests of this component, just execute `docker run --name fiware-skuld-unittests fiware-skuld-unittests`. Finally you can extract the information of the executed tests just executing `docker cp fiware-skuld-unittests:/opt/fiware-skuld/test_results .`


> TIP: If you are trying these methods or run them more than once and come across an error saying that the container already exists you can delete it with `docker rm fiware-skuld-unittests`. If you have to stop it first do `docker stop fiware-skuld-unittests`.

Keep in mind that if you use these commands you get access to the tags and specific versions of Skuld. If you do not specify a version you are pulling from `latest` by default.

----
## 2. Run Acceptance tests

Taking into account that you download the repository from GitHub. This method will launch a container to run the E2E tests of the Skuld component, previously you should launch or configure a FIWARE Lab access. You have to define the following environment variables:

    export KEYSTONE_IP=<IP of the keystone instance>
    export ADM_TENANT_ID=<admin tenant id in the OpenStack environment>
    export ADM_TENANT_NAME=<admin tenant name>
    export ADM_USERNAME=<admin username>
    export ADM_PASSWORD=<admin password>
    export Region1=<Region name>
    export OS_USER_DOMAIN_NAME=<OpenStack user domain name>
    export OS_PROJECT_DOMAIN_NAME=<OpenStack project domain name>	

Take it, You should move to the AcceptanceTests folder `cd AcceptanceTests`. Just create a new docker image executing `docker build -t fiware-skuld-acceptance .`. To see that the image is created run `docker images` and you see something like this:

    REPOSITORY                 TAG                 IMAGE ID            CREATED             SIZE
    fiware-skuld-acceptance   latest              eadbe0b2e186        About an hour ago   579.3 MB
    ...

Now is time to execute the container. This time, we take advantage of the docker compose. Just execute `docker-compose up` to launch the architecture. You can take a look to the log generated executing `docker-compose logs`. If you want to get the result of the acceptance tests, just execute `docker cp docker_fiware-skuld-aceptance_1:/opt/fiware-skuld/test/acceptance/testreport .`

Please keep in mind that if you do not change the name of the image it will automatically create a new one for unit tests and change the previous one to tag none.

> TIP: you can launch a FIWARE Lab testbed container to execute the Skuld E2E test. Just follow the indications in [FIWARE Testbed Deploy](https://hub.docker.com/r/fiware/testbed-deploy/). It will launch a virtual machine in which a reproduction of the FIWARE Lab is installed.

----
## 4. Other info

Things to keep in mind while working with docker containers and Skuld.

### 4.1 Data persistence
Everything you do with Skuld when dockerized is non-persistent. *You will lose all your data* if you turn off the Skuld container. This will happen with either method presented in this README.

### 4.2 Using `sudo`

If you do not want to have to use `sudo` follow [these instructions](http://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo).
   
