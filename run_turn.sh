#!/bin/bash
cd ~/trade-agent
# Gizli anahtarları .env'den yükle (gitignore'lu — repo'ya GİRMEZ). ANTHROPIC_API_KEY burada.
set -a
[ -f .env ] && . ./.env
set +a
.venv/bin/python run_turn.py >> logs/run.log 2>&1
