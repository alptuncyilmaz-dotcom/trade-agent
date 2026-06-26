"""
data/onchain.py — On-chain / pozisyonlanma PROXY katmanı.
Ne yapar: Gerçek on-chain veri (borsa giriş-çıkışları, balina transferleri, likidasyon kümeleri)
          için ücretsiz kaynağımız YOK. Bu modül, eldeki türev verisinden (OI + funding) DÜRÜST bir
          pozisyonlanma proxy'si üretir ve neyin EKSİK olduğunu açıkça işaretler.
Neden:   CLAUDE.md kural 6 (uydurma yok, kaynak zorunlu). Gerçek on-chain için strategy/paid-sources.md'ye
         bakın (F-03 likidasyon kümeleri ücretli). Bu proxy KARAR vermez — yalnız bağlam.
Çıktı:   Saf sözlük; trigger/decision'a girmez (Faz-1 config sabit — kural 7).
"""

# OI'yı sözel sınıfa çevirmek için referans eşik yok (varlığa göre çok değişir); bu yüzden
# proxy, OI'nın MUTLAK değerini ve funding ile birlikte yorumlanacak ham sinyali taşır.

UNAVAILABLE = "ücretsiz-kaynak-yok"  # gerçek on-chain alanları için dürüst işaret


def positioning_proxy(funding_data):
    """OI + funding'den pozisyonlanma proxy'si. funding_data = data.funding.fetch_funding çıktısı.
    Döner: bağlam sözlüğü. 'real' alanları bilinçli olarak UNAVAILABLE — uydurma yok."""
    funding = funding_data.get("funding", 0.0)
    oi = funding_data.get("openInterest", 0.0)
    # funding işareti = ağırlıklı taraf: pozitif → long'lar öder (long kalabalık), negatif → short kalabalık
    crowd = "long-agirlikli" if funding > 0 else ("short-agirlikli" if funding < 0 else "notr")
    return {
        "open_interest": oi,
        "funding_sign": crowd,
        # aşağıdakiler gerçek on-chain ister — şu an yok, uydurulmaz:
        "exchange_flows": UNAVAILABLE,
        "whale_transfers": UNAVAILABLE,
        "liquidation_clusters": UNAVAILABLE,  # F-03, ücretli (paid-sources.md)
        "note": "PROXY: yalnız OI+funding. Gerçek on-chain için paid-sources.md.",
    }
