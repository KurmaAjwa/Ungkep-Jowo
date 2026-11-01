"""Pembayaran kasbon (tanpa UI): tagihan per periode, kirim bukti transfer, konfirmasi lunas."""
from __future__ import annotations

import base64
import io
from datetime import date

import pandas as pd

import logic

# status pembayaran
LUNAS_OTO = "Lunas (otomatis)"      # hanya untuk data lama; sekarang tidak pernah dipakai (bukti selalu dicek admin)
LUNAS = "Lunas"
CEK = "Perlu dicek admin"
DITOLAK = "Ditolak"
STATUS_LUNAS = {LUNAS, LUNAS_OTO}


def _kasbon(store) -> pd.DataFrame:
    df = store.all("Kasbon")
    df["subtotal"] = pd.to_numeric(df["subtotal"], errors="coerce").fillna(0)
    return df[df["status_pesanan"] != "Batal"]


def tagihan(store, nama: str, kode: str, tanggal: str | None = None, pilih: list[str] | None = None) -> dict:
    """Ringkasan kasbon satu pelanggan pada satu periode (atau satu tanggal bila `tanggal` diisi):
    total, sisa (belum lunas), dan rincian per tanggal dengan status lunas."""
    df = _kasbon(store)
    df = df[(df["pelanggan"] == nama) & (df["periode"] == kode)]
    if tanggal:
        df = df[df["tanggal"] == tanggal]
    if pilih is not None:   # hanya item yang dicentang
        df = df[df["item"].isin(pilih)]
    total = float(df["subtotal"].sum())
    sisa = float(df.loc[df["status_bayar"] != "Lunas", "subtotal"].sum())
    per_hari = {}
    for tgl, g in df.groupby("tanggal"):
        per_hari[tgl] = {"total": float(g["subtotal"].sum()), "lunas": bool((g["status_bayar"] == "Lunas").all()),
                         "sisa": float(g.loc[g["status_bayar"] != "Lunas", "subtotal"].sum())}
    return {"total": total, "sisa": sisa, "lunas": total > 0 and sisa == 0, "per_hari": dict(sorted(per_hari.items()))}


def daftar(store, nama: str | None = None, kode: str | None = None) -> pd.DataFrame:
    df = store.all("Pembayaran")
    if nama:
        df = df[df["pelanggan"] == nama]
    if kode:
        df = df[df["periode"] == kode]
    return df


def menunggu_cek(store, nama: str, kode: str, tanggal: str | None = None) -> pd.DataFrame:
    df = daftar(store, nama, kode)
    df = df[df["status"] == CEK]
    if tanggal:  # bukti khusus tanggal itu, atau bukti satu periode penuh
        df = df[(df["tanggal"] == tanggal) | (df["tanggal"] == "")]
    return df


def kompres_bukti(data: bytes, batas: int = 44000) -> str:
    """Perkecil foto bukti jadi JPEG kecil (base64) agar muat di satu sel Google Sheets (maks 50.000 karakter)."""
    from PIL import Image, ImageOps

    img = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
    for sisi, mutu in ((520, 55), (420, 50), (340, 45), (280, 40), (220, 35)):
        im = img.copy()
        im.thumbnail((sisi, sisi * 3))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=mutu, optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode()
        if len(b64) <= batas:
            return b64
    return b64[:0]


def kompres_penuh(data: bytes, batas: int = 240000) -> str:
    """Foto bukti ukuran jelas (sisi terpanjang ±1000 px) sebagai JPEG base64; dipotong per 45.000 karakter saat disimpan."""
    from PIL import Image, ImageOps

    img = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
    b64 = ""
    for sisi, mutu in ((1000, 62), (900, 58), (800, 54), (700, 50), (600, 46)):
        im = img.copy()
        im.thumbnail((sisi, sisi * 3))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=mutu, optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode()
        if len(b64) <= batas:
            return b64
    return ""


_POTONG = 45000


def simpan_foto_penuh(store, pid: str, b64: str) -> None:
    if not b64:
        return
    store.append("BuktiFoto", [{"id": pid, "urut": i, "data": b64[k:k + _POTONG]} for i, k in enumerate(range(0, len(b64), _POTONG))])


def foto_penuh(store, pid: str, cadangan: str = "") -> str:
    """Foto bukti ukuran jelas (base64). Bila tidak ada, pakai foto kecil di kolom bukti."""
    df = store.all("BuktiFoto")
    df = df[df["id"] == str(pid)]
    if df.empty:
        return cadangan if len(cadangan) > 20 else ""      # "ada" = penanda saja, bukan gambar
    df = df.assign(_u=pd.to_numeric(df["urut"], errors="coerce")).sort_values("_u")
    return "".join(df["data"].tolist())


