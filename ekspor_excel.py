"""Unduh Excel lengkap satu periode.

Lembar:
  Pesanan          format sama dengan REKAP_PEMBELIAN (A1 "TANGGAL", baris 2 tanggal, NAMA | PESANAN) berisi SEMUA tanggal periode,
                   jadi bisa diunggah ulang di tab Impor Excel (menjadi riwayat).
  Makanan          Jenis | Nama | Harga (bisa jadi master) + jumlah porsi & total harga periode + porsi per tanggal.
  Minuman          Nama | Harga (bisa jadi master) + jumlah porsi & total harga periode + porsi per tanggal.
  Pendamping Free  jumlah pendamping gratis per jenis dan per tanggal.
  Ringkasan        total periode dan total per pelanggan (lunas / belum).
"""
from __future__ import annotations

import io
from datetime import date

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

import logic
import orders

KEPALA = PatternFill("solid", fgColor="FFE7B0")
TEBAL = Font(bold=True)
URUT_KAT = {"Nasi": 0, "Ayam Sayur": 1, "Lauk": 2, "Lain-lain": 3, "Pendamping": 4}


def _gratis(item: str, harga: float) -> bool:
    return harga == 0 and item.lower().startswith("free ")


def _ambil(store, kode: str) -> pd.DataFrame:
    df = store.all("Kasbon")
    if df.empty:
        return df
    df = df[(df["periode"] == kode) & (df["status_pesanan"] != "Batal")].copy()
    for c in ("qty", "harga", "subtotal"):
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df


