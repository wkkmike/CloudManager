cp orgin.yml docker-compose.yml
etcdctl del --prefix ""
docker-compose stop
docker kill $(docker ps -a -q)
