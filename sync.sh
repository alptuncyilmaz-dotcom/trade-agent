#!/bin/bash
# sync.sh — snapshot tazele + dashboard'u GÜVENLİ sun (yalnız site/, yalnız localhost).
# Güvenlik: kök dizini SUNMA (./.env içerir). Bind 127.0.0.1 — ağa açma.
cd ~/trade-agent
.venv/bin/python capture_snapshot.py
echo "Snapshot guncellendi."
if ! lsof -i:8080 >/dev/null 2>&1; then
  (cd site && python3 -m http.server 8080 --bind 127.0.0.1 >/dev/null 2>&1 &)
  echo "Server baslatildi: http://127.0.0.1:8080/"
else
  echo "Server zaten calisiyor: http://127.0.0.1:8080/"
fi
