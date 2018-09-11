#!/bin/sh

set -e

# NOTE: user ID should match ID of the SSH user on the os-services container
adduser --system --disabled-password --ingroup users --shell /bin/false --uid 110 ${SSH_USER}