def _id() -> str:
    return logic.now_wib().strftime("%Y%m%d%H%M%S%f")


def _cocok(nama: str, kode: str, tgl: str | None) -> dict:
    m = {"pelanggan": nama, "periode": kode}
    if tgl:
        m["tanggal"] = tgl
    return m


def item_belum_lunas(store, nama: str, kode: str, tgl: str) -> list[dict]:
    """Item pada satu tanggal beserta status lunasnya: [{item, qty, subtotal, lunas}]."""
    df = _kasbon(store)
    df = df[(df["pelanggan"] == nama) & (df["periode"] == kode) & (df["tanggal"] == tgl)]
    return [{"item": r.item, "qty": int(float(r.qty or 0)), "subtotal": float(r.subtotal), "lunas": r.status_bayar == "Lunas"}
            for r in df.itertuples()]


def _tandai_lunas(store, nama: str, kode: str, tgl: str | None = None, pilih: list[str] | None = None) -> None:
    if pilih is None:
        store.update_where("Kasbon", _cocok(nama, kode, tgl), {"status_bayar": "Lunas"})
        return
    for it in pilih:
        store.update_where("Kasbon", {**_cocok(nama, kode, tgl), "item": it}, {"status_bayar": "Lunas"})


_PFX = "ITEM:"


def _catat_item(pilih: list[str] | None) -> str:
    return _PFX + "|".join(pilih) if pilih is not None else ""


def _item_dari_cek(store, nama: str, kode: str, tgl: str | None) -> list[str] | None:
    """Item yang tercatat pada bukti transfer yang menunggu cek (None = seluruh tagihan)."""
    df = daftar(store, nama, kode)
    df = df[(df["status"] == CEK) & (df["tanggal"] == (tgl or ""))]
    hasil: list[str] = []
    for c in df["catatan"]:
        if not str(c).startswith(_PFX):
            return None
        hasil += [x for x in str(c)[len(_PFX):].split("|") if x]
    return hasil if len(df) else None


def kirim_pembayaran(store, nama: str, kode: str, jumlah: float, foto: bytes | None,
                     tgl: str | None = None, pilih: list[str] | None = None) -> tuple[str | None, str]:
    """Pelanggan mengirim bukti transfer. Bukti disimpan dan menunggu pengecekan admin (tidak pernah lunas otomatis).
    Kembalikan (galat, status)."""
    t = tagihan(store, nama, kode, tgl, pilih)
    if t["sisa"] <= 0:
        return "Tidak ada tagihan yang tersisa pada periode ini.", ""
    if pilih is not None:   # hanya item yang masih belum lunas
        pilih = [i["item"] for i in item_belum_lunas(store, nama, kode, tgl or "") if not i["lunas"] and i["item"] in pilih]
    if jumlah <= 0:
        return "Isi jumlah yang kamu transfer.", ""
    if not foto:
        return "Unggah foto bukti pembayaran dulu.", ""
    try:
        from PIL import Image
        with Image.open(io.BytesIO(foto)) as im0:
            if min(im0.size) < 150:
                return "Foto terlalu kecil untuk jadi bukti. Unggah foto/tangkapan layar bukti transfer yang jelas.", ""
        penuh = kompres_penuh(foto)
        bukti = "" if penuh else kompres_bukti(foto)     # foto jelas disimpan di sheet BuktiFoto; kolom bukti hanya penanda (sheet Pembayaran tetap ringan)
    except Exception:
        return "Foto tidak bisa dibaca. Coba foto lain (JPG/PNG).", ""
    if not penuh and not bukti:
        return "Foto terlalu besar untuk disimpan. Coba foto lain.", ""
    pid = _id()
    simpan_foto_penuh(store, pid, penuh)
    status = CEK      # bukti transfer TIDAK pernah otomatis lunas: admin yang mengecek dan menandai item yang dibayar
    store.append("Pembayaran", [{
        "id": pid, "waktu": logic.now_wib().isoformat(timespec="seconds"), "pelanggan": nama, "periode": kode,
        "jumlah": int(round(jumlah)), "tagihan": int(round(t["sisa"])), "metode": "Transfer BNI",
        "status": status, "bukti": bukti or "ada", "catatan": _catat_item(pilih), "tanggal": tgl or "",
    }])
    return None, status


