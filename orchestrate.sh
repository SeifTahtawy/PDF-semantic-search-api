#!/usr/bin/env bash
set -e

if [[ "$1" != "--action" || -z "$2" ]]; then
    echo "Error: Invalid command usage."
    echo
    echo "Correct usage:"
    echo "  ./orchestrate.sh --action start"
    echo "  ./orchestrate.sh --action terminate"
    exit 1
fi

if [[ "$2" == "start" ]]; then
    docker compose up --build -d
elif [[ "$2" == "terminate" ]]; then
    docker compose down -v --remove-orphans
else
    echo "Error: Invalid action '$2'."
    echo
    echo "Valid actions are:"
    echo "  start"
    echo "  terminate"
    exit 1
fi