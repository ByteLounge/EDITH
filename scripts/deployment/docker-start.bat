@echo off
echo Starting EDITH PostgreSQL and Core Backend in Docker...
docker-compose up -d --build
echo EDITH services started.
docker-compose ps
