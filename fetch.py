import requests
import json
import os
from time import sleep, time
import logging

# clan tag without "#"
CLAN_TAG = "CP28G8V"

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

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
        data = request.json()
        with open('{}.json'.format(int(time())), 'w') as f:
            json.dump(data, f)

        logging.info("Waiting 300s")
        sleep(300)
    
    else:
        logging.error(request.text)

        logging.info("Waiting 300s")
        sleep(300)

        exit(1)
