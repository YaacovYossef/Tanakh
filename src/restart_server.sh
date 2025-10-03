#!/bin/bash

# Tenter de trouver et tuer le processus Flask existant
PID=$(lsof -t -i:5001)
if [ -n "$PID" ]; then
    kill -9 $PID
    echo "Processus Flask (PID: $PID) terminé."
    sleep 2
fi

# Lancer le serveur Flask en arrière-plan
nohup python3 main.py > server.log 2>&1 &
echo "Serveur redémarré à $(date)"
