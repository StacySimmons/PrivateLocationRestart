import requests
import argparse
import json
import docker
import gzip


def main():

    # parse arguments passed by command line
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('apikey', help='New Relic API Key')
    parser.add_argument('-a', '--accountid', help='New Relic Account ID')
    parser.add_argument('-l', '--locationname', help='New Relic Private Location Name')
    parser.add_argument('-k', '--locationkey', help='New Relic Private Location Key')
    parser.add_argument('-c', '--containername', help='Name of CPM Docker Container')
    parser.add_argument('-q', '--queuelimit', help='Integer representing restart/rebuild threshold')
    parser.add_argument('-i', '--insightsapikey', help='New Relic Insights Insert API Key')

    args = parser.parse_args()
    api_key = args.apikey
    account_id = args.accountid
    location_name = args.locationname
    location_key = args.locationkey
    container_name = args.containername
    queue_limit = int(args.queuelimit)
    insights_key = args.insightsapikey
    random_var = 5

    event_type = 'CPMRestart'

    headers = {
        'Content-Type': 'application/json',
        'API-Key': api_key,
    }

    query = '{"query":"{\\n actor {\\n account(id: ' + str(account_id) + ') {\\n nrql(query: \
    \\"SELECT latest(checksPending) as \'checks_pending\' FROM SyntheticsPrivateLocationStatus where name = \\u0027' + \
            location_name + '\\u0027\\") {\\n results\\n }\\n }\\n }\\n}\\n", "variables":""}'

    response = requests.post('https://api.newrelic.com/graphql', headers=headers, data=query)

    if response.status_code == 200:
        c = json.loads(response.text)
        checks_pending = int(c['data']['actor']['account']['nrql']['results'][0]['checks_pending'])

        if checks_pending is not None and checks_pending > queue_limit:
            if checks_pending > queue_limit:
                # start auto-remediation here
                client = docker.from_env()
                try:
                    container = client.containers.get(container_name)
                    container.restart()
                    action = "RESTART"
                except (docker.errors.APIError, docker.errors.NotFound) as e:
                    print(e)
                    print('Trying reinstall...')
                    try:
                        container = client.containers.run('quay.io/newrelic/synthetics-minion:latest',
                                                          environment=['MINION_PRIVATE_LOCATION_KEY=' + location_key],
                                                          volumes={'/tmp': {'bind': '/tmp', 'mode': 'rw'},
                                                                   '/var/run/docker.sock': {
                                                                       'bind': '/var/run/docker.sock', 'mode': 'rw'}
                                                                   },
                                                          name=container_name,
                                                          restart_policy={"Name": "unless-stopped", "MaximumRetryCount": 0},
                                                          detach=True)
                        action = "REINSTALL"
                    except (docker.errors.APIError, docker.errors.NotFound, docker.errors.ContainerError) as e:
                        print(e)
                        action = "REMEDIATION FAILED"
                # HERE WILL BE CUSTOM EVENTS
                custom_event_data = {'eventType': 'PrivateMinionRestarts', 'action': action,
                                     'locationName': location_name}
                custom_event_json = json.dumps(custom_event_data)
                b = custom_event_json.encode('utf-8')
                b_zipped = gzip.compress(b)

                headers = {
                    'Content-Type': 'application/json',
                    'X-Insert-Key': insights_key,
                    'Content-Encoding': 'gzip',
                }
                try:
                    response = requests.post('https://insights-collector.newrelic.com/v1/accounts/' + account_id + '/events', headers=headers, data=b_zipped)
                    print(response.reason)
                except requests.exceptions.RequestException as e:
                    print(e)

    else:
        print(str(response.status_code) + ' response received: ' + response.reason)


if __name__ == '__main__':
    main()

