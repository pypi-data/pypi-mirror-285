@echo off
start /B python -m http.server 8133
timeout /t 2 > nul
start "" "http://localhost:8133/index.html"