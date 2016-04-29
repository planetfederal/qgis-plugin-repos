# Settings for the Auth0 endpoint
# Default implementation reads the credentials from .env file
# Alternatively you can also directly set client_domain and client_id
# in this file.

import os

env = None

try:
    from dotenv import Dotenv
    env = Dotenv('./.env')
except IOError:
    env = os.environ


# The following two parameters are mandatory.
client_domain = env["AUTH0_DOMAIN"]
client_id = env["AUTH0_CLIENT_ID"]

# This will be only needed in case we will implement JWT tokens
# (currently not suppported)
#client_secret = env['AUTH0_CLIENT_SECRET']

# This will be only necessary if we are going to perform any administrative
# query or task using v2 API
# (currently not suppported)
#client_token = env["AUTH0_TOKEN"]
