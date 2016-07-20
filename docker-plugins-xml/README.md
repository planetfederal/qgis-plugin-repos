# Docker-based QGIS Plugin Repository

This orchestrated setup is for quickly standing up two HTTP(S) endpoints for
simple QGIS plugin repositories (for _release_ and _dev_), then updating them
via SSH by uploading PyQGIS plugin ZIP archives and running a Python updater
script to process the archives. It is particularly useful for processing
automated developer builds of plugins (e.g. from Jenkins or Travis CI).

Uses [docker-compose][dkc] to create images and manage their containers for:

- Service **base** on Debian (`os-services` directory):
  - [Nginx server][ngx] on ports 80 and 443
  - [OpenSSH server][ops] on port 2222
  - Services are run under [supervisord][svd]
- Volume **conf** on busybox (`services-conf` directory):
  - Nginx and SSH configuration
- Volume **data** on busybox (`www-data` directory):
  - Site content and QGIS plugin repo scripts

[dkc]: https://docs.docker.com/compose/
[ngx]: http://nginx.org/
[ops]: http://www.openssh.com/
[svd]: http://supervisord.org/

**IMPORTANT:** This setup requires docker 1.10+ and docker-compose 1.6+. It
_may_ work with previous versions of docker (untested), but _will not work_ with
previous versions of docker-compose.

## Service and Volume Container Layout

Here are the data volume containers and their mounted directory overlays for
each running service:

- From **conf**:
  - /etc/nginx
  - /etc/uwsgi
  - /etc/ssl/nginx
  - /etc/ssh/sshd
  - /home/${SSH_USER}/.ssh

- From **data**
  - /var/www
  - /opt/repo-updater

- Service **base** is overlaid with **conf** and **data**  directories

## Steps to Stand Up a TEST Repository

_Sidebar_: For the terminally lazy, those comfortable with `docker-compose`,
and/or iterative rebuilds, you can use the test scripts (review contents first):

    $> ./test-build.sh
       # run scripts require SSH and hosts file configuration (see below)
    $> ./test-run.sh
       # ... then, after reconfiguring images setups ...
    $> ./test-rebuild-run.sh

### 1. Clone repo

    $> git clone --recursive git@github.com:boundlessgeo/qgis-plugin-repos.git
    $> cd qgis-plugin-repos/docker-plugins-xml

### 2. Build test images

Using [`docker-compose`][dkc], build the images by
_sourcing_ the custom environment first (configured for `bash` shell):

    $> source docker-compose.env

or, if you want to use a custom APT catcher IP address (for example: 172.17.0.2):

    $> CUSTOM_APT_CATCHER_IP=172.17.0.2 source docker-compose.env

Other environment variables are available for services ports customization:

- `CUSTOM_HTTP_PORT` (defaults to 80)
- `CUSTOM_HTTPS_PORT` (defaults to 443)
- `CUSTOM_SSH_PORT` (defaults to 2222)

Then, build the images. See `docker-compose build --help`

    $> docker-compose build

This should give you the following similar test images:

    $> docker images
    REPOSITORY        TAG     ...  SIZE
    qgisrepo_base     latest  ...  428.5 MB
    qgisrepo_conf     latest  ...  1.199 MB
    qgisrepo_data     latest  ...  2.252 MB

### 3. Run test containers

When running the containers, only the **base** container will remain up, this is
because the other containers merely provide [data volumes][dvl] that offer
separation of the services from their configuration and content. This is a
general docker design idiom and allows the data volumes to be accessed
separately by multiple services, for example a service to back up the data.

[dvl]: https://docs.docker.com/engine/userguide/containers/dockervolumes/

See `docker-compose up --help`

    $> docker-compose up  -d
    Creating network "qgisrepo_default" with the default driver
    Creating qgisrepo_data_1
    Creating qgisrepo_conf_1
    Creating qgisrepo_base_1

