"""Fungsi murni (tanpa Streamlit): waktu WIB, periode kasbon, sandi, item pesanan."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets as pysecrets
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

WIB = ZoneInfo("Asia/Jakarta")
BATAS_EDIT = time(10, 15)  # pelanggan boleh ubah/batal sampai jam ini pada hari H
BULAN = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
KATEGORI = ["Nasi", "Lauk", "Minuman", "Lain-lain"]
NAMA_ADMIN = "ADMIN"


# ---------- waktu ----------
def sekarang() -> datetime:
    return datetime.now(WIB)


def hari_ini() -> date:
    return sekarang().date()


def iso(d: date) -> str:
    return d.isoformat()


def dari_iso(s: str) -> date:
    return date.fromisoformat(s)


def tgl_pendek(d: date) -> str:
    return f"{d.day} {BULAN[d.month]}"


def tgl_panjang(d: date) -> str:
    hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][d.weekday()]
    return f"{hari}, {d.day} {BULAN[d.month]} {d.year}"


def batas_edit(tgl: date) -> datetime:
    return datetime.combine(tgl, BATAS_EDIT, tzinfo=WIB)


def bisa_edit(tgl: date) -> bool:
    """Pelanggan masih boleh mengubah/membatalkan pesanan untuk tanggal ini?"""
    return sekarang() < batas_edit(tgl)


# ---------- periode kasbon: tanggal 11 s/d tanggal 10 bulan berikutnya ----------
def periode_dari(d: date) -> tuple[date, date]:
    if d.day >= 11:
        mulai = d.replace(day=11)
    else:
        mulai = (d.replace(day=1) - timedelta(days=1)).replace(day=11)
    bulan_depan = (mulai.replace(day=28) + timedelta(days=4)).replace(day=1)
    return mulai, bulan_depan.replace(day=10)


def periode_key(mulai: date) -> str:
    return mulai.strftime("%Y-%m")


def periode_label(mulai: date) -> str:
    return f"{BULAN[mulai.month]} {mulai.year}"


def periode_dari_key(key: str) -> tuple[date, date]:
    y, m = key.split("-")
    return periode_dari(date(int(y), int(m), 11))


def hari_periode(mulai: date, akhir: date) -> list[date]:
    return [mulai + timedelta(days=i) for i in range((akhir - mulai).days + 1)]


def periode_sebelumnya(mulai: date) -> tuple[date, date]:
    return periode_dari(mulai - timedelta(days=1))


# ---------- uang & teks ----------
def rupiah(n) -> str:
    return "Rp" + f"{int(n):,}".replace(",", ".")


def rapikan_nama(s: str) -> str:
    return " ".join(str(s).split()).upper()


# ---------- sandi (PBKDF2, tidak disimpan polos) ----------
def hash_sandi(sandi: str, salt: str | None = None) -> str:
    salt = salt or pysecrets.token_hex(8)
    h = hashlib.pbkdf2_hmac("sha256", sandi.encode(), salt.encode(), 100_000).hex()
    return f"{salt}${h}"


def cek_sandi(sandi: str, tersimpan: str) -> bool:
    if not tersimpan or "$" not in tersimpan:
        return False
    salt, _ = tersimpan.split("$", 1)
    return hmac.compare_digest(hash_sandi(sandi, salt), tersimpan)


# ---------- token masuk (agar tidak keluar sendiri saat halaman di-refresh di HP) ----------
def buat_token(nama: str, rahasia: str, jam: int) -> str:
    exp = int((sekarang() + timedelta(hours=jam)).timestamp())
    payload = base64.urlsafe_b64encode(f"{nama}|{exp}".encode()).decode()
    sig = hmac.new(rahasia.encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]
    return f"{payload}.{sig}"


def baca_token(token: str, rahasia: str) -> str | None:
    try:
        payload, sig = token.split(".", 1)
        ok = hmac.new(rahasia.encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]
        if not hmac.compare_digest(sig, ok):
            return None
        nama, exp = base64.urlsafe_b64decode(payload.encode()).decode().rsplit("|", 1)
        return nama if sekarang().timestamp() < int(exp) else None
    except Exception:
        return None


# ---------- item pesanan ----------
def parse_items(s) -> list[dict]:
    if not s:
        return []
    try:
        return json.loads(s)
    except Exception:
        return []


def dump_items(items: list[dict]) -> str:
    return json.dumps(items, ensure_ascii=False, separators=(",", ":"))


def total_items(items: list[dict]) -> int:
    return sum(int(i["harga"]) * int(i["qty"]) for i in items)


def rincian_teks(items: list[dict]) -> str:
    return ", ".join(f'{i["nama"]} x{i["qty"]}' for i in items) if items else "-"


def kelompok(items: list[dict]) -> int:
    """1 = ada nasi, 2 = lauk tanpa nasi, 3 = hanya minuman / lain-lain."""
    kat = {i["kategori"] for i in items}
    if "Nasi" in kat:
        return 1
    if "Lauk" in kat:
        return 2
    return 3


def jumlah_porsi(items: list[dict], grup: int) -> int:
    kat = {1: "Nasi", 2: "Lauk"}.get(grup)
    if kat:
        return sum(int(i["qty"]) for i in items if i["kategori"] == kat)
    return sum(int(i["qty"]) for i in items)


def hitung_rekap(daftar_items: list[list[dict]]) -> dict[str, tuple[str, int]]:
    """{nama menu: (kategori, jumlah)} dijumlah dari banyak pesanan."""
    out: dict[str, list] = {}
    for items in daftar_items:
        for i in items:
            e = out.setdefault(i["nama"], [i["kategori"], 0])
            e[1] += int(i["qty"])
    return {k: (v[0], v[1]) for k, v in out.items()}


def bandingkan(lama: list[dict], baru: list[dict]) -> list[tuple[str, str, int]]:
    """Daftar perubahan: ('+'|'-'|'~', nama, selisih/qty)."""
    a = {i["nama"]: int(i["qty"]) for i in lama}
    b = {i["nama"]: int(i["qty"]) for i in baru}
    out = []
    for nama in list(dict.fromkeys([*a, *b])):
        d = b.get(nama, 0) - a.get(nama, 0)
        if d > 0:
            out.append(("+", nama, d))
        elif d < 0:
            out.append(("-", nama, -d))
    return out