def _kepala(ws, judul: list[str], lebar: list[int]) -> None:
    ws.append(judul)
    for c in ws[1]:
        c.font = TEBAL
        c.fill = KEPALA
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for i, w in enumerate(lebar, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "C2"


def _lembar_pesanan(ws, df: pd.DataFrame) -> None:
    """Format impor: pasangan kolom NAMA | PESANAN per tanggal."""
    tanggal = sorted(df["tanggal"].unique()) if not df.empty else []
    ws["A1"] = "TANGGAL"
    ws["A1"].font = TEBAL
    for j, t in enumerate(tanggal):
        c0 = 1 + j * 2
        sel = ws.cell(row=2, column=c0, value=date.fromisoformat(t))
        sel.number_format = "d mmm yyyy"
        sel.font = TEBAL
        ws.cell(row=3, column=c0, value="NAMA").font = TEBAL
        ws.cell(row=3, column=c0 + 1, value="PESANAN").font = TEBAL
        ws.column_dimensions[get_column_letter(c0)].width = 18
        ws.column_dimensions[get_column_letter(c0 + 1)].width = 42
        r = 4
        for nama, g in sorted(df[df["tanggal"] == t].groupby("pelanggan"), key=lambda x: x[0].lower()):
            biasa = [x for x in g.itertuples() if not _gratis(x.item, x.harga)]
            free = [x for x in g.itertuples() if _gratis(x.item, x.harga)]
            ada_lauk = any(x.kategori in orders.LAUK for x in biasa)
            teks_free = " DAN ".join(x.item[5:].strip().upper() for x in free)      # "Free Sup" -> "SUP"
            dipakai = False
            for x in biasa:
                for _ in range(max(1, int(x.qty))):           # qty > 1 = baris diulang (aturan berkas rekap)
                    teks = x.item.upper()
                    if teks_free and not dipakai and x.kategori in orders.LAUK:
                        teks += f" (FREE {teks_free})"
                        dipakai = True
                    ws.cell(row=r, column=c0, value=nama.upper())
                    ws.cell(row=r, column=c0 + 1, value=teks)
                    r += 1
            if free and not ada_lauk:         # pendamping tanpa lauk: tetap tercatat supaya tidak hilang
                ws.cell(row=r, column=c0, value=nama.upper())
                ws.cell(row=r, column=c0 + 1, value=" + ".join(x.item.upper() for x in free))
                r += 1
    ws.freeze_panes = "A4"


def _per_tanggal(g: pd.DataFrame, tanggal: list[str], ws, baris: int, kol0: int, nama) -> None:
    for j, t in enumerate(tanggal):
        v = int(g[(g["tanggal"] == t)]["qty"].sum())
        if v:
            ws.cell(row=baris, column=kol0 + j, value=v)


def _lembar_makanan(ws, df: pd.DataFrame, store, tanggal: list[str]) -> None:
    _kepala(ws, ["Jenis", "Nama", "Harga", "Porsi periode", "Total harga", "Untuk lauk (khusus Gratis)", ""] +
            [date.fromisoformat(t).strftime("%d/%m") for t in tanggal], [12, 32, 10, 13, 14, 40, 3] + [6] * len(tanggal))
    jual = df[(df["kategori"] != "Minuman") & ~df.apply(lambda x: _gratis(x["item"], x["harga"]), axis=1)] if not df.empty else df
    master = store.all("Menu")
    master = master[(master["kategori"] != "Minuman") & (master["aktif"] != "0")] if not master.empty else master
    baris: dict[str, dict] = {}
    for r in master.itertuples():
        baris[r.nama.lower()] = {"jenis": r.kategori or "Lain-lain", "nama": r.nama, "harga": orders._num(r.harga)}
    for nm, g in (jual.groupby("item") if not jual.empty else []):
        akhir = g.sort_values("tanggal").iloc[-1]
        baris.setdefault(nm.lower(), {"jenis": akhir["kategori"] or "Lain-lain", "nama": nm, "harga": float(akhir["harga"])})
    for b in sorted(baris.values(), key=lambda b: (URUT_KAT.get(b["jenis"], 9), b["nama"].lower())):
        g = jual[jual["item"].str.lower() == b["nama"].lower()] if not jual.empty else jual
        qty, tot = (int(g["qty"].sum()), int(g["subtotal"].sum())) if not g.empty else (0, 0)
        ws.append([b["jenis"], b["nama"], None if b["jenis"] == "Pendamping" else int(b["harga"]), qty or None, tot or None, None, None])
        _per_tanggal(g, tanggal, ws, ws.max_row, 8, b["nama"]) if not g.empty else None
    for lauk_, pend in orders.aturan_gratis(store):        # aturan pendamping gratis (supaya master lengkap)
        ws.append(["Gratis", pend, None, None, None, "" if lauk_ in ("*", "") else lauk_])


def _lembar_minuman(ws, df: pd.DataFrame, store, tanggal: list[str]) -> None:
    _kepala(ws, ["Nama", "Harga", "Harga Jumbo", "Harga + Susu", "Rasa (pisahkan koma)", "Porsi periode", "Total harga"] +
            [date.fromisoformat(t).strftime("%d/%m") for t in tanggal], [34, 10, 13, 14, 20, 13, 14] + [6] * len(tanggal))
    ws.freeze_panes = "B2"
    jual = df[df["kategori"] == "Minuman"] if not df.empty else df
    baris: dict[str, float] = {}
    for r in store.all("Minuman").itertuples():
        nm = " ".join(f"{r.nama} {r.varian}".split())
        if nm:
            baris[nm] = orders._num(r.harga)
    for nm, g in (jual.groupby("item") if not jual.empty else []):
        if nm.lower() not in {k.lower() for k in baris}:
            baris[nm] = float(g.sort_values("tanggal").iloc[-1]["harga"])
    for nm in sorted(baris, key=str.lower):
        g = jual[jual["item"].str.lower() == nm.lower()] if not jual.empty else jual
        qty, tot = (int(g["qty"].sum()), int(g["subtotal"].sum())) if not g.empty else (0, 0)
        ws.append([nm, int(baris[nm]), None, None, None, qty or None, tot or None])
        if not g.empty:
            _per_tanggal(g, tanggal, ws, ws.max_row, 8, nm)


def _lembar_free(ws, df: pd.DataFrame, tanggal: list[str]) -> None:
    _kepala(ws, ["Pendamping Free", "Porsi periode"] + [date.fromisoformat(t).strftime("%d/%m") for t in tanggal],
            [44, 13] + [6] * len(tanggal))
    fr = df[df.apply(lambda x: _gratis(x["item"], x["harga"]), axis=1)] if not df.empty else df
    for nm, g in (fr.groupby("item") if not fr.empty else []):
        ws.append([nm, int(g["qty"].sum())])
        _per_tanggal(g, tanggal, ws, ws.max_row, 3, nm)


def _lembar_ringkasan(ws, df: pd.DataFrame, label: str) -> None:
    ws.column_dimensions["A"].width = 32
    for c in "BCD":
        ws.column_dimensions[c].width = 16
    ws["A1"] = "UNGKEP JOWO · REKAP PEMBELIAN"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A2"] = label
    ws["A3"] = f"Dibuat {logic.today_wib().strftime('%d/%m/%Y')}"
    if df.empty:
        ws["A5"] = "Belum ada pesanan pada periode ini."
        return
    mnm = df["kategori"] == "Minuman"
    ws.append([])
    for k, v in (("Total makanan", df[~mnm]["subtotal"].sum()), ("Total minuman", df[mnm]["subtotal"].sum()),
                 ("TOTAL SEMUA", df["subtotal"].sum()),
                 ("Sudah lunas", df[df["status_bayar"] == "Lunas"]["subtotal"].sum()),
                 ("Belum lunas", df[df["status_bayar"] != "Lunas"]["subtotal"].sum())):
        ws.append([k, int(v)])
        ws.cell(row=ws.max_row, column=2).number_format = '#,##0'
        if k.isupper():
            ws.cell(row=ws.max_row, column=1).font = TEBAL
    ws.append([])
    ws.append(["Pelanggan", "Total", "Lunas", "Belum lunas"])
    for c in ws[ws.max_row]:
        c.font = TEBAL
        c.fill = KEPALA
    for nama, g in sorted(df.groupby("pelanggan"), key=lambda x: x[0].lower()):
        lunas = g[g["status_bayar"] == "Lunas"]["subtotal"].sum()
        ws.append([nama, int(g["subtotal"].sum()), int(lunas), int(g["subtotal"].sum() - lunas)])
        for c in ws[ws.max_row][1:]:
            c.number_format = '#,##0'


def buat_excel(store, kode: str, label: str) -> bytes:
    df = _ambil(store, kode)
    tanggal = sorted(df["tanggal"].unique()) if not df.empty else []
    wb = Workbook()
    _lembar_pesanan(wb.active, df)
    wb.active.title = "Pesanan"
    _lembar_makanan(wb.create_sheet("Makanan"), df, store, tanggal)
    _lembar_minuman(wb.create_sheet("Minuman"), df, store, tanggal)
    _lembar_free(wb.create_sheet("Pendamping Free"), df, tanggal)
    _lembar_ringkasan(wb.create_sheet("Ringkasan"), df, label)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
