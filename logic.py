"""Logika murni: waktu WIB, periode kasbon (tgl 11 s/d tgl 10), sandi, format rupiah."""
from __future__ import annotations

import calendar
import hashlib
import hmac
import secrets as pysecrets
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

WIB = ZoneInfo("Asia/Jakarta")
CUTOFF_HARI = 10          # kasbon dibayar tanggal 10
EDIT_BATAS_JAM = (10, 45)  # pelanggan bisa pesan/ubah/batal sampai jam ini (WIB) pada hari H
BATAS_TEKS = f"{EDIT_BATAS_JAM[0]:02d}:{EDIT_BATAS_JAM[1]:02d}"

BULAN = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]


HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]


def tanggal_panjang(d: date) -> str:
    return f"{HARI[d.weekday()]}, {d.day} {BULAN[d.month]} {d.year}"


def tanggal_pendek(d: date) -> str:
    return f"{d.day} {BULAN[d.month][:3]}"


def now_wib() -> datetime:
    return datetime.now(WIB)


def today_wib() -> date:
    return now_wib().date()


def _add_month(d: date, n: int) -> date:
    idx = d.year * 12 + (d.month - 1) + n
    y, m = divmod(idx, 12)
    return date(y, m + 1, 1)


def periode_untuk(d: date) -> tuple[date, date]:
    """Periode kasbon yang memuat tanggal d: tgl 11 bulan ini (atau lalu) s/d tgl 10 berikutnya."""
    if d.day > CUTOFF_HARI:
        start = d.replace(day=CUTOFF_HARI + 1)
        end = _add_month(d, 1).replace(day=CUTOFF_HARI)
    else:
        start = _add_month(d, -1).replace(day=CUTOFF_HARI + 1)
        end = d.replace(day=CUTOFF_HARI)
    return start, end


def geser_periode(start: date, n: int) -> tuple[date, date]:
    return periode_untuk(_add_month(start, n).replace(day=CUTOFF_HARI + 1))


def kode_periode(start: date) -> str:
    """Kode periode = bulan awal, mis. 2026-10 untuk 11 Okt - 10 Nov 2026."""
    return f"{start.year}-{start.month:02d}"


def label_periode(start: date, end: date) -> str:
    return f"{start.day} {BULAN[start.month][:3]} - {end.day} {BULAN[end.month][:3]} {end.year}"


def daftar_hari(start: date, end: date) -> list[date]:
    return [start + timedelta(days=i) for i in range((end - start).days + 1)]


def rupiah(n: float | int) -> str:
    return "Rp" + f"{int(round(n)):,}".replace(",", ".")


UNGGAH_BATAS_JAM = 13   # menu diunggah sebelum jam ini = menu hari itu; setelahnya = menu besok


def tanggal_menu_default(sekarang: datetime | None = None) -> date:
    """Tanggal bawaan saat admin mengunggah menu: sebelum jam 13:00 WIB menu hari ini, setelahnya menu besok."""
    sekarang = sekarang or now_wib()
    return sekarang.date() + timedelta(days=0 if sekarang.hour < UNGGAH_BATAS_JAM else 1)


def bisa_edit(tgl: date, sekarang: datetime | None = None) -> bool:
    """Pelanggan boleh mengubah pesanan untuk tanggal `tgl` sampai batas jam (BATAS_TEKS) WIB pada hari itu."""
    sekarang = sekarang or now_wib()
    batas = datetime(tgl.year, tgl.month, tgl.day, *EDIT_BATAS_JAM, tzinfo=WIB)
    return sekarang <= batas


# --- sandi: disimpan sebagai hash (PBKDF2), bukan teks asli ---
def hash_sandi(sandi: str) -> str:
    salt = pysecrets.token_hex(8)
    h = hashlib.pbkdf2_hmac("sha256", sandi.encode(), salt.encode(), 120_000).hex()
    return f"{salt}${h}"


def cek_sandi(sandi: str, tersimpan: str) -> bool:
    try:
        salt, h = tersimpan.split("$", 1)
    except ValueError:
        return False
    cek = hashlib.pbkdf2_hmac("sha256", sandi.encode(), salt.encode(), 120_000).hex()
    return hmac.compare_digest(cek, h)


def bersih_nama(nama: str) -> str:
    return " ".join(nama.strip().split())
