"""Menu dari Excel: lembar "Menu" (makanan + pendamping gratis) dan "Minuman" (aturan harga). Aturan tidak permanen:
ubah angka di Excel lalu unggah lagi. Lembar ini boleh berada di berkas yang sama dengan rekap pesanan."""
from __future__ import annotations

import io

import openpyxl

KAT_MAKANAN = ["Nasi", "Ayam Sayur", "Lauk", "Lain-lain"]


def _t(x) -> str:
    return "" if x is None else str(x).strip()


def _n(x) -> int | None:
    if x is None or str(x).strip() == "":
        return None
    try:
        return int(float(str(x).replace(".", "").replace(",", ".").replace("Rp", "").strip()))
    except ValueError:
        return None


def _lembar(wb, nama: str):
    for ws in wb.worksheets:
        if ws.title.strip().lower() == nama:
            return ws
    return None


def ada_menu(data: bytes) -> bool:
    wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    try:
        return any(_lembar(wb, n) is not None for n in ("menu", "makanan", "minuman"))
    finally:
        wb.close()


def baca(data: bytes) -> dict:
    """Lembar "Menu": kolom Jenis | Nama | Harga | Harga Jumbo | Harga + Susu | Rasa / Untuk lauk.
    Jenis: Nasi, Ayam Sayur, Lauk, Lain-lain (makanan), Minuman, Gratis (Nama = pendamping, kolom terakhir = lauk penerima, kosong/SEMUA = semua lauk).
    -> {"makanan", "minuman", "gratis", "aturan", "katalog", "catatan"} (belum menulis apa pun)."""
    wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    makanan, minuman, gratis, cat = [], [], [], []
    try:
        baris = []      # (jenis, nama, harga, jumbo, susu, rasa)
        for nm in ("menu", "makanan"):          # kolom: Jenis | Nama | Harga | Jumbo | + Susu | Rasa/Untuk
            ws = _lembar(wb, nm)
            if ws:
                baris += [(list(r) + [None] * 6)[:6] for r in list(ws.iter_rows(values_only=True))[1:]]
        ws = _lembar(wb, "minuman")             # kolom: Nama | Harga | Jumbo | + Susu | Rasa  (Jenis otomatis Minuman)
        if ws:
            for r in list(ws.iter_rows(values_only=True))[1:]:
                n_, h_, j_, s_, r_ = (list(r) + [None] * 5)[:5]
                baris.append(["Minuman", n_, h_, j_, s_, r_])
        for jenis, nama, harga, jumbo, susu, rasa in baris:
            nama, j = _t(nama), _t(jenis).lower()
            if not nama or not j:
                continue
            if j == "gratis":
                untuk = [x.strip() for x in _t(rasa).split(",") if x.strip() and x.strip().lower() not in ("semua", "*")]
                for u in (untuk or ["*"]):
                    gratis.append({"lauk": u, "pendamping": nama})
            elif j == "minuman":
                varian = [v.strip() for v in _t(rasa).split(",") if v.strip()] or [""]
                if _n(harga) is None and _n(jumbo) is None and _n(susu) is None:
                    cat.append(f"Minuman “{nama}” tanpa harga, dilewati.")
                for v in varian:
                    for sufiks, h in (("", _n(harga)), (" Jumbo", _n(jumbo)), (" + Susu", _n(susu))):
                        if h is not None:
                            minuman.append({"nama": nama, "varian": (v + sufiks).strip(), "harga": h, "hpp": 0, "ready": "1"})
            else:
                kat = next((k for k in KAT_MAKANAN if k.lower() == j), None)
                h = _n(harga)
                if kat is None:
                    cat.append(f"Jenis “{_t(jenis)}” pada “{nama}” tidak dikenal, dilewati.")
                elif h is None:
                    cat.append(f"Menu “{nama}” tanpa harga, dilewati.")
                else:
                    makanan.append({"kategori": kat, "nama": nama, "harga": h, "hpp": 0})
    finally:
        wb.close()
    katalog = {m["nama"]: {"kategori": m["kategori"], "harga": float(m["harga"]), "hpp": 0.0} for m in makanan}
    for m in minuman:
        katalog[(m["nama"] + " " + m["varian"]).strip()] = {"kategori": "Minuman", "harga": float(m["harga"]), "hpp": 0.0}
    return {"makanan": makanan, "minuman": minuman, "gratis": gratis, "catatan": cat, "katalog": katalog,
            "aturan": [(g["lauk"], g["pendamping"]) for g in gratis]}


