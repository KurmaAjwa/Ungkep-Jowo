"""Penyimpanan: Google Sheets (produksi) atau file CSV lokal (mode percobaan)."""
from __future__ import annotations

import threading
import time
from pathlib import Path

import pandas as pd

SKEMA: dict[str, list[str]] = {
    "pelanggan": ["nama", "sandi", "aktif", "dibuat"],
    "menu_master": ["id", "nama", "kategori", "harga", "hpp", "aktif"],
    "menu_harian": ["tanggal", "menu_id", "nama", "kategori", "harga", "stok", "alternatif", "diunggah"],
    # Kolom depan sengaja dibuat mudah dibaca (rekap kasbon); kolom JSON di belakang.
    "pesanan": [
        "tanggal", "nama", "rincian", "total", "periode", "status_bayar", "tgl_bayar",
        "status", "revisi", "dibungkus", "catatan", "id", "items", "items_baru",
        "catatan_baru", "dibuat", "diubah",
    ],
    "permintaan": ["id", "nama", "jenis", "waktu", "status"],
}
KOLOM_ANGKA = {"total", "harga", "hpp", "stok"}
KUNCI = threading.RLock()  # Streamlit berjalan 1 proses; kunci ini mencegah tulis bersamaan
TTL = 8  # detik cache baca (hemat kuota API Google)


class Store:
    def __init__(self):
        self._cache: dict[str, tuple[float, pd.DataFrame]] = {}

    # --- diimplementasi turunan ---
    def _baca(self, tab: str) -> pd.DataFrame:  # pragma: no cover
        raise NotImplementedError

    def _tulis(self, tab: str, df: pd.DataFrame) -> None:  # pragma: no cover
        raise NotImplementedError

    # --- API ---
    def read(self, tab: str, segar: bool = False) -> pd.DataFrame:
        t = self._cache.get(tab)
        if t and not segar and time.time() - t[0] < TTL:
            return t[1].copy()
        df = self._baca(tab)
        self._cache[tab] = (time.time(), df)
        return df.copy()

    def update(self, tab: str, fn):
        """Baca data terbaru -> fn(df) -> tulis, di bawah kunci. fn boleh mengembalikan df atau (df, hasil)."""
        with KUNCI:
            df = self.read(tab, segar=True)
            out = fn(df)
            hasil = None
            if isinstance(out, tuple):
                df, hasil = out
            else:
                df = out
            df = rapikan(tab, df)
            self._tulis(tab, df)
            self._cache[tab] = (time.time(), df)
            return hasil

    @property
    def nama(self) -> str:
        return "?"


def rapikan(tab: str, df: pd.DataFrame) -> pd.DataFrame:
    cols = SKEMA[tab]
    df = df.copy()
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    df = df[cols].fillna("")
    for c in cols:
        if c in KOLOM_ANGKA:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
        else:
            df[c] = df[c].astype(str)
    return df.reset_index(drop=True)


class LocalStore(Store):
    def __init__(self, folder: str | Path):
        super().__init__()
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)

    @property
    def nama(self) -> str:
        return "lokal"

    def _baca(self, tab):
        p = self.folder / f"{tab}.csv"
        if not p.exists():
            return rapikan(tab, pd.DataFrame(columns=SKEMA[tab]))
        return rapikan(tab, pd.read_csv(p, dtype=str, keep_default_na=False))

    def _tulis(self, tab, df):
        tmp = self.folder / f"{tab}.csv.tmp"
        df.to_csv(tmp, index=False)
        tmp.replace(self.folder / f"{tab}.csv")


class SheetsStore(Store):
    def __init__(self, creds: dict, sheet_id: str):
        super().__init__()
        import gspread

        self.gc = gspread.service_account_from_dict(dict(creds))
        self.sh = self.gc.open_by_key(sheet_id)
        self._ws = {}
        ada = {w.title: w for w in self.sh.worksheets()}
        for tab, cols in SKEMA.items():
            if tab in ada:
                ws = ada[tab]
            else:
                ws = self.sh.add_worksheet(title=tab, rows=200, cols=max(len(cols), 8))
                ws.update([cols], value_input_option="RAW")
            self._ws[tab] = ws

    @property
    def nama(self) -> str:
        return "sheets"

    def _baca(self, tab):
        vals = self._ws[tab].get_all_values()
        if len(vals) <= 1:
            return rapikan(tab, pd.DataFrame(columns=SKEMA[tab]))
        head, rows = vals[0], vals[1:]
        return rapikan(tab, pd.DataFrame(rows, columns=head))

    def _tulis(self, tab, df):
        ws = self._ws[tab]
        isi = [SKEMA[tab]] + [
            [int(v) if c in KOLOM_ANGKA else str(v) for c, v in zip(SKEMA[tab], r)]
            for r in df.itertuples(index=False)
        ]
        ws.clear()
        need_rows = max(len(isi) + 20, 100)
        if ws.row_count < need_rows:
            ws.resize(rows=need_rows)
        ws.update(isi, value_input_option="RAW")
