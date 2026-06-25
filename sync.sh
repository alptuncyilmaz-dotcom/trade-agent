#!/bin/bash
cd ~/Documents/trade-agent
.venv/bin/python capture_snapshot.py
echo "Snapshot guncellendi."
echo "Dashboard: http://localhost:8080/site/"
if ! lsof -i:8080 > /dev/null 2>&1; then
  python3 -m http.server 8080 &
  echo "Server baslatildi: http://localhost:8080/site/"
else
  echo "Server zaten calisiyor: http://localhost:8080/site/"
fi
