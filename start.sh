#!/bin/bash

# -----------------------
# ENV CONFIGURATION
# -----------------------
export DD_ENV=${DD_ENV:-dev}
export DD_VERSION=${DD_VERSION:-1.0}
export DD_LOGS_INJECTION=true
export DD_TRACE_AGENT_URL=${DD_TRACE_AGENT_URL:-http://localhost:8126}

# -----------------------
# LOG CONFIGURATION
# -----------------------
export LOG_FORMAT=${LOG_FORMAT:-json}            # json or text
export LOG_OUTPUT=${LOG_OUTPUT:-stdout}          # stdout, file, syslog
export LOG_FILE_PATH=${LOG_FILE_PATH:-/tmp/celery_tasks.log} # file output
export SYSLOG_ADDRESS=${SYSLOG_ADDRESS:-/dev/log}  # '/dev/log' or 'localhost:514'
export LOG_CORRELATED=${LOG_CORRELATED:-true}

# -----------------------
# SHOW CONFIG
# -----------------------
echo "-----------------------------"
echo "DD_ENV:         $DD_ENV"
echo "DD_VERSION:     $DD_VERSION"
echo "LOG_FORMAT:     $LOG_FORMAT"
echo "LOG_OUTPUT:     $LOG_OUTPUT"
echo "LOG_CORRELATED: $LOG_CORRELATED"
if [[ "$LOG_OUTPUT" == "file" ]]; then
  echo "LOG_FILE_PATH:  $LOG_FILE_PATH"
elif [[ "$LOG_OUTPUT" == "syslog" ]]; then
  echo "SYSLOG_ADDRESS: $SYSLOG_ADDRESS"
fi
echo "-----------------------------"

# -----------------------
# START CELERY WORKER
# -----------------------
export DD_SERVICE=celery-worker
echo "Starting Celery Worker as service: $DD_SERVICE"
ddtrace-run celery -A tasks worker --loglevel=info &

WORKER_PID=$!
sleep 2

# -----------------------
# START RUNNER
# -----------------------
export DD_SERVICE=celery-runner
echo "Starting Task Runner as service: $DD_SERVICE"
ddtrace-run python runner.py

# -----------------------
# CLEANUP
# -----------------------
wait $WORKER_PID
