"""Layanan aplikasi: akun, sesi, dan pembacaan data bersama untuk semua halaman."""
from __future__ import annotations

import streamlit as st

import logic
from store import make_store


def secret(kunci: str, bawaan=None):
    """Baca st.secrets dengan aman: tanpa berkas secrets pun aplikasi tetap jalan memakai nilai bawaan."""
    try:
        return st.secrets.get(kunci, bawaan)
    except Exception:
        return bawaan


class _Rahasia:
    def get(self, k, d=None):
        return secret(k, d)

    def __getitem__(self, k):
        return st.secrets[k]


@st.cache_resource(show_spinner="Menghubungkan ke database…")
def get_store():
    store = make_store(_Rahasia())
    _pastikan_admin(store)
    _muat_awal_otomatis(store)
    return store


def _muat_awal_otomatis(store) -> None:
    """Database baru (hanya akun admin, belum ada pesanan): isi otomatis dari data_awal.json agar riwayat 20-21 Okt langsung ada."""
    try:
        import data_awal
        if len(store.all("Pelanggan")) <= 1 and store.all("Kasbon").empty:
            data_awal.muat(store, sandi_awal())
    except Exception:
        pass


def _pastikan_admin(store) -> None:
    df = store.all("Pelanggan")
    if (df["role"] == "admin").any():
        return
    nama = secret("admin_name", "ADMIN")
    sandi = secret("admin_password", "admin123")
    store.append("Pelanggan", [{
        "nama": nama, "sandi_hash": logic.hash_sandi(sandi), "role": "admin",
        "aktif": "1", "dibuat": logic.now_wib().isoformat(timespec="seconds"),
    }])


def sandi_awal() -> str:
    return secret("default_password", "ungkep123")


# ---- sesi ----
def user() -> str | None:
    return st.session_state.get("user")


def is_admin() -> bool:
    return st.session_state.get("role") == "admin"


MASA_PENUH = 1800    # detik: setelah kode 2FA benar, akses penuh terbuka 30 menit lalu terkunci sendiri


def is_penuh() -> bool:
    """Admin dengan akses penuh. Tanpa 2FA terpasang = penuh (supaya bisa memasang 2FA pertama kali).
    Admin yang sudah masuk tetapi belum membuka kunci hanya boleh: memesankan, menambah pesanan, mengonfirmasi revisi, membalas chat."""
    if not is_admin():
        return False
    if not _rahasia_2fa():
        return True
    return st.session_state.get("_penuh_sampai", 0) > _time.time()


def sisa_penuh() -> int:
    return max(0, int(st.session_state.get("_penuh_sampai", 0) - _time.time()))


def buka_penuh(kode: str) -> str | None:
    if not is_admin():
        return "Khusus admin."
    nama = user() or "?"
    if (sisa := _terkunci("2fa:" + nama)):
        return f"Terlalu banyak percobaan salah. Coba lagi {sisa // 60 + 1} menit lagi."
    if not totp_cek(_rahasia_2fa(), kode):
        _GAGAL.setdefault("2fa:" + nama, []).append(_time.time())
        return "Kode salah. Lihat kode 6 angka terbaru di aplikasi authenticator."
    _GAGAL.pop("2fa:" + nama, None)
    st.session_state["_penuh_sampai"] = _time.time() + MASA_PENUH
    return None


def kunci_lagi() -> None:
    st.session_state.pop("_penuh_sampai", None)


def keluar() -> None:
    for k in ("user", "role", "_disapa", "_chat", "_penuh_sampai"):
        st.session_state.pop(k, None)


# ---- akun ----
def daftar_nama(store) -> list[str]:
    df = store.all("Pelanggan")
    df = df[df["aktif"] != "0"]
    return sorted(df["nama"].tolist(), key=str.lower)


import base64
import hashlib
import hmac
import secrets as _sec
import struct
import time as _time

_GAGAL: dict[str, list[float]] = {}      # percobaan masuk yang gagal per nama (di memori server)
_MAKS_GAGAL, _JENDELA = 6, 600           # 6 kali salah dalam 10 menit -> kunci 10 menit


def _terkunci(nama: str) -> int:
    """Sisa detik terkunci (0 = boleh mencoba)."""
    t = _time.time()
    _GAGAL[nama] = [x for x in _GAGAL.get(nama, []) if t - x < _JENDELA]
    if len(_GAGAL[nama]) >= _MAKS_GAGAL:
        return int(_JENDELA - (t - _GAGAL[nama][0]))
    return 0


