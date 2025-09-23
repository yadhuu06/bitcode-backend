#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Start Redis server in background (if not already running)
if ! pgrep -x "redis-server" > /dev/null
then
    redis-server --daemonize yes
    echo "Redis started"
else
    echo "Redis already running"
fi

# Start Django ASGI server using Daphne
if ! pgrep -f "daphne.*bitWar_backend.asgi:application" > /dev/null
then
    daphne -p 8000 bitWar_backend.asgi:application &
    echo "Daphne started"
else
    echo "Daphne already running"
fi






