#! bin/sh
set -ex

python cli.py  run-service --interval ${INTERVAL} --filepath ${SOURCE_FILEPATH} \
    --source-format csv
