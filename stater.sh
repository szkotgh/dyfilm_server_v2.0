#!/bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd -P )"

# Get the path of the script
echo dyfilm server Path=\'$DIR\'
cd "$DIR"

# 시작 시 자동 git pull은 원격 저장소/계정 침해가 재시작마다 자동 실행으로
# 이어지는 공급망 위험이 있어 기본 비활성화한다. 필요 시 DYFILM_AUTO_PULL=1로 활성화.
if [ "${DYFILM_AUTO_PULL:-0}" = "1" ]; then
    if command -v git &> /dev/null
    then
        echo "DYFILM_AUTO_PULL=1: pulling latest changes . . ."
        git pull
    else
        echo "dyfilm server git not found, skipping pull . . ."
    fi
else
    echo "auto git pull disabled (set DYFILM_AUTO_PULL=1 to enable)"
fi

# Start the server
python3 app.py
