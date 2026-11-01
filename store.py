"""Lapisan data. Dua backend dengan antarmuka sama: Google Sheets (produksi) dan CSV lokal (uji coba)."""
from __future__ import annotations

import os
import threading
import time
from pathlib import Path

import pandas as pd

def _locked(fn):
    """Serialkan operasi baca-ubah-tulis dalam satu proses server."""
    def wrapper(self, *a, **k):
        with self.lock:
            return fn(self, *a, **k)
    wrapper.__name__ = fn.__name__
    return wrapper


SCHEMA: dict[str, list[str]] = {
    # akun pelanggan + admin (sandi disimpan sebagai hash)
    "Pelanggan": ["nama", "sandi_hash", "role", "aktif", "dibuat"],
    # permintaan reset sandi ("Tanya admin")
    "Permintaan": ["waktu", "nama", "jenis", "status"],
    # daftar menu master (harga bawaan + modal/HPP)
    "Menu": ["id", "kategori", "nama", "harga", "hpp", "aktif"],
    # daftar minuman + varian; kolom ready dicentang admin (otomatis masuk menu harian)
    "Minuman": ["nama", "varian", "harga", "hpp", "ready"],
    # menu yang diunggah admin untuk tanggal tertentu (harga bisa beda dari master)
    "MenuHarian": ["tanggal", "menu_id", "kategori", "nama", "harga", "hpp", "batas_stok", "stok", "alternatif"],
    # REKAP KASBON: satu baris per item yang dipesan (siapa, apa, harga, tanggal, status bayar)
    "Kasbon": ["order_id", "tanggal", "periode", "pelanggan", "kategori", "item", "qty", "harga", "hpp",
               "subtotal", "catatan", "status_pesanan", "status_bayar", "dibuat", "dipesan_oleh"],
    # revisi pesanan dari pelanggan yang menunggu konfirmasi admin (items = JSON daftar item baru)
    "Revisi": ["tanggal", "pelanggan", "jenis", "items", "catatan", "waktu", "status"],
    # pembayaran kasbon: bukti transfer disimpan sebagai foto kecil (base64) di kolom bukti
    "Pembayaran": ["id", "waktu", "pelanggan", "periode", "jumlah", "tagihan", "metode", "status", "bukti", "catatan", "tanggal"],
    # foto bukti bayar ukuran penuh dipecah per potongan (satu sel Google Sheets maks 50.000 karakter)
    "BuktiFoto": ["id", "urut", "data"],
    # pendamping gratis: tiap porsi lauk tertentu otomatis mendapat item pendamping (harga 0). lauk "*" = semua lauk
    "Gratis": ["lauk", "pendamping"],
    # tanggal libur pemesanan (diatur admin)
    "Libur": ["tanggal", "keterangan", "dibuat"],
    "Tutup": ["tanggal", "waktu"],
    "Tanya": ["id", "waktu", "pelanggan", "pertanyaan", "status", "jawaban", "dijawab", "dibaca"],
    # backup tabel "Pesanan Hari Ini" (satu baris per pelanggan per hari)
    "RecordHarian": ["tanggal", "periode", "kelompok", "pelanggan", "pesanan", "jumlah", "status", "dicatat"],
}


