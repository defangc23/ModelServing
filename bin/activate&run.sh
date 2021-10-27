docker run --shm-size=8G -d --gpus all \
           -e TZ="Asia/Shanghai" \
           -v /:/mnt \
           -w /mnt/opt/modelserve/ \
           --net=host --name=modelserve_head \
           eum814/modelserve_env:latest \
           conda run -n AlgoExample ray start --head --port=6370 --dashboard-host 0.0.0.0 --block &

sleep 3

docker exec -it modelserve_head /bin/bash -c -i "conda activate AlgoExample&&python --version"
