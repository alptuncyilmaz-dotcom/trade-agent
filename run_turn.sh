#!/bin/bash
cd ~/Documents/trade-agent
.venv/bin/python run_turn.py >> logs/run.log 2>&1