def terapkan(store, hasil: dict) -> dict:
    """Tulis ke menu master, minuman, dan aturan gratis. Hanya bagian yang ada di berkas yang diganti."""
    n = {}
    if hasil["makanan"]:
        lama = store.all("Menu")
        simpan = [r._asdict() for r in lama.itertuples(index=False) if r.kategori == "Minuman"]
        rows = [{"id": f"m{i:03d}", "kategori": m["kategori"], "nama": m["nama"], "harga": m["harga"], "hpp": m["hpp"], "aktif": "1"}
                for i, m in enumerate(hasil["makanan"], 1)]
        store.replace_all("Menu", simpan + rows)
        store.replace_all("Gratis", hasil["gratis"])
        n["makanan"] = len(rows)
    if hasil["minuman"]:
        seen, rows = set(), []
        for m in hasil["minuman"]:
            k = (m["nama"].lower(), m["varian"].lower())
            if k not in seen:
                seen.add(k)
                rows.append(m)
        store.replace_all("Minuman", rows)
        n["minuman"] = len(rows)
    return n


def menu_harian_rows(store, tgl_iso: str) -> list[dict]:
    """Semua makanan aktif + minuman ready, siap ditulis ke MenuHarian untuk satu tanggal."""
    rows = []
    for r in store.all("Menu").itertuples():
        if r.kategori != "Minuman" and r.aktif != "0":
            rows.append({"tanggal": tgl_iso, "menu_id": r.id, "kategori": r.kategori, "nama": r.nama, "harga": int(float(r.harga or 0)),
                         "hpp": int(float(r.hpp or 0)), "batas_stok": 0, "stok": "", "alternatif": ""})
    for r in store.all("Minuman").itertuples():
        if r.ready == "1":
            rows.append({"tanggal": tgl_iso, "menu_id": "", "kategori": "Minuman", "nama": (r.nama + " " + r.varian).strip(),
                         "harga": int(float(r.harga or 0)), "hpp": int(float(r.hpp or 0)), "batas_stok": 0, "stok": "", "alternatif": ""})
    return rows