def totp_baru() -> str:
    """Kunci pendaftaran yang STABIL (tidak berubah saat halaman dimuat ulang atau aplikasi di-reboot): diturunkan dari rahasia
    server (kunci Google). Dengan begitu kunci yang sudah dimasukkan ke aplikasi authenticator tetap cocok."""
    try:
        dasar = str(st.secrets["gcp_service_account"]["private_key"]) or str(st.secrets.get("admin_password", ""))
    except Exception:
        dasar = str(secret("admin_password", "")) or "lokal"
    h = hmac.new(dasar.encode(), b"ungkep-jowo-admin-totp", hashlib.sha256).digest()[:20]
    return base64.b32encode(h).decode().rstrip("=")


def totp_kode(rahasia: str, t: float | None = None) -> str:
    kunci = base64.b32decode(rahasia.upper() + "=" * (-len(rahasia) % 8))
    h = hmac.new(kunci, struct.pack(">Q", int((t or _time.time()) // 30)), hashlib.sha1).digest()
    o = h[-1] & 15
    return f"{(struct.unpack('>I', h[o:o + 4])[0] & 0x7FFFFFFF) % 1000000:06d}"


def totp_cek(rahasia: str, kode: str) -> bool:
    kode = "".join(ch for ch in str(kode) if ch.isdigit())
    t = _time.time()
    return len(kode) == 6 and any(hmac.compare_digest(totp_kode(rahasia, t + d * 30), kode) for d in (-1, 0, 1))


def _rahasia_2fa() -> str:
    return str(secret("admin_totp_secret", "") or "").strip()


def masuk(store, nama: str, sandi: str) -> str | None:
    """Kembalikan None bila sukses, "2FA" bila admin perlu kode, atau pesan galat."""
    if (sisa := _terkunci(nama)):
        return f"Terlalu banyak percobaan salah. Coba lagi {sisa // 60 + 1} menit lagi."
    df = store.all("Pelanggan")
    row = df[df["nama"] == nama]
    if row.empty or row.iloc[0]["aktif"] == "0":
        return "Nama tidak ditemukan."
    if not logic.cek_sandi(sandi, row.iloc[0]["sandi_hash"]):
        _GAGAL.setdefault(nama, []).append(_time.time())
        return "Sandi salah. Lupa sandi? Tekan 'Tanya admin'."
    _GAGAL.pop(nama, None)
    st.session_state["user"] = nama
    st.session_state["role"] = row.iloc[0]["role"]
    return None


def daftar_baru(store, nama: str) -> str | None:
    nama = logic.bersih_nama(nama)
    if len(nama) < 3:
        return "Nama minimal 3 huruf."
    ada = {n.lower() for n in store.all("Pelanggan")["nama"]}
    if nama.lower() in ada:
        return "Nama sudah terdaftar. Silakan masuk, atau pakai nama lain (mis. tambah inisial/bagian)."
    store.append("Pelanggan", [{
        "nama": nama, "sandi_hash": logic.hash_sandi(sandi_awal()), "role": "pelanggan",
        "aktif": "1", "dibuat": logic.now_wib().isoformat(timespec="seconds"),
    }])
    return None


def ganti_sandi(store, nama: str, lama: str, baru: str) -> str | None:
    row = store.all("Pelanggan").query("nama == @nama")
    if row.empty or not logic.cek_sandi(lama, row.iloc[0]["sandi_hash"]):
        return "Sandi lama salah."
    if len(baru) < 4:
        return "Sandi baru minimal 4 karakter."
    store.update_where("Pelanggan", {"nama": nama}, {"sandi_hash": logic.hash_sandi(baru)})
    return None


def tanya_admin(store, nama: str) -> None:
    store.append("Permintaan", [{
        "waktu": logic.now_wib().isoformat(timespec="seconds"), "nama": nama,
        "jenis": "reset_sandi", "status": "Menunggu",
    }])


def reset_sandi(store, nama: str) -> None:
    store.update_where("Pelanggan", {"nama": nama}, {"sandi_hash": logic.hash_sandi(sandi_awal())})
    store.update_where("Permintaan", {"nama": nama, "status": "Menunggu"}, {"status": "Selesai"})
