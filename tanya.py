"""Pertanyaan yang tidak bisa dijawab Meong diteruskan ke admin; jawaban admin muncul kembali di obrolan."""
from __future__ import annotations

import uuid

import logic


def teruskan(store, nama: str | None, teks: str) -> str:
    if not nama:
        return "Meong? Pertanyaan ini perlu dijawab admin 🙀 Silakan **masuk** dulu supaya admin tahu siapa yang bertanya."
    store.append("Tanya", [{"id": uuid.uuid4().hex[:8], "waktu": logic.now_wib().isoformat(timespec="seconds"),
                            "pelanggan": nama, "pertanyaan": teks.strip()[:500], "status": "Menunggu",
                            "jawaban": "", "dijawab": "", "dibaca": "0"}])
    return ("Hmm, itu di luar tugasku 🙀 Pertanyaanmu sudah **kuteruskan ke admin**. "
            "Mohon **tunggu sebentar** ya — jawabannya akan muncul di sini dan kuberi tahu lewat gelembung 🐾")


def milik(store, nama: str):
    df = store.all("Tanya")
    return df[df["pelanggan"] == nama] if len(df) else df


def menunggu(store):
    df = store.all("Tanya")
    return df[df["status"] == "Menunggu"] if len(df) else df


def belum_dibaca(store, nama: str):
    df = milik(store, nama)
    return df[(df["status"] == "Dijawab") & (df["dibaca"] != "1")] if len(df) else df


def jawab(store, id_: str, isi: str, admin: str = "admin") -> None:
    store.update_where("Tanya", {"id": id_}, {"status": "Dijawab", "jawaban": isi.strip(),
                                              "dijawab": logic.now_wib().isoformat(timespec="seconds"), "dibaca": "0"})


def tandai_dibaca(store, nama: str) -> None:
    for i in belum_dibaca(store, nama)["id"]:
        store.update_where("Tanya", {"id": i}, {"dibaca": "1"})


def kabar(store, nama: str | None) -> str:
    if not nama:
        return ""
    n = len(belum_dibaca(store, nama))
    return f"Admin sudah menjawab pertanyaanmu! Ketuk aku untuk membaca 💌" if n else ""
