
# Auth0 setup for plugin repos


The modifications provided in this directory, enable Auth0 authentication for
the plugins in the protected folder (`packages-auth`).

Supported authentication methods are:

- HTTP Basic with username and password
- Authorization Request Header Field access token (Bearer)
- HTTP GET access token passed on the query string as `access_token`
- HTTP POST Form-Encoded Body Parameter access token passed as
  `access_token`


## Configuration


Auth0 credentials are stored in `settings.py` (default implementation reads the
values from an `.env` file).

You can either provide a `.env` file, fill in the correct credentials and store
it in the container as `/var/www/.env` or directly edit the `settings.py` file.

A typical `.env` file looks like this:
```bash
AUTH0_CLIENT_ID=your_client_id
AUTH0_DOMAIN=your_domain.auth0.com
```

## Installation


An `install.sh` script is available in the `auth0` folder. The `install.sh`
script performs the steps described here below.


The `qgis-repo.conf` file contains placeholders for the domain name. You can
replace the placeholders with the domain name that you used to configure
the docker containers with:

```bash
. ../docker-compose.env
sed -i -e "s/domain-tld-dev/${DOMAIN_TLD_DEV}/g" qgis-repo.conf
sed -i -e "s/domain-tld/${DOMAIN_TLD}/g" qgis-repo.conf
```

Copy the files `settings.py`, `main.py` and `qgis-repo.conf` into the container
with `scp`

```bash
scp main.py boundless.test:/var/www
scp settings.py boundless.test:/var/www
scp qgis-repo.conf boundless.test:/home/user
scp REQUIREMENTS.txt boundless.test:/home/user
```

To install the files and restart the services, log into the container with `ssh`
and gain root privleges with `sudo`:
```bash
ssh boundless.test
# Run the following commands in the container
sudo su -
. /opt/venv/bin/activate
pip install -r /home/user/REQUIREMENTS.txt
mv /home/user qgis-repo.conf /etc/nginx/conf.d/
supervisorctl restart app-uwsgi
supervisorctl restart nginx
```


## Testing the endpoints


Please refer to the `README.md` in the top-level folder for detailed
instructions about building the dockers and upload example plugins.

The following endpoint is protected:
https://qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip

### Testing **GET** method with no credentials:

```bash
wget -S --no-check-certificate -O /dev/null 'https://qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip'
HTTP/1.1 401 UNAUTHORIZED
Server: nginx
Date: Wed, 27 Apr 2016 14:09:54 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 90
Connection: keep-alive
WWW-Authenticate: Basic realm="Login Required"
```

### Testing **GET** method with valid credentials

Insert your username and password, if the username contains `@`, encode as `%40`:

```bash
wget -S --no-check-certificate -O /dev/null 'https://your_username%40your_domain.com:your_password@qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip'
HTTP/1.1 200 OK
Server: nginx
Date: Wed, 27 Apr 2016 14:12:07 GMT
Content-Type: application/zip
Content-Length: 5082
Connection: keep-alive
Content-Disposition: attachment; filename=test_plugin_3.0.1.zip
X-Access-Token: XXXXXXXXXXXXX
```

`XXXXXXXXXXXXX` is your access token that can be used to test the `access_token`
authentication.


### Testing **GET** method with invalid **access_token**:

```bash
wget -S --no-check-certificate -O /dev/null 'https://qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip?access_token=wrong_token_here'
HTTP/1.1 401 UNAUTHORIZED
Server: nginx
Date: Wed, 27 Apr 2016 14:20:11 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 90
Connection: keep-alive
WWW-Authenticate: Basic realm="Login Required"
```

### Testing **GET** method with valid **access_token**

Replace `XXXXXXXXXXXXX` with your valid `access_token`

```bash
wget -S --no-check-certificate -O /dev/null 'https://qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip?access_token=XXXXXXXXXXXXX'
HTTP/1.1 200 OK
Server: nginx
Date: Wed, 27 Apr 2016 14:12:07 GMT
Content-Type: application/zip
Content-Length: 5082
Connection: keep-alive
Content-Disposition: attachment; filename=test_plugin_3.0.1.zip
X-Access-Token: XXXXXXXXXXXXX
```


### Testing Authorization Request Header Field access token (Bearer) method with wrong **access_token**

```bash
wget -S --no-check-certificate -O /dev/null --header="Authorization: Bearer wrong_token_here"  'https://qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip'
HTTP/1.1 401 UNAUTHORIZED
Server: nginx
Date: Wed, 27 Apr 2016 14:20:11 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 90
Connection: keep-alive
WWW-Authenticate: Basic realm="Login Required"
```


### Testing Authorization Request Header Field access token (Bearer) method with valid **access_token**

Replace `XXXXXXXXXXXXX` with your valid `access_token`

```bash
wget -S --no-check-certificate -O /dev/null --header="Authorization: Bearer XXXXXXXXXXXXX"  'https://qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip'
HTTP/1.1 200 OK
Server: nginx
Date: Wed, 27 Apr 2016 14:12:07 GMT
Content-Type: application/zip
Content-Length: 5082
Connection: keep-alive
Content-Disposition: attachment; filename=test_plugin_3.0.1.zip
X-Access-Token: XXXXXXXXXXXXX
```

### Testing **POST** method with wrong access_token:

```bash
wget -S --no-check-certificate -O /dev/nul l--post-data="access_token=wrong_token_here" 'https://qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip'
  HTTP/1.1 401 UNAUTHORIZED
  Server: nginx
  Date: Wed, 27 Apr 2016 14:09:54 GMT
  Content-Type: text/html; charset=utf-8
  Content-Length: 90
  Connection: keep-alive
  WWW-Authenticate: Basic realm="Login Required"
```

### Testing **POST** method with valid access_token

Replace `XXXXXXXXXXXXX` with your valid `access_token`

```bash
wget -S --no-check-certificate -O /dev/null --post-data="access_token=XXXXXXXXXXXXX" 'https:/qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip'
HTTP/1.1 200 OK
Server: nginx
Date: Wed, 27 Apr 2016 14:12:07 GMT
Content-Type: application/zip
Content-Length: 5082
Connection: keep-alive
Content-Disposition: attachment; filename=test_plugin_3.0.1.zip
X-Access-Token: XXXXXXXXXXXXX
```
