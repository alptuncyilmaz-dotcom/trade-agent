#!/usr/bin/env bash
# setup.sh — Asimetri sistemi tek-komut kurulum (iki repo venv + pip + .env).
# Bu paket içinde repolar (Obsidian Vault + trade-agent) zaten KARDEŞ duruyor.
# Kullanım: paket klasörünün İÇİNDEN:
#   bash setup.sh
# (Repolar başka yerdeyse: bash setup.sh /tam/yol/parent-klasor)
set -e

# Parent = bu script'in bulunduğu klasör (paket içinde repolar KARDEŞ). Argümanla override edilebilir.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT="${1:-$SCRIPT_DIR}"
VAULT="$PARENT/Obsidian Vault"
TRADE="$PARENT/trade-agent"

echo "═══════════════════════════════════════════════"
echo " ASİMETRİ KURULUM — parent: $PARENT"
echo "═══════════════════════════════════════════════"

# --- 0. Önkoşul kontrol ---
command -v python3 >/dev/null || { echo "❌ python3 yok — Python 3.11+ kur (brew install python@3.14)"; exit 1; }
PYV=$(python3 -c 'import sys;print(f"{sys.version_info[0]}.{sys.version_info[1]}")')
echo "✓ python3 $PYV"
[ "$(printf '%s\n3.11' "$PYV" | sort -V | head -1)" = "3.11" ] || echo "⚠️  Python <3.11 — sözdizimi hatası riski (3.11+ önerilir)"

# --- 1. Klasör yapısı kontrol (KRİTİK) ---
[ -d "$VAULT" ] || { echo "❌ '$VAULT' yok. Vault klasörü adı BİREBİR 'Obsidian Vault' olmalı (Adım 2)."; exit 1; }
[ -d "$TRADE" ] || { echo "❌ '$TRADE' yok. Klasör adı BİREBİR 'trade-agent' olmalı, vault ile KARDEŞ."; exit 1; }
echo "✓ klasör yapısı doğru (kardeş)"

# --- 2. trade-agent venv + pip ---
echo "→ trade-agent venv kuruluyor..."
cd "$TRADE"
[ -d .venv ] && echo "  (.venv var, atlanıyor)" || python3 -m venv .venv
./.venv/bin/pip install -q --upgrade pip
./.venv/bin/pip install -q -r requirements.txt
[ -f .env ] || { cp .env.example .env; echo "  .env oluşturuldu (HL_TESTNET_KEY boş bırakılabilir)"; }
echo "✓ trade-agent hazır"

# --- 3. vault data venv + pip ---
echo "→ vault data venv kuruluyor..."
cd "$VAULT/data"
[ -d .venv ] && echo "  (.venv var, atlanıyor)" || python3 -m venv .venv
./.venv/bin/pip install -q --upgrade pip
./.venv/bin/pip install -q -r requirements.txt
if [ ! -f .env ]; then
  cp .env.example .env
  echo "  ⚠️  data/.env oluşturuldu — SEC_USER_AGENT'i KENDİ adın/email'inle doldur (EDGAR 403 vermesin)"
fi
echo "✓ vault data hazır"

# --- 4. doğrulama: trade-agent testleri ---
echo "→ trade-agent testleri çalışıyor..."
cd "$TRADE"
if ./.venv/bin/python -m pytest tests -q 2>/dev/null | tail -1; then
  echo "✓ testler geçti"
else
  echo "⚠️  bazı testler başarısız — KURULUM.md Adım 13 (troubleshooting)"
fi

echo ""
echo "═══════════════════════════════════════════════"
echo " ✅ KURULUM TAMAM"
echo "═══════════════════════════════════════════════"
echo " Sıradaki:"
echo "  1) data/.env içinde SEC_USER_AGENT'i doldur (equity için)"
echo "  2) Kripto turu:  cd \"$TRADE\" && .venv/bin/python capture_snapshot.py && .venv/bin/python run_deterministic.py && .venv/bin/python run_aggressive.py"
echo "  3) Dashboard:    bash \"$VAULT/data/scripts/sync.sh\" && open \"$VAULT/site/index.html\""
echo "  4) LLM kolları (deep-thinker / equity tarama): ilgili repoda Claude Code aç"
echo " Tam rehber: KURULUM.md"
