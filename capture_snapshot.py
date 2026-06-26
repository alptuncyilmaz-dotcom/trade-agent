"""
capture_snapshot.py — Snapshot giriş noktası (ince sarmalayıcı).
Ne yapar: data/snapshot.py'yi çağırır. Asıl mantık (fetch + gösterge + tetik + rejim) data/'dadır.
Neden:   run_turn.py / run_turn.sh bu dosyayı çağırıyor (geriye uyumluluk). Veri çekme katmanı
         data/ohlcv + data/funding + data/onchain'e ayrıştırıldı; bu giriş onları orkestratör
         data/snapshot üzerinden tetikler.
Çıktı:   state/snapshot_latest.json
"""

from data import snapshot

if __name__ == "__main__":
    snapshot.main()
