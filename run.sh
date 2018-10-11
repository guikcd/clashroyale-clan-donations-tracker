docker build -t donations:0.1 .
bash ./tests.sh
 docker run --restart always --env CR_API_TOKEN=$CR_API_TOKEN --env INFLUXDB_HOST=influxdb --link influxdb --name donations --detach donations:0.1
docker logs donations
