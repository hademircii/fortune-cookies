#! bin/sh
set -ex

printenv
python cli.py  run-service --interval ${INTERVAL} --server-address ${SERVER_ADDRESS}