def konfirmasi_lunas(store, nama: str, kode: str, tgl: str | None = None, metode: str = "Tunai",
                     pilih: list[str] | None = None) -> None:
    """Admin menandai kasbon (satu tanggal, atau satu periode penuh) lunas. Bukti yang menunggu cek ikut disetujui.
    `pilih` = hanya item itu yang lunas; bila kosong dan bukti transfer mencatat item tertentu, item itulah yang lunas."""
    if pilih is None:
        pilih = _item_dari_cek(store, nama, kode, tgl)
    t = tagihan(store, nama, kode, tgl, pilih)
    ada = store.update_where("Pembayaran", {"pelanggan": nama, "periode": kode, "status": CEK, "tanggal": tgl or ""},
                             {"status": LUNAS})
    if not ada and t["sisa"] > 0:
        store.append("Pembayaran", [{
            "id": _id(), "waktu": logic.now_wib().isoformat(timespec="seconds"), "pelanggan": nama, "periode": kode,
            "jumlah": int(round(t["sisa"])), "tagihan": int(round(t["sisa"])), "metode": metode,
            "status": LUNAS, "bukti": "", "catatan": _catat_item(pilih) if pilih is not None else "Dikonfirmasi admin",
            "tanggal": tgl or "",
        }])
    _tandai_lunas(store, nama, kode, tgl, pilih)


def tolak_pembayaran(store, nama: str, kode: str, tgl: str | None = None) -> None:
    m = {"pelanggan": nama, "periode": kode, "status": CEK}
    if tgl is not None:
        m["tanggal"] = tgl
    store.update_where("Pembayaran", m, {"status": DITOLAK})


def batalkan_lunas(store, nama: str, kode: str, tgl: str | None = None) -> None:
    """Admin salah menandai lunas: kembalikan ke belum lunas."""
    store.update_where("Kasbon", _cocok(nama, kode, tgl), {"status_bayar": "Belum"})
    for st_ in (LUNAS, LUNAS_OTO):
        m = {"pelanggan": nama, "periode": kode, "status": st_}
        if tgl:
            m["tanggal"] = tgl
        store.update_where("Pembayaran", m, {"status": DITOLAK})


def status_periode(store, nama: str, kode: str) -> str:
    t = tagihan(store, nama, kode)
    if t["total"] <= 0:
        return "—"
    if t["lunas"]:
        return "Lunas"
    if not menunggu_cek(store, nama, kode).empty:
        return "Menunggu cek"
    return "Belum bayar"


# ---------------------------------------------------------------- pengecekan bukti oleh admin
def menunggu_semua(store) -> pd.DataFrame:
    """Semua bukti bayar yang belum dicek (semua periode), terbaru di atas."""
    df = store.all("Pembayaran")
    df = df[df["status"] == CEK]
    return df.iloc[::-1]


def cari(store, pid: str):
    df = store.all("Pembayaran")
    df = df[df["id"] == str(pid)]
    return None if df.empty else df.iloc[0]


def rincian_periode(store, nama: str, kode: str) -> list[dict]:
    """Semua pembelian satu pelanggan dalam satu periode (per baris item) untuk dicentang admin."""
    df = _kasbon(store)
    df = df[(df["pelanggan"] == nama) & (df["periode"] == kode)].sort_values(["tanggal", "order_id"])
    return [{"order_id": str(r.order_id), "item": str(r.item), "tanggal": str(r.tanggal), "qty": int(float(r.qty or 0)),
             "subtotal": float(r.subtotal), "lunas": r.status_bayar == "Lunas"} for r in df.itertuples()]


def item_bukti(bukti) -> tuple[str | None, list[str] | None]:
    """(tanggal, daftar item) yang dicatat pelanggan pada bukti; None = seluruh periode / semua item."""
    tgl = str(bukti["tanggal"]) or None
    c = str(bukti["catatan"])
    items = [x for x in c[len(_PFX):].split("|") if x] if c.startswith(_PFX) else None
    return tgl, items


def konfirmasi_pilihan(store, pid: str, pilih: list[tuple[str, str]], oleh: str = "admin") -> int:
    """Admin menyetujui bukti `pid` dan menandai lunas HANYA item terpilih [(order_id, item)]. Kembalikan jumlah item."""
    b = cari(store, pid)
    if b is None:
        return 0
    for oid, it in pilih:
        store.update_where("Kasbon", {"order_id": oid, "item": it, "pelanggan": b["pelanggan"]}, {"status_bayar": "Lunas"})
    store.update_where("Pembayaran", {"id": str(pid)}, {"status": LUNAS, "catatan": f"Dikonfirmasi {oleh}: {len(pilih)} item"})
    return len(pilih)


def tolak_bukti(store, pid: str) -> None:
    store.update_where("Pembayaran", {"id": str(pid)}, {"status": DITOLAK})


