"""Gambar tagihan: pesanan BELUM LUNAS dan sudah terkonfirmasi pada satu periode (kolom Nama | Tanggal | Total)."""
from __future__ import annotations

import io
from datetime import date

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

import logic

BG, KOP, GARIS, TEKS, SOFT, AKSEN = "#FFF6E5", "#E8742C", "#E9D3B0", "#4A2E14", "#FFE7B0", "#B4491B"
_FONT = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf"]
_FONTB = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"]


def _font(ukuran: int, tebal: bool = False):
    for p in (_FONTB if tebal else _FONT):
        try:
            return ImageFont.truetype(p, ukuran)
        except OSError:
            continue
    return ImageFont.load_default(size=ukuran)       # Pillow >= 10.1: font bawaan berukuran


def data_tagihan(store, kode: str) -> list[tuple[str, list[tuple[date, float]]]]:
    """[(nama, [(tanggal, sisa belum lunas)])]; hanya pesanan terkonfirmasi (bukan batal, bukan revisi/batal yang masih menunggu)."""
    df = store.all("Kasbon")
    if df.empty:
        return []
    df = df[(df["periode"] == kode) & (df["status_pesanan"] != "Batal") & (df["status_bayar"] != "Lunas")].copy()
    df["subtotal"] = pd.to_numeric(df["subtotal"], errors="coerce").fillna(0)
    rv = store.all("Revisi")
    if not rv.empty:
        tunggu = {(r.pelanggan, r.tanggal) for r in rv.itertuples() if r.status == "Menunggu"}
        df = df[[(p, t) not in tunggu for p, t in zip(df["pelanggan"], df["tanggal"])]]
    hasil = []
    for nama, g in df.groupby("pelanggan"):
        per = g.groupby("tanggal")["subtotal"].sum()
        baris = [(date.fromisoformat(t), float(v)) for t, v in sorted(per.items()) if v > 0]
        if baris:
            hasil.append((nama, baris))
    hasil.sort(key=lambda x: x[0].lower())
    return hasil


def buat_gambar(store, kode: str, label: str) -> bytes:
    data = data_tagihan(store, kode)
    W, PAD, RH = 760, 28, 40
    kol = [PAD, PAD + 300, W - PAD]            # nama | tanggal | total (rata kanan)
    n_baris = sum(len(b) + 1 for _, b in data) or 1
    H = 150 + (n_baris + 2) * RH + 60
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    f, fb, fk, fs = _font(22), _font(22, True), _font(30, True), _font(17)
    d.rectangle([0, 0, W, 92], fill=KOP)
    d.text((PAD, 14), "UNGKEP JOWO · TAGIHAN BELUM LUNAS", font=fk, fill="white")
    d.text((PAD, 56), f"{label} · dibuat {logic.today_wib().strftime('%d/%m/%Y')}", font=fs, fill="#FFF0DA")
    y = 108
    d.rectangle([PAD - 8, y, W - PAD + 8, y + RH], fill=SOFT)
    for x, t in zip(kol[:2], ("Nama", "Tanggal")):
        d.text((x, y + 8), t, font=fb, fill=TEKS)
    d.text((kol[2] - d.textlength("Total", font=fb), y + 8), "Total", font=fb, fill=TEKS)
    y += RH
    total = 0.0
    if not data:
        d.text((PAD, y + 10), "Tidak ada tagihan. Semua sudah lunas.", font=f, fill=TEKS)
        y += RH
    for nama, baris in data:
        sub = sum(v for _, v in baris)
        total += sub
        for i, (tgl, v) in enumerate(baris):
            if i == 0:
                d.text((kol[0], y + 8), nama, font=fb, fill=TEKS)
            d.text((kol[1], y + 8), tgl.strftime("%d/%m/%Y"), font=f, fill=TEKS)
            t = logic.rupiah(v)
            d.text((kol[2] - d.textlength(t, font=f), y + 8), t, font=f, fill=TEKS)
            y += RH
            d.line([PAD - 8, y, W - PAD + 8, y], fill=GARIS, width=1)
        t = logic.rupiah(sub)
        d.text((kol[1], y + 8), f"Jumlah {nama}", font=fs, fill=AKSEN)
        d.text((kol[2] - d.textlength(t, font=fb), y + 8), t, font=fb, fill=AKSEN)
        y += RH
        d.line([PAD - 8, y, W - PAD + 8, y], fill=KOP, width=2)
    y += 10
    d.rectangle([PAD - 8, y, W - PAD + 8, y + RH + 6], fill=KOP)
    t = logic.rupiah(total)
    d.text((PAD, y + 9), "TOTAL SEMUA", font=fb, fill="white")
    d.text((kol[2] - d.textlength(t, font=fb), y + 9), t, font=fb, fill="white")
    im = im.crop((0, 0, W, y + RH + 30))
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return buf.getvalue()
