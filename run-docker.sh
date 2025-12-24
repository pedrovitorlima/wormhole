#!/bin/zsh

echo "Stopping any running containers..."
docker compose down

echo "Building containers from scratch (no cache)..."
docker compose build --no-cache

echo "Starting containers in foreground..."
docker compose up