def templat() -> bytes:
    """Berkas contoh yang disusun dari pricelist/riwayat pesanan. Ubah isinya kapan saja lalu unggah lagi."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Makanan"
    tulis_menu(ws, wb.create_sheet("Minuman"))
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


BARIS_MENU = [
    ["Nasi", "Nasi", 3000, "", "", ""],
    ["Lauk", "Ayam Geprek", 7000, "", "", ""],
    ["Lauk", "Ayam Kecap", 7000, "", "", ""],
    ["Lauk", "Ayam Rujak & Sayur Asem", 7000, "", "", ""],
    ["Lauk", "Ayam Urap Urap", 7000, "", "", ""],
    ["Lauk", "Koloke Ayam", 7000, "", "", ""],
    ["Lauk", "Sate Ayam", 7000, "", "", ""],
    ["Lauk", "Sate Komo & Sayur Bening", 7000, "", "", ""],
    ["Lauk", "Telur Bumbu Rujak", 7000, "", "", ""],
    ["Lauk", "Telur Dadar", 7000, "", "", ""],
    ["Lauk", "Telur Dadar Urap Urap", 7000, "", "", ""],
    ["Lain-lain", "Kerupuk", 1000, "", "", ""],
    ["Gratis", "Free Sup", "", "", "", "Ayam Geprek, Ayam Kecap, Telur Dadar"],
    ["Gratis", "Free Bihun", "", "", "", "Sate Ayam"],
    ["Gratis", "Free Tumis Kangkung", "", "", "", "Koloke Ayam"],
    ["Minuman", "Es Nutrisari", 5000, 8000, 8000, "Jeruk, Mangga, Anggur, Coco Pandan, Mangga Milky"],
    ["Minuman", "Es Marimas", 3000, 5000, 8000, "Jambu, Jeruk, Mangga"],
    ["Minuman", "Es Kuku Bima", "", "", 8000, ""],
    ["Minuman", "Es Teh", 3000, 5000, "", ""],
    ["Minuman", "Es Teh Susu", 6000, "", "", ""],
    ["Minuman", "Es Susu Indomilk", 5000, "", "", ""],
    ["Minuman", "Es Susu", 5000, "", "", ""],
    ["Minuman", "Susu Panas", 5000, "", "", ""],
    ["Minuman", "Es Dancow", 8000, "", "", ""],
    ["Minuman", "Es Dancow Coklat", 8000, "", "", ""],
    ["Minuman", "Es Susu Dancow Coklat", 8000, "", "", ""],
    ["Minuman", "Es Good Day", 5000, "", "", ""],
    ["Minuman", "Es Good Day Freze", 5000, "", "", ""],
    ["Minuman", "Es Josshua", 8000, "", "", ""],
    ["Minuman", "Es Americano", 8000, "", "", ""],
    ["Minuman", "Es Segar Sari Susu Soda", 5000, "", "", ""],
    ["Minuman", "Teh Panas", 3000, "", "", ""],
    ["Minuman", "Wedang Kencur", 7000, "", "", ""],
]


def tulis_menu(ws, wm) -> None:
    """ws = lembar Makanan (Jenis | Nama | Harga | Untuk lauk), wm = lembar Minuman (Nama | Harga | Jumbo | + Susu | Rasa)."""
    from openpyxl.styles import Font, PatternFill

    def kepala(w, judul, lebar):
        w.append(judul)
        for c in w[1]:
            c.font = Font(bold=True)
            c.fill = PatternFill("solid", fgColor="FFE7B0")
        for col, x in zip("ABCDEF", lebar):
            w.column_dimensions[col].width = x

    kepala(ws, ["Jenis", "Nama", "Harga", "", "", "Untuk lauk (khusus Gratis; kosong = semua lauk)"], (12, 30, 10, 3, 3, 50))
    for r in BARIS_MENU:
        if r[0] != "Minuman":
            ws.append([r[0], r[1], r[2], "", "", r[5]])
    kepala(wm, ["Nama", "Harga", "Harga Jumbo", "Harga + Susu", "Rasa (pisahkan koma)"], (30, 10, 13, 14, 52))
    for r in BARIS_MENU:
        if r[0] == "Minuman":
            wm.append(r[1:])
    ws["H1"] = "Petunjuk"
    ws["H1"].font = Font(bold=True)
    for i, t in enumerate((
        "Jenis: Nasi, Lauk, Ayam Sayur, Lain-lain, Gratis.",
        "Gratis: Nama = pendamping (Free Sup); kolom terakhir = lauk penerima, kosong = semua lauk. Tiap porsi lauk itu otomatis dapat 1 pendamping.",
        "Di lembar Pesanan, tulisan “(FREE BIHUN)” pada nama pesanan dipakai langsung sebagai pendamping hari itu.",
        "Lembar Minuman: isi Rasa untuk membuat banyak varian sekaligus. Harga Jumbo / + Susu kosong = varian itu tidak ada.",
        "Aturan tidak permanen: ubah lalu unggah lagi."), start=2):
        ws[f"H{i}"] = t
    ws.column_dimensions["H"].width = 110
