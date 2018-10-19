import requests
import os
from time import sleep
from influxdb import InfluxDBClient
from datetime import datetime
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

ENV_VARS = ['INFLUXDB_HOST', 'INFLUXDB_PORT', 'INFLUXDB_LOGIN', 'INFLUXDB_PASSWORD', 'INFLUXDB_DATABASE', 'CR_API_TOKEN', 'CLAN_TAG']

def _required_vars():
    for var in ENV_VARS:
        if var not in os.environ:
           logging.error("Please set {}".format(var))
           exit(1)

MEASUREMENT = "donations"
SLEEP_SECONDS = 300

_required_vars()

while 1:
    logging.info('Get players clan stats for CR api')
    headers = {
            "Accept": "application/json",
            "Authorization": "Bearer {}".format(os.environ['CR_API_TOKEN']),
            }
    request = requests.get('https://api.clashroyale.com/v1/clans/%23{}/members'.format(os.environ['CLAN_TAG']), headers=headers)
    
    if request.status_code == 200:
    
        logging.info('Connecting to {}:{}/{}'.format(os.environ['INFLUXDB_HOST'], os.environ['INFLUXDB_PORT'], os.environ['INFLUXDB_DATABASE']))
        client = InfluxDBClient(os.environ['INFLUXDB_HOST'], os.environ['INFLUXDB_PORT'], os.environ['INFLUXDB_LOGIN'], os.environ['INFLUXDB_PASSWORD'], os.environ['INFLUXDB_DATABASE'])

        jsons = []
        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        for player in request.json()['items']:
            json_body = {
                "measurement": MEASUREMENT,
                "tags": {
                   "player_name": player['name'].replace(' ', '_'),
                   "player_tag": player['tag']
                },
                "time": current_time,
                "fields": {
                    "donations": int(player['donations']),
                    "donationsReceived": int(player['donationsReceived'])
                }
            }
            jsons.append(json_body)
    
        logging.info("Writing data to influxdb ({} records)".format(len(jsons)))
        client.write_points(jsons)

        logging.info("Closing influxdb connection")
        client.close()
    
    else:
        logging.error(request.text)
        exit(1)

    logging.info("Waiting {}s".format(SLEEP_SECONDS))
    sleep(SLEEP_SECONDS)