class LocalStore:
    """Menyimpan tiap sheet sebagai CSV di folder data/ (untuk uji coba tanpa Google)."""

    def __init__(self, folder: str = "data"):
        self.dir = Path(folder)
        self.dir.mkdir(exist_ok=True)
        self.lock = threading.RLock()

    def _path(self, sheet: str) -> Path:
        return self.dir / f"{sheet}.csv"

    def stamp(self, *sheets: str) -> tuple:
        """Penanda perubahan data: berubah bila salah satu sheet berubah (dipakai untuk memoisasi tampilan)."""
        out = []
        for sh in sheets:
            p = self._path(sh)
            out.append(p.stat().st_mtime_ns if p.exists() else 0)
        return tuple(out)

    def all(self, sheet: str) -> pd.DataFrame:
        p = self._path(sheet)
        if not p.exists():
            return pd.DataFrame(columns=SCHEMA[sheet])
        return pd.read_csv(p, dtype=str, keep_default_na=False)

    def _save(self, sheet: str, df: pd.DataFrame) -> None:
        df.reindex(columns=SCHEMA[sheet]).to_csv(self._path(sheet), index=False)

    @_locked
    def append(self, sheet: str, rows: list[dict]) -> None:
        if not rows:
            return
        df = pd.concat([self.all(sheet), pd.DataFrame(rows).astype(str)], ignore_index=True)
        self._save(sheet, df)

    @_locked
    def replace_where(self, sheet: str, col: str, value: str, rows: list[dict]) -> None:
        df = self.all(sheet)
        df = df[df[col] != str(value)]
        if rows:
            df = pd.concat([df, pd.DataFrame(rows).astype(str)], ignore_index=True)
        self._save(sheet, df)

    @_locked
    def replace_all(self, sheet: str, rows: list[dict]) -> None:
        self._save(sheet, pd.DataFrame(rows, columns=SCHEMA[sheet]).astype(str))

    @_locked
    def update_banyak(self, sheet: str, daftar: list[dict], updates: dict) -> int:
        """Ubah banyak baris sekaligus (satu penyimpanan): setiap elemen `daftar` = syarat satu baris."""
        df = self.all(sheet)
        mask = pd.Series(False, index=df.index)
        for match in daftar:
            m = pd.Series(True, index=df.index)
            for k, v in match.items():
                m &= df[k] == str(v)
            mask |= m
        for k, v in updates.items():
            df.loc[mask, k] = str(v)
        if mask.any():
            self._save(sheet, df)
        return int(mask.sum())

    @_locked
    def update_where(self, sheet: str, match: dict, updates: dict) -> int:
        df = self.all(sheet)
        mask = pd.Series(True, index=df.index)
        for k, v in match.items():
            mask &= df[k] == str(v)
        for k, v in updates.items():
            df.loc[mask, k] = str(v)
        self._save(sheet, df)
        return int(mask.sum())


def _a1(baris: int, kolom: int) -> str:
    huruf = ""
    while kolom:
        kolom, sisa = divmod(kolom - 1, 26)
        huruf = chr(65 + sisa) + huruf
    return f"{huruf}{baris}"


