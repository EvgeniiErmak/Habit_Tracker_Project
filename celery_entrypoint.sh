#!/bin/bash

# Delay Celery startup for 10 seconds to allow other services to start
sleep 10

# Start Celery worker
celery -A config worker --loglevel=info --uid=1000
