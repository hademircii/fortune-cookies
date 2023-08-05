#! bin/sh
set -ex

python cli.py  run-service --interval ${INTERVAL} --server-address ${SERVER_ADDRESS}
