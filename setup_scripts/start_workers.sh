#!/bin/bash

# Start RQ workers
python manage.py rqworker default high low &

# Start RQ scheduler
python manage.py rqscheduler &

echo "Started RQ workers and scheduler"
