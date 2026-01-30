CONFIG=$1
GPUS=$2
MODEL_NAME=$(basename "$(dirname "$CONFIG")")

PORT=10902
PYTHON=$(which python)

while :
do
    $PYTHON -m torch.distributed.run \
        --nproc_per_node=$GPUS \
        --master_port=$PORT \
        train.py --c $CONFIG --model $MODEL_NAME

    for PID in $(ps -aux | grep "$CONFIG" | grep python | awk '{print $2}')
    do
        echo "Killing PID $PID"
        kill -9 $PID
    done

    sleep 30
done