class SheetsStore:
    """Google Sheets lewat gspread, dibuat cepat:
    - semua sesi memakai satu cache di memori server; membaca dari cache tidak memanggil Google;
    - setiap tulisan langsung memperbarui cache (write-through), jadi perubahan satu orang terlihat oleh semua tanpa menunggu;
    - cache yang lewat TTL disegarkan diam-diam di latar belakang (tampilan tidak menunggu), supaya suntingan manual di Sheet ikut terbaca;
    - satu tulisan = satu panggilan API; mengubah status tidak menulis ulang seluruh sheet, hanya sel yang berubah."""

    TTL = 60     # detik: lewat ini cache disegarkan di latar belakang
    FRESH = 30   # detik: dasar penulisan memakai cache bila lebih muda dari ini, kalau tidak baca ulang dulu

    def __init__(self, spreadsheet_id: str, creds: dict):
        import gspread

        self.gc = gspread.service_account_from_dict(creds)
        self.sh = self.gc.open_by_key(spreadsheet_id)
        self._cache: dict[str, tuple[float, pd.DataFrame, list[int]]] = {}   # ts, data, nomor baris di Sheet
        self._ver: dict[str, int] = {}
        self._gen: dict[str, int] = {}
        self._busy: set[str] = set()
        self._ws: dict[str, object] = {}
        self.lock = threading.RLock()
        for name in SCHEMA:
            self._worksheet(name)

    def _worksheet(self, sheet: str):
        if sheet in self._ws:
            return self._ws[sheet]
        import gspread

        try:
            ws = self.sh.worksheet(sheet)
        except gspread.WorksheetNotFound:
            ws = self.sh.add_worksheet(title=sheet, rows=500, cols=len(SCHEMA[sheet]) + 2)
            ws.update([SCHEMA[sheet]], "A1")
        else:
            try:  # samakan judul kolom bila skema bertambah kolom baru
                if ws.row_values(1) != SCHEMA[sheet]:
                    ws.update([SCHEMA[sheet]], "A1")
            except Exception:
                pass
        self._ws[sheet] = ws
        return ws

    def stamp(self, *sheets: str) -> tuple:
        return tuple(self._gen.get(sh, 0) for sh in sheets)

    def _taruh(self, sheet: str, df: pd.DataFrame, rn: list[int], ts: float | None = None) -> None:
        self._cache[sheet] = (time.time() if ts is None else ts, df, rn)
        self._gen[sheet] = self._gen.get(sheet, 0) + 1

    # ---- baca
    def _read(self, sheet: str) -> tuple[pd.DataFrame, list[int]]:
        values = self._worksheet(sheet).get_all_values()
        cols = SCHEMA[sheet]
        rows, rn = [], []
        for i, r in enumerate(values[1:], start=2):
            if any(c != "" for c in r):
                rows.append((r + [""] * (len(cols) - len(r)))[: len(cols)])
                rn.append(i)
        return pd.DataFrame(rows, columns=cols, dtype=str), rn

    def _segarkan_latar(self, sheet: str) -> None:
        if sheet in self._busy:
            return
        self._busy.add(sheet)
        v0 = self._ver.get(sheet, 0)

        def kerja():
            try:
                df, rn = self._read(sheet)
                with self.lock:
                    if self._ver.get(sheet, 0) == v0:   # bila ada tulisan selama membaca, cache sudah lebih baru
                        lama = self._cache.get(sheet)
                        if lama is None or not lama[1].equals(df):
                            self._taruh(sheet, df, rn)
                        else:
                            self._cache[sheet] = (time.time(), lama[1], rn)
            except Exception:
                hit = self._cache.get(sheet)           # gagal: coba lagi sebentar lagi
                if hit:
                    self._cache[sheet] = (time.time() - self.TTL + 10, hit[1], hit[2])
            finally:
                self._busy.discard(sheet)

        threading.Thread(target=kerja, daemon=True).start()

    def all(self, sheet: str) -> pd.DataFrame:
        hit = self._cache.get(sheet)
        if hit is None:
            with self.lock:
                hit = self._cache.get(sheet)
                if hit is None:
                    df, rn = self._read(sheet)
                    self._taruh(sheet, df, rn)
                    hit = self._cache[sheet]
        elif time.time() - hit[0] > self.TTL:
            self._segarkan_latar(sheet)
        return hit[1].copy()

    # ---- tulis (selalu di dalam lock)
    def _dasar(self, sheet: str) -> tuple[pd.DataFrame, list[int]]:
        hit = self._cache.get(sheet)
        if hit and time.time() - hit[0] < self.FRESH:
            return hit[1].copy(), list(hit[2])
        df, rn = self._read(sheet)
        return df, rn

    def _simpan(self, sheet: str, df: pd.DataFrame, baris_lama: int) -> None:
        cols = SCHEMA[sheet]
        df = df.reindex(columns=cols).fillna("").astype(str).reset_index(drop=True)
        data = [cols] + df.values.tolist()
        data += [[""] * len(cols)] * max(0, baris_lama - len(data))   # kosongkan sisa baris lama dalam satu panggilan
        self._worksheet(sheet).update(data, "A1", value_input_option="RAW")
        self._ver[sheet] = self._ver.get(sheet, 0) + 1
        self._taruh(sheet, df, list(range(2, len(df) + 2)))

    @_locked
    def append(self, sheet: str, rows: list[dict]) -> None:
        if not rows:
            return
        cols = SCHEMA[sheet]
        self._worksheet(sheet).append_rows([[str(r.get(c, "")) for c in cols] for r in rows], value_input_option="RAW")
        self._ver[sheet] = self._ver.get(sheet, 0) + 1
        hit = self._cache.get(sheet)
        if hit:
            tambah = pd.DataFrame([{c: str(r.get(c, "")) for c in cols} for r in rows], columns=cols)
            awal = (hit[2][-1] if hit[2] else 1) + 1
            self._taruh(sheet, pd.concat([hit[1], tambah], ignore_index=True), hit[2] + list(range(awal, awal + len(rows))), hit[0])
        else:
            self._gen[sheet] = self._gen.get(sheet, 0) + 1

    @_locked
    def replace_where(self, sheet: str, col: str, value: str, rows: list[dict]) -> None:
        df, rn = self._dasar(sheet)
        n = (rn[-1] if rn else 1)
        df = df[df[col] != str(value)]
        if rows:
            df = pd.concat([df, pd.DataFrame(rows).astype(str)], ignore_index=True)
        self._simpan(sheet, df, n)

    @_locked
    def replace_all(self, sheet: str, rows: list[dict]) -> None:
        df, rn = self._dasar(sheet)
        self._simpan(sheet, pd.DataFrame(rows, columns=SCHEMA[sheet]).astype(str), (rn[-1] if rn else 1))

    @_locked
    def update_where(self, sheet: str, match: dict, updates: dict) -> int:
        df, rn = self._dasar(sheet)
        mask = pd.Series(True, index=df.index)
        for k, v in match.items():
            mask &= df[k] == str(v)
        cols = SCHEMA[sheet]
        sel = []
        for pos in [i for i, m in enumerate(mask.tolist()) if m]:
            for k, v in updates.items():
                if str(df.iat[pos, cols.index(k)]) != str(v):
                    sel.append({"range": _a1(rn[pos], cols.index(k) + 1), "values": [[str(v)]]})
                    df.iat[pos, cols.index(k)] = str(v)
        if sel:   # hanya sel yang berubah, dalam satu panggilan
            ws = self._worksheet(sheet)
            try:
                ws.batch_update(sel, value_input_option="RAW")
            except TypeError:
                ws.batch_update(sel)
            self._ver[sheet] = self._ver.get(sheet, 0) + 1
            self._taruh(sheet, df.reset_index(drop=True), rn)
        return int(mask.sum())

    @_locked
    def update_banyak(self, sheet: str, daftar: list[dict], updates: dict) -> int:
        """Ubah banyak baris sekaligus dalam SATU panggilan ke Google."""
        df, rn = self._dasar(sheet)
        mask = pd.Series(False, index=df.index)
        for match in daftar:
            m = pd.Series(True, index=df.index)
            for k, v in match.items():
                m &= df[k] == str(v)
            mask |= m
        cols = SCHEMA[sheet]
        sel = []
        for pos in [i for i, x in enumerate(mask.tolist()) if x]:
            for k, v in updates.items():
                if str(df.iat[pos, cols.index(k)]) != str(v):
                    sel.append({"range": _a1(rn[pos], cols.index(k) + 1), "values": [[str(v)]]})
                    df.iat[pos, cols.index(k)] = str(v)
        if sel:
            ws = self._worksheet(sheet)
            try:
                ws.batch_update(sel, value_input_option="RAW")
            except TypeError:
                ws.batch_update(sel)
            self._ver[sheet] = self._ver.get(sheet, 0) + 1
            self._taruh(sheet, df.reset_index(drop=True), rn)
        return int(mask.sum())


def make_store(secrets) -> LocalStore | SheetsStore:
    backend = secrets.get("backend", os.environ.get("KASIR_BACKEND", "local"))
    if backend == "sheets":
        return SheetsStore(secrets["spreadsheet_id"], dict(secrets["gcp_service_account"]))
    return LocalStore()