This should give you the following similar test containers:

    $> docker ps -a
    ...  IMAGE             ...  STATUS  PORTS           NAMES
    ...  qgisrepo_base     ...  Up      80->80/tcp,
                                        443->443/tcp
                                        2222->2222/tcp  qgisrepo_base_1
    ...  qgisrepo_conf     ...  Exited                  qgisrepo_conf_1
    ...  qgisrepo_data     ...  Exited                  qgisrepo_data_1

Logs for the **base** container should look similar to:

    $ docker logs qgisrepo_base_1
    ... CRIT Supervisor running as root (no user in config file)
    ... WARN Included extra file "/etc/supervisor/conf.d/services.conf" during parsing
    ... INFO RPC interface 'supervisor' initialized
    ... CRIT Server 'unix_http_server' running without any HTTP authentication checking
    ... INFO supervisord started with pid 1
    ... INFO spawned: 'app-uwsgi' with pid 10
    ... INFO spawned: 'nginx' with pid 11
    ... INFO spawned: 'sshd' with pid 12
    ... INFO success: app-uwsgi entered RUNNING state, process has stayed up for > than 5 seconds (startsecs)
    ... INFO success: nginx entered RUNNING state, process has stayed up for > than 5 seconds (startsecs)
    ... INFO success: sshd entered RUNNING state, process has stayed up for > than 5 seconds (startsecs)


### 4. Get docker machine's IP address

On Linux, the IP address is:

    $> docker inspect --format '{{ .NetworkSettings.Networks.qgisrepo_default.IPAddress }}' qgisrepo_base_1

If using `docker-machine` on OSX and Win (or some Linux setups), docker runs in
a thin VirtualBox or VMware virtual machine and is managed by the
`docker-machine` utility, with the default machine name called 'default'.

It's IP address can be obtained with the following command:

    $> docker-machine ip $(docker-machine active)

or, if the docker machine's environment has already been sourced:

    $> docker-machine ip $DOCKER_MACHINE_NAME

### 5. Update hosts file

NOTE: if using a VM via recent versions of the `docker-machine` utility, your VM
may essentially have a _static_ local IP address.

To try out the preconfigured SSH server and wildcard test SSL certificate, add
the following to your `hosts` file:

    <docker-machine-ip> boundless.test
    <docker-machine-ip> qgis.boundless.test
    <docker-machine-ip> qgis-dev.boundless.test

### 6. Configure SSH client

Add test SSH private key to your SSH config directory:

    $> cp services-conf/resources/test-ssh-keypair/boundless_test_id_rsa ~/.ssh/
    $> chmod 0600 ~/.ssh/boundless_test_id_rsa

Add an SSH configuration for the boundless.test repo (see [ssh_config][shc])

    Host boundless.test
      HostName boundless.test  <-- or docker-machine's IP
      Port 2222
      User user
      IdentityFile ~/.ssh/boundless_test_id_rsa

[shc]: http://www.openssh.com/manual.html

Note: The SSH host fingerprint will change if you _rebuild_ the **base** image.
You will need to remove the `[boundless.test]:2222 ...` line from your
`~/.ssh/known_hosts` file, else receive a WARNING (and failed connection) using
your SSH client.

### 7. Test SSH access

Running the following should produce a similar prompt:

    $> ssh boundless.test

    The programs included with the Debian GNU/Linux system are free software;
    ...
    user@b374d2418324:~$

The default `user` has a password of `pass`, which can be used to elevate
permissions using `sudo`.

### 8. Populate the repositories with test plugins

Run the SSH-based remote loading script for the test plugins:

    $> ./www-data/resources/plugins-xml/test/remote-load-test-plugins.sh
    test_plugin_1.zip     100% 2768     2.7KB/s   00:00
    ...
    test_plugin_3.zip     100% 2972     2.9KB/s   00:00

This will load 3 test plugins into both the `release` and `dev` repositories,
with `test_plugin_3` loaded as "download authenticated" restricted plugin.

Note: this also sets up some basic web files for the `release` and `dev` sites.

### 9. Test access to HTTP endpoints

Go to:

- <http://qgis.boundless.test/>
- <http://qgis-dev.boundless.test/>

Should produce a _blank page_, with no error.

Go to:

