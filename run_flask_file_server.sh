#!/bin/bash 

if [ $# -gt 0 ]; then
    root=$1
else
    root=$(pwd)
fi

python flask_file_server/server.py --root $root --port 8080
