# PrivateLocationRestart
A python script that will restart a Containerized Private Minion if queue length reaches a defined threshold and create an alertable custom event. Not a panacea for all privation location issues.

## Pre-requisites
* Tested with Python 3.8
* Required Libraries:
  * requests
  * argparse
  * json
  * docker
  * gzip
* New Relic Account
  * Account ID
  * Insights Insert Key
  * User API Key
  * Private Location Key
  * Private Location Name

## Example
Run a single time to test configuration:

`python /path/to/script/minion-restart.py NEW_RELIC_USER_API_KEY -a ACCOUNT_ID -l PRIVATE_LOCATION_NAME -k PRIVATE_LOCATION_KEY -c DOCKER_CONTAINER_NAME -q QUEUE_LENGTH_THRESHOLD -i INSIGHTS_INSERT_API_KEY`

Set it up as a cron job on the private location and go!

## Support
* Issues/Enhancement Requests
Issues and enhancement requests can be submitted in the [Issues tab of this repository](https://github.com/StacySimmons/PrivateLocationRestart/issues). Please search for and review the existing open issues before submitting a new issue.