- <http://qgis.boundless.test/plugins/plugins.xml>
- <http://qgis-dev.boundless.test/plugins/plugins.xml>

Should produce a listing of 3 plugins. Each download link should download the
appropriate ZIP archive, with the `test_plugin_3.zip` download requiring
authentication:

- username: user or dev _(relative to repo)_
- password: password

### 10. Test access to HTTPS endpoints

Note: you should already have '*.boundless.test' domains set up in your `hosts`
file as noted above, else the test SSL setup _will not function_.

Add the following test root Certificate Authority for your browser:

[services-conf/resources/nginx/ssl-test/boundless-root-ca.pem][bca]

[bca]: ./services-conf/resources/nginx/ssl-test/boundless-root-ca.pem

The server's certificate is signed by an issuing chain with a self-signed root
test certificate, so you need to set the imported "Boundless Test Root CA"
certificate to trusted.

Go to HTTPS URLs and verify the same results as with HTTP access above:

- <https://qgis.boundless.test/>
- <https://qgis.boundless.test/plugins/plugins.xml>
- <https://qgis-dev.boundless.test/>
- <https://qgis-dev.boundless.test/plugins/plugins.xml>

Additionally, the connection should be secured with a `*.boundless.test`
wildcard certificate and there should be no SSL errors.


#### Fully automated tests

The directory `tests` contains a python test script that can be used
to test the dockerized repository created with `test-build.run load`
as explained in the [base manual][mdr].
The list of Python requirements for the test script can be found in the file
`resources/REQUIREMENTS.txt`.

Start the tests from the command line with:

    $> python endpoint_tests.py

## Plugin Repository Updating/Editing

See the [README for the Python updater script][rus] in the **qgis-plugins-xml** code repository.

[rus]: https://github.com/boundlessgeo/qgis-plugins-xml

### Manual editing of `plugins.xml`

If you are on the docker host, log into the running repo's **base** container:

    $ docker exec -it -t qgisrepo_base_1 bash -l
    root@62696a0fa3aa:/# nano /var/www/qgis/plugins/plugins.xml

Otherwise, log in via a remote SSH connection.

## Customization

Review/edit the [docker-compose.env][dke] file for customization of the build
environment.

[dke]: ./docker-compose.env

Edit files under [services-conf/resources][svc] to configure **conf** image.

[svc]: ./services-conf/resources/

Edit files under [www-data/resources][wdr] to configure **data** image.

[wdr]: ./www-data/resources/

To create HTTP Basic Auth user:passwords, you can use (e.g. Apache MD5):

    printf "USER:$(openssl passwd -apr1 PASSWORD)\n" >> htpasswd_file

See also [notes on htpasswd in Nginx FAQs][nfq].

[nfq]: https://www.nginx.com/resources/wiki/community/faq/

To use a custom SSL certificate/key for Nginx, see
[services-conf/resources/ssl-custom-cert/README.md][scc]

[scc]: ./services-conf/resources/ssl-custom-cert/README.md

## Deployment

**WARNING:** This is mostly for testing. If you use this setup for a live
production repository, you will need to do additional security hardening.

If you intend to use this setup in a production deployment, consider _not_ using
`docker-compose down -v`, as this will _ERASE the contents_ on your **data**
container. Once you have done `docker-compose build`, manage your containers
_separately_ as recommended in the documentation, see:

- [Overview of Docker Compose][odc]
- [Using Compose in production][ucp]

[odc]: https://docs.docker.com/compose/overview/
[ucp]: https://docs.docker.com/compose/production/

Example scripts are provided to backup and upgrade a running repository:

- [repo-www-backup.sh][rbu] - backs up running repo's `/var/www/qgis*` data to
  `qgis-repo-www-backup_$(date +%Y%m%d-%H%M%S).tgz`
- [repo-www-upgrade.sh][rup] - upgrades a running repo, backing up its
  `/var/www/qgis*` data, then restoring it after upgrade

[rbu]: ./repo-www-backup.sh
[rup]: ./repo-www-upgrade.sh


## Auth0 setup

See the `README.md` file in `auth0` folder.
