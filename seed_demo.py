"""Isi data contoh ke folder data/ (hanya untuk uji coba lokal, backend = local)."""
from datetime import timedelta

import logic
import orders
from store import LocalStore

s = LocalStore()
now = logic.now_wib()
iso = now.isoformat(timespec="seconds")
besok = logic.today_wib() + timedelta(days=1)

for n in ["Budi QC", "Erry QC", "Erix Kama", "Sari Admin", "Dewi Packing", "Andi SK"]:
    s.append("Pelanggan", [{"nama": n, "sandi_hash": logic.hash_sandi("ungkep123"), "role": "pelanggan", "aktif": "1", "dibuat": iso}])

M = [("m001", "Nasi", "Nasi", 4000, 2000), ("m002", "Ayam Sayur", "Ayam sayur lengkap", 11000, 7000),
     ("m003", "Lauk", "Dadar telur", 6000, 3500), ("m004", "Lauk", "Mie goreng", 7000, 4500),
     ("m005", "Minuman", "Es teh", 3000, 1000), ("m006", "Minuman", "Es kopi", 5000, 2000),
     ("m007", "Lain-lain", "Kerupuk", 1000, 500), ("m008", "Lain-lain", "Tempe goreng", 2000, 1000)]
s.append("Menu", [{"id": i, "kategori": k, "nama": n, "harga": h, "hpp": p, "aktif": "1"} for i, k, n, h, p in M])
s.append("MenuHarian", [{"tanggal": besok.isoformat(), "menu_id": i, "kategori": k, "nama": n, "harga": h, "hpp": p,
                         "batas_stok": 1 if n == "Ayam sayur lengkap" else 0, "stok": 4 if n == "Ayam sayur lengkap" else "",
                         "alternatif": "Dadar telur" if n == "Ayam sayur lengkap" else ""} for i, k, n, h, p in M])

# riwayat kasbon lama (periode berjalan)
rows = []
for tgl, items in {"2026-10-12": [("Nasi", "Nasi", 1, 4000), ("Ayam Sayur", "Ayam sayur lengkap", 1, 11000)],
                   "2026-10-13": [("Nasi", "Nasi", 1, 4000), ("Ayam Sayur", "Ayam sayur lengkap", 1, 11000), ("Minuman", "Es teh", 1, 3000)]}.items():
    for k, it, q, h in items:
        rows.append({"order_id": f"{tgl}|Budi QC", "tanggal": tgl, "periode": "2026-10", "pelanggan": "Budi QC", "kategori": k, "item": it,
                     "qty": q, "harga": h, "hpp": 0, "subtotal": q * h, "catatan": "", "status_pesanan": "Disetujui", "status_bayar": "Belum", "dibuat": iso})
s.append("Kasbon", rows)

# pesanan untuk menu terbaru (tabel Pesanan Hari Ini)
st = s
orders.simpan_pesanan(st, besok, "Budi QC", {"Nasi": 2, "Ayam sayur lengkap": 2, "Es teh": 1}, "sambal dipisah", langsung=True)
orders.simpan_pesanan(st, besok, "Erix Kama", {"Nasi": 1, "Ayam sayur lengkap": 1, "Kerupuk": 2}, langsung=True)
orders.simpan_pesanan(st, besok, "Sari Admin", {"Ayam sayur lengkap": 1}, langsung=True)
orders.simpan_pesanan(st, besok, "Dewi Packing", {"Es kopi": 1, "Es teh": 1}, langsung=True)
# Budi revisi (menunggu admin)
orders.simpan_pesanan(st, besok, "Budi QC", {"Nasi": 2, "Ayam sayur lengkap": 1, "Dadar telur": 1, "Es teh": 1}, "sambal dipisah", langsung=False)