# ---------------------------------------------------------------- lonceng & konfirmasi per pesanan (admin)
def lonceng(store, kode: str) -> tuple[set[tuple[str, str]], set[str]]:
    """Bukti bayar yang belum diperiksa pada satu periode: ({(nama, tanggal_iso)}, {nama}).
    Bukti khusus satu tanggal -> lonceng di sel tanggal itu; semua bukti menyalakan lonceng di TOTAL orangnya."""
    df = store.all("Pembayaran")
    if df.empty:
        return set(), set()
    df = df[(df["periode"] == kode) & (df["status"] == CEK)]
    return ({(r.pelanggan, r.tanggal) for r in df.itertuples() if r.tanggal}, set(df["pelanggan"]))


def daftar_bukti(store, nama: str, kode: str, tgl: str | None = None) -> list[dict]:
    """Semua foto bukti yang diunggah pelanggan pada periode (atau yang berlaku untuk satu tanggal), urut waktu.
    Satu elemen = satu foto: {id, waktu, jumlah, status, tanggal}."""
    df = daftar(store, nama, kode)
    df = df[df["bukti"] != ""]
    if tgl:
        df = df[(df["tanggal"] == tgl) | (df["tanggal"] == "")]
    df = df.sort_values("waktu")
    return [{"id": str(r.id), "waktu": str(r.waktu), "jumlah": float(r.jumlah or 0), "status": str(r.status), "tanggal": str(r.tanggal)}
            for r in df.itertuples()]


def periksa_bukti(store, nama: str, kode: str, tgl: str | None = None) -> int:
    """Admin sudah memeriksa: bukti yang menunggu jadi 'Lunas' (diperiksa). tgl=None -> semua bukti pelanggan pada periode itu."""
    m = {"pelanggan": nama, "periode": kode, "status": CEK}
    if tgl:
        m["tanggal"] = tgl
    return store.update_where("Pembayaran", m, {"status": LUNAS, "catatan": "Diperiksa admin"})


def simpan_pelunasan(store, nama: str, kode: str, lunas: list[tuple[str, str]], belum: list[tuple[str, str]],
                     tgl: str | None = None, periksa: bool = True) -> dict:
    """Simpan keputusan admin: `lunas` = [(order_id, item)] yang ditandai lunas, `belum` = yang dikembalikan ke belum lunas
    (batal pelunasan). Bukti yang menunggu pada cakupan itu dianggap sudah diperiksa."""
    if lunas:
        store.update_banyak("Kasbon", [{"order_id": o, "item": i, "pelanggan": nama} for o, i in lunas], {"status_bayar": "Lunas"})
    if belum:
        store.update_banyak("Kasbon", [{"order_id": o, "item": i, "pelanggan": nama} for o, i in belum], {"status_bayar": "Belum"})
    n_cek = periksa_bukti(store, nama, kode, tgl) if periksa else 0
    if lunas and not n_cek:    # tanpa bukti (tunai / langsung): catat sebagai riwayat
        df = _kasbon(store)
        kunci = {(o, i) for o, i in lunas}
        df = df[(df["pelanggan"] == nama) & (df["periode"] == kode)]
        jml = float(sum(r.subtotal for r in df.itertuples() if (str(r.order_id), str(r.item)) in kunci))
        store.append("Pembayaran", [{
            "id": _id(), "waktu": logic.now_wib().isoformat(timespec="seconds"), "pelanggan": nama, "periode": kode,
            "jumlah": int(round(jml)), "tagihan": int(round(jml)), "metode": "Tunai/langsung", "status": LUNAS, "bukti": "",
            "catatan": f"Dikonfirmasi admin: {len(lunas)} item", "tanggal": tgl or "",
        }])
    return {"lunas": len(lunas), "belum": len(belum), "diperiksa": n_cek}


def pesanan_periode(store, nama: str, kode: str) -> list[dict]:
    """Pesanan satu pelanggan pada satu periode, per order & tanggal: [{tanggal, order_id, item:[...], total, lunas, sisa, kunci:[(order_id,item)]}]."""
    out: dict[tuple[str, str], dict] = {}
    for r in rincian_periode(store, nama, kode):
        o = out.setdefault((r["tanggal"], r["order_id"]), {"tanggal": r["tanggal"], "order_id": r["order_id"], "teks": [], "total": 0.0,
                                                        "sisa": 0.0, "kunci": [], "n_lunas": 0})
        o["teks"].append(f"{r['item']} ×{r['qty']}")
        o["total"] += r["subtotal"]
        o["kunci"].append((r["order_id"], r["item"]))
        if r["lunas"]:
            o["n_lunas"] += 1
        else:
            o["sisa"] += r["subtotal"]
    for o in out.values():
        o["lunas"] = o["n_lunas"] == len(o["kunci"])
    return sorted(out.values(), key=lambda o: (o["tanggal"], o["order_id"]))
