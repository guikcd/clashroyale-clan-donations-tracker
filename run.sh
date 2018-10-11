docker build -t donations:0.1 .
bash ./tests.sh
docker run --restart always --link influxdb --name donations --detach donations:0.1
docker logs donations
