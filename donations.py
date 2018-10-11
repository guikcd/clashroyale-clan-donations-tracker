import requests
import os
from time import sleep
from influxdb import InfluxDBClient
from datetime import datetime
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

INFLUXDB_PORT = 8086
INFLUXDB_LOGIN = 'root'
INFLUXDB_PASSWORD = 'root'
INFLUXDB_DATABASE = 'clashroyale_stats'
CLAN_TAG = "CP28G8V"

MEASUREMENT = "donations"

if 'INFLUXDB_HOST' not in os.environ:
    logging.error("Please set INFLUXDB_HOST")
    exit(1)

if 'CR_API_TOKEN' not in os.environ:
    logging.error("Please set CR_API_TOKEN")
    exit(1)

while 1:
    logging.info('Get players clan stats for CR api')
    headers = {
            "Accept": "application/json",
            "Authorization": "Bearer {}".format(os.environ['CR_API_TOKEN']),
            }
    request = requests.get('https://api.clashroyale.com/v1/clans/%23{}/members'.format(CLAN_TAG), headers=headers)
    
    if request.status_code == 200:
    
        logging.info('Connecting to {}:{}/{}'.format(os.environ['INFLUXDB_HOST'], INFLUXDB_PORT, INFLUXDB_DATABASE))
        client = InfluxDBClient(os.environ['INFLUXDB_HOST'], INFLUXDB_PORT, INFLUXDB_LOGIN, INFLUXDB_PASSWORD, INFLUXDB_DATABASE)

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

        logging.info("Waiting 300s")
        sleep(300)
    
    else:
        logging.error(request.text)

        logging.info("Waiting 300s")
        sleep(300)

        exit(1)
