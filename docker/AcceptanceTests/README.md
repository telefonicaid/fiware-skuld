# How to use Skuld with Docker

Docker allows you to deploy an Skuld container in a few minutes. This method requires that you have installed docker or can deploy container into the FIWARE Lab (see previous details about it). Consider this method if you want to try Skuld and do not want to bother about losing data. Follow these steps:

1. Download [Skuld' source code](https://github.com/telefonicaid/fiware-skuld) from GitHub (`git clone https://github.com/telefonicaid/fiware-skuld.git`)
2. `cd fiware-skuld/docker`

----
## 1. Run Acceptance tests

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
## 2. Other info

Things to keep in mind while working with docker containers and Skuld.

### 2.1 Data persistence
Everything you do with Skuld when dockerized is non-persistent. *You will lose all your data* if you turn off the Skuld container. This will happen with either method presented in this README.

### 2.2 Using `sudo`

If you do not want to have to use `sudo` follow [these instructions](http://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo).
   
