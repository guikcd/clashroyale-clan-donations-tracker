import requests
import os
from time import sleep
from influxdb import InfluxDBClient
from datetime import datetime
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

INFLUXDB_HOST = 'influxdb'
INFLUXDB_PORT = 8086
INFLUXDB_LOGIN = 'root'
INFLUXDB_PASSWORD = 'root'
INFLUXDB_DATABASE = 'clashroyale_stats'
CLAN_TAG = "%23CP28G8V"

CURRENT_TIME = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
MEASUREMENT = "donations"

if 'CR_API_TOKEN' not in os.environ:
    logging.error("Please set CR_API_TOKEN")
    exit(1)

while 1:
    logging.info('Get players clan stats for CR api')
    headers = {
            "Accept": "application/json",
            "Authorization": "Bearer {}".format(os.environ['CR_API_TOKEN']),
            }
    request = requests.get('https://api.clashroyale.com/v1/clans/{}/members'.format(CLAN_TAG), headers=headers)
    
    if request.status_code == 200:
    
        logging.info('Connecting to {}:{}/{}'.format(INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_DATABASE))
        client = InfluxDBClient(INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_LOGIN, INFLUXDB_PASSWORD, INFLUXDB_DATABASE)

        jsons = []
        for player in request.json()['items']:
            #print player['name']
            json_body = {
                "measurement": MEASUREMENT,
                "tags": {
                   "player_name": player['name'],
                   "player_tag": player['tag']
                },
                "time": CURRENT_TIME,
                "fields": {
                    "donations": int(player['donations']),
                    "donationsReceived": int(player['donationsReceived'])
                }
            }
            jsons.append(json_body)
    
        #logging.info(jsons)
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
