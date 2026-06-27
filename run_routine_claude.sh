#!/bin/bash
# run_routine_claude.sh — Dosyadaki (ROUTINE.md) A/B/C turunu HEADLESS CLAUDE'a yürüttürür.
# Neden: dosyayla birebir — deep-thinker'ı Claude koşar (analyst + BAĞIMSIZ challenger subagent),
#        haberi WebSearch ile doldurur. API KEY GEREKTİRMEZ (Claude Code girişi).
# A/C kolları yine deterministik script (Claude sadece çağırır) → A/B testi bütünlüğü korunur.
cd /Users/alpyilmaz/trade-agent
set -a
[ -f .env ] && . ./.env
set +a

echo "=== ROUTINE (Claude) BAŞLADI — $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" >> logs/routine.log

claude -p "$(cat ROUTINE_PROMPT.txt)" \
  --allowedTools "Bash,Read,Write,Edit,WebSearch,Task" \
  --permission-mode bypassPermissions \
  --output-format text >> logs/routine.log 2>&1

echo "=== ROUTINE (Claude) BİTTİ — $(date -u +%Y-%m-%dT%H:%M:%SZ) (exit $?) ===" >> logs/routine.log
