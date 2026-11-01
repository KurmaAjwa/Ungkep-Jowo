"""Muat data awal (pelanggan, riwayat, menu, minuman) dari data_awal.json ke database yang sedang dipakai."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import logic
import orders

BERKAS = Path(__file__).parent / "data_awal.json"


def ringkasan() -> dict:
    d = json.loads(BERKAS.read_text(encoding="utf-8"))
    return {"pelanggan": len(d["pelanggan"]), "minuman": len(d["minuman"]), "menu": len(d["menu"]),
            "riwayat": len({(r["tanggal"], r["pelanggan"]) for r in d["riwayat"]}),
            "total": sum(r["qty"] * r["harga"] for r in d["riwayat"])}


def muat(store, sandi_awal: str) -> dict:
    """Aman diulang: pelanggan yang sudah ada tidak diubah, riwayat diganti per pesanan, menu master/minuman ditimpa."""
    d = json.loads(BERKAS.read_text(encoding="utf-8"))
    sekarang = logic.now_wib().isoformat(timespec="seconds")

    ada = {n.lower() for n in store.all("Pelanggan")["nama"]}
    baru = []
    for nm in d["pelanggan"]:
        if nm.lower() not in ada:
            ada.add(nm.lower())
            baru.append({"nama": nm, "sandi_hash": logic.hash_sandi(sandi_awal), "role": "pelanggan", "aktif": "1", "dibuat": sekarang})
    store.append("Pelanggan", baru)
    # nama yang diganti (mis. ERIK SK -> ERIK KAMA): akun lama dinonaktifkan agar tidak dobel
    for lama in d.get("pelanggan_diganti", {}):
        store.update_where("Pelanggan", {"nama": lama, "role": "pelanggan"}, {"aktif": "0"})

    store.replace_all("Menu", d["menu"])
    store.replace_all("Minuman", d["minuman"])

    id_menu = {m["nama"]: m["id"] for m in d["menu"]}
    per_tgl: dict[str, list[dict]] = {}
    for r in d["menu_harian"]:
        r = dict(r)
        r["menu_id"] = id_menu.get(r["nama"], "")
        per_tgl.setdefault(r["tanggal"], []).append(r)
    sudah_ada = set(store.all("MenuHarian")["tanggal"])
    for tgl, rows in per_tgl.items():
        # tanggal bertanda "jika kosong" (menu besok) tidak menimpa menu yang sudah diunggah admin
        if tgl in d.get("menu_jika_kosong", []) and tgl in sudah_ada:
            continue
        store.replace_where("MenuHarian", "tanggal", tgl, rows)

    # semua pesanan pada tanggal yang ada di file diganti seluruhnya (aman diulang)
    # catatan: riwayat lama di tanggal itu (mis. revisi menunggu) ikut dibersihkan
    for t in sorted({r["tanggal"] for r in d["riwayat"]}):
        store.replace_where("Revisi", "tanggal", t, [])
    per_tanggal: dict[str, list[dict]] = {}
    pesanan: set[tuple[str, str]] = set()
    for r in d["riwayat"]:
        tgl = date.fromisoformat(r["tanggal"])
        per_tanggal.setdefault(r["tanggal"], []).extend(orders._baris(
            tgl, r["pelanggan"], [{"kategori": r["kategori"], "item": r["item"], "qty": r["qty"], "harga": r["harga"], "hpp": 0}],
            "", "Disetujui", f"{r['tanggal']}T08:00:00+07:00"))
        pesanan.add((r["tanggal"], r["pelanggan"]))
    lunas_lama = {r.order_id for r in store.all("Kasbon").itertuples() if r.status_bayar == "Lunas"}
    for tgl_iso, rows in per_tanggal.items():
        for r in rows:
            if r["order_id"] in lunas_lama:
                r["status_bayar"] = "Lunas"
        store.replace_where("Kasbon", "tanggal", tgl_iso, rows)
    for tgl_iso in sorted({t for t, _ in pesanan}):
        orders.simpan_record(store, date.fromisoformat(tgl_iso), tunggu=True)
    return {"pelanggan_baru": len(baru), "pesanan": len(pesanan), "tanggal": sorted({t for t, _ in pesanan})}
