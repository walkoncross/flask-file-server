#!/bin/bash 

if [ $# -gt 0 ]; then
    root=$1
else
    root=$(pwd)
fi

python flask_file_server/server.py --root $root --host 127.0.0.1 --port 8080
