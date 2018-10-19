docker build -t donations:0.1 .
bash ./tests.sh
docker stop donations && docker rm -f donations
docker run --restart always --env CR_API_TOKEN=$(cat token) --env INFLUXDB_HOST=influxdb -e INFLUXDB_PORT=8086 -e INFLUXDB_LOGIN=root -e INFLUXDB_PASSWORD=root -e INFLUXDB_DATABASE=clashroyale_stats -e CLAN_TAG=CP28G8V --link influxdb --name donations --detach donations:0.1
docker logs donations
