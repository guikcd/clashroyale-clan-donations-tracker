import requests
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

API_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImQ4MjFiMDE1LTkzNWItNGJmOC1hYmIyLWJjYTU0MjI5MzgwMSIsImlhdCI6MTUzOTEyMTI5Mywic3ViIjoiZGV2ZWxvcGVyLzMyNzNhOWU5LTVhYTMtMjhlMS1kNzlhLTRjNjk4MjhlNjgyMCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIyMTcuMTc0LjIwOS4xMTUiXSwidHlwZSI6ImNsaWVudCJ9XX0.1SYG4t1zV2KxhOBiSKKIWVYT8cEXv1uA4fiDtt--tzeMCpGRqBorMIaUd89lXeKE9CLdabv6eEBcdl-rtAFSQA"
#API_TOKEN = "aaa"

CURRENT_TIME = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
MEASUREMENT = "donations"

while 1:
    logging.info('Get players clan stats for CR api')
    headers = {
            "Accept": "application/json",
            "Authorization": "Bearer {}".format(API_TOKEN),
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
