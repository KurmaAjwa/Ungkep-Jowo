"""Jendela admin untuk bukti bayar: lihat foto bukti dan konfirmasi pelunasan per item (hanya admin)."""
from __future__ import annotations

import base64
from datetime import date, datetime

import streamlit as st

import logic
import payments
import services


def waktu_teks(iso: str) -> str:
    try:
        d = datetime.fromisoformat(str(iso))
        return f"{d.day} {logic.BULAN[d.month][:3]} {d.year} · {d:%H:%M} WIB"
    except Exception:
        return str(iso)


def _label_periode(kode: str) -> str:
    th, bl = (int(x) for x in kode.split("-"))
    a, b = logic.periode_untuk(date(th, bl, logic.CUTOFF_HARI + 1))
    return logic.label_periode(a, b)


def _tgl(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} {logic.BULAN[d.month][:3]}"


@st.dialog("Bukti bayar", width="large")
def dialog_bukti(pid: str):
    if not services.is_admin():
        st.error("Khusus admin.")
        return
    store = services.get_store()
    b = payments.cari(store, pid)
    if b is None:
        st.info("Bukti tidak ditemukan.")
        return
    st.markdown(f"**{b['pelanggan']}** · dikirim {waktu_teks(b['waktu'])}")
    st.caption(f"Nominal yang diisi pelanggan: {logic.rupiah(float(b['jumlah'] or 0))} · periode {_label_periode(b['periode'])}")
    foto = payments.foto_penuh(store, pid, b["bukti"])
    if foto:
        st.image(base64.b64decode(foto), width="stretch")
    else:
        st.warning("Foto bukti tidak tersimpan.")
    if st.button("Tutup", width="stretch", key=f"tutup_bk_{pid}"):
        st.rerun()


@st.dialog("Konfirmasi pelunasan", width="large")
def dialog_konfirmasi(pid: str):
    if not services.is_admin():
        st.error("Khusus admin.")
        return
    store = services.get_store()
    b = payments.cari(store, pid)
    if b is None or b["status"] != payments.CEK:
        st.info("Bukti ini sudah diproses.")
        return
    nama, kode = b["pelanggan"], b["periode"]
    dibayar = float(b["jumlah"] or 0)
    st.markdown(f"**{nama}** · periode {_label_periode(kode)}")
    st.caption(f"Bukti dikirim {waktu_teks(b['waktu'])} · nominal yang diisi pelanggan **{logic.rupiah(dibayar)}**")
    its = payments.rincian_periode(store, nama, kode)
    if not its:
        st.info("Tidak ada pembelian pada periode ini.")
        return
    tgl_b, item_b = payments.item_bukti(b)
    belum = sum(i["subtotal"] for i in its if not i["lunas"])
    st.markdown("**Centang pembelian yang dibayar:**")
    pilih: list[tuple[str, str]] = []
    total_pilih = 0.0
    tgl_now = None
    for n, i in enumerate(its):
        if i["tanggal"] != tgl_now:
            tgl_now = i["tanggal"]
            st.markdown(f"<div style='margin-top:.5rem;font-weight:800'>{_tgl(tgl_now)}</div>", unsafe_allow_html=True)
        teks = f"{i['item']} ×{i['qty']} · {logic.rupiah(i['subtotal'])}"
        if i["lunas"]:
            st.checkbox(teks + "  — sudah lunas", value=True, disabled=True, key=f"kb_{pid}_{n}")
            continue
        if tgl_b or item_b is not None:     # pelanggan memilih tanggal/item tertentu: itu yang tercentang awal
            awal = (tgl_b is None or i["tanggal"] == tgl_b) and (item_b is None or i["item"] in item_b)
        else:                               # bukti satu periode penuh: centang semua hanya bila nominal pas
            awal = int(round(dibayar)) == int(round(belum))
        if st.checkbox(teks, value=awal, key=f"kb_{pid}_{n}"):
            pilih.append((i["order_id"], i["item"]))
            total_pilih += i["subtotal"]
    selisih = dibayar - total_pilih
    st.markdown(f'<div class="kartu"><small>Dicentang</small><div class="besar">{logic.rupiah(total_pilih)}</div>'
                f'<small>Dibayar pelanggan {logic.rupiah(dibayar)}</small></div>', unsafe_allow_html=True)
    if pilih and int(round(selisih)) != 0:
        st.warning(("Dibayar lebih " if selisih > 0 else "Dibayar kurang ") + logic.rupiah(abs(selisih)) + " dari yang dicentang. Periksa lagi fotonya.")
    a, c = st.columns(2)
    if a.button("Simpan", type="primary", width="stretch", disabled=not pilih, key=f"simpan_kb_{pid}"):
        payments.konfirmasi_pilihan(store, pid, pilih)
        st.session_state["_toast"] = f"Pelunasan {nama} tersimpan ({len(pilih)} item)."
        st.rerun()
    if c.button("Batal", width="stretch", key=f"batal_kb_{pid}"):
        st.rerun()


# ===================================================================== pemeriksaan bukti di jendela rincian / total (admin)
_FLAG = "_lihat_bukti"


def halaman_bukti(store, pid: str) -> None:
    """Isi jendela yang sama diganti gambar bukti bayar; tombol Tutup mengembalikan ke jendela rincian (tanpa memuat ulang halaman)."""
    b = payments.cari(store, pid)
    st.markdown("**Bukti bayar**")
    if b is None:
        st.info("Bukti tidak ditemukan.")
    else:
        st.markdown(f"**{b['pelanggan']}** · dikirim {waktu_teks(b['waktu'])}")
        tgl = f"pesanan {_tgl(b['tanggal'])}" if b["tanggal"] else "seluruh periode"
        st.caption(f"Nominal yang diisi pelanggan: {logic.rupiah(float(b['jumlah'] or 0))} · {tgl} · status: "
                   + ("menunggu dicek" if b["status"] == payments.CEK else ("sudah diperiksa" if b["status"] in payments.STATUS_LUNAS else str(b["status"]).lower())))
        foto = payments.foto_penuh(store, pid, b["bukti"])
        if foto:
            st.image(base64.b64decode(foto), width="stretch")
        else:
            st.warning("Foto bukti tidak tersimpan.")
    if st.button("Tutup", type="primary", width="stretch", key=f"tutup_hb_{pid}"):
        st.session_state.pop(_FLAG, None)
        st.rerun(scope="fragment")


def tombol_bukti(bukti: list[dict]) -> None:
    """Satu tombol per foto bukti yang diunggah pelanggan (jumlah tombol = jumlah foto)."""
    if not bukti:
        st.caption("Belum ada foto bukti bayar dari pelanggan.")
        return
    for baris in range(0, len(bukti), 3):
        cols = st.columns(3)
        for c, b in zip(cols, bukti[baris:baris + 3]):
            n = bukti.index(b) + 1
            lab = f"{'🔔 ' if b['status'] == payments.CEK else ''}Bukti bayar {n}" if len(bukti) > 1 else f"{'🔔 ' if b['status'] == payments.CEK else ''}Lihat bukti bayar"
            if c.button(lab, key=f"lb_{b['id']}", width="stretch"):
                st.session_state[_FLAG] = b["id"]
                st.rerun(scope="fragment")


def _ringkas(total_pilih: float, dibayar: float | None) -> None:
    teks = f'<div class="kartu"><small>Ditandai lunas</small><div class="besar">{logic.rupiah(total_pilih)}</div>'
    if dibayar is not None:
        teks += f"<small>Dibayar pelanggan (bukti menunggu) {logic.rupiah(dibayar)}</small>"
    st.markdown(teks + "</div>", unsafe_allow_html=True)
    if dibayar is not None and int(round(dibayar)) != int(round(total_pilih)):
        sel = dibayar - total_pilih
        st.warning(("Dibayar lebih " if sel > 0 else "Dibayar kurang ") + logic.rupiah(abs(sel)) + " dari yang ditandai. Periksa lagi fotonya.")


def blok_harian(store, tgl: date, nama: str, kunci_muat) -> None:
    """Admin, jendela rincian satu tanggal: lihat bukti, centang item yang lunas (boleh sebagian), simpan, batalkan."""
    kode = logic.kode_periode(logic.periode_untuk(tgl)[0])
    iso = tgl.isoformat()
    its = [i for i in payments.rincian_periode(store, nama, kode) if i["tanggal"] == iso]
    if not its:
        return
    bukti = payments.daftar_bukti(store, nama, kode, iso)
    cek = payments.menunggu_cek(store, nama, kode, iso)
    n_lunas = sum(1 for i in its if i["lunas"])
    total = sum(i["subtotal"] for i in its)
    if n_lunas == len(its):
        stat = "✓ LUNAS"
    elif not cek.empty:
        stat = "🔔 MENUNGGU DIPERIKSA"
    elif n_lunas:
        stat = f"SEBAGIAN LUNAS · sisa {logic.rupiah(sum(i['subtotal'] for i in its if not i['lunas']))}"
    else:
        stat = "BELUM DIBAYAR"
    st.markdown(f'<div class="bayar-stat {"ok" if n_lunas == len(its) else ("cek" if not cek.empty or n_lunas else "belum")}"><small>Pembayaran</small><b>{stat}</b></div>',
                unsafe_allow_html=True)
    tombol_bukti(bukti)
    pil_cek = payments._item_dari_cek(store, nama, kode, iso) if not cek.empty else None
    dibayar = float(pd_sum(cek, "jumlah")) if not cek.empty else None
    ver = f"{n_lunas}_{len(cek)}_{len(bukti)}"
    st.markdown("**Centang pembelian yang sudah dibayar** (hilangkan centang untuk membatalkan pelunasan)")
    want_lunas, want_belum, tot_lunas = [], [], 0.0
    for n, i in enumerate(its):
        awal = i["lunas"] or (not cek.empty and (pil_cek is None or i["item"] in pil_cek))
        v = st.checkbox(f"{i['item']} ×{i['qty']} · {logic.rupiah(i['subtotal'])}" + ("  — lunas" if i["lunas"] else ""),
                        value=awal, key=f"ck_{iso}_{nama}_{n}_{ver}")
        k = (i["order_id"], i["item"])
        if v:
            tot_lunas += i["subtotal"]
        if v and not i["lunas"]:
            want_lunas.append(k)
        elif not v and i["lunas"]:
            want_belum.append(k)
    _ringkas(tot_lunas, dibayar)
    ada_ubah = bool(want_lunas or want_belum or not cek.empty)
    c1, c2 = st.columns(2)
    if c1.button("Simpan", type="primary", width="stretch", disabled=not ada_ubah, key=f"sv_{iso}_{nama}_{ver}"):
        payments.simpan_pelunasan(store, nama, kode, want_lunas, want_belum, tgl=iso)
        st.session_state["_toast"] = f"Pembayaran {nama} tanggal {_tgl(iso)} tersimpan."
        kunci_muat()
    if not cek.empty:
        if c2.button("Tolak bukti", width="stretch", key=f"tk_{iso}_{nama}_{ver}"):
            payments.tolak_pembayaran(store, nama, kode, iso)
            kunci_muat()
    elif n_lunas:
        if c2.button("Batalkan semua lunas", width="stretch", key=f"bs_{iso}_{nama}_{ver}"):
            payments.simpan_pelunasan(store, nama, kode, [], [(i["order_id"], i["item"]) for i in its if i["lunas"]], tgl=iso, periksa=False)
            st.session_state["_toast"] = "Pelunasan dibatalkan."
            kunci_muat()


def pd_sum(df, kolom: str) -> float:
    import pandas as pd
    return float(pd.to_numeric(df[kolom], errors="coerce").fillna(0).sum())


def blok_total(store, kode: str, nama: str, kunci_muat) -> None:
    """Admin, jendela total periode: semua pesanan periode (per tanggal) bisa dicentang lunas satu per satu + tombol bukti per foto."""
    orders_ = payments.pesanan_periode(store, nama, kode)
    if not orders_:
        return
    bukti = payments.daftar_bukti(store, nama, kode)
    cek = payments.daftar(store, nama, kode)
    cek = cek[cek["status"] == payments.CEK]
    n_lunas = sum(1 for o in orders_ if o["lunas"])
    st.markdown("**Bukti bayar**" + (f" · {len(bukti)} foto" if bukti else ""))
    tombol_bukti(bukti)
    tgl_cek = {c for c in cek["tanggal"] if c}
    nominal_cek = pd_sum(cek, "jumlah") if not cek.empty else None
    sisa_total = sum(o["sisa"] for o in orders_)
    umum = (not cek.empty) and ("" in set(cek["tanggal"])) and int(round(nominal_cek)) == int(round(sisa_total))
    ver = f"{n_lunas}_{len(cek)}_{len(bukti)}"
    st.markdown("**Pesanan periode ini** — centang yang sudah dibayar (hilangkan centang untuk membatalkan)")
    want_lunas, want_belum, tot = [], [], 0.0
    tgl_now = None
    for n, o in enumerate(orders_):
        if o["tanggal"] != tgl_now:
            tgl_now = o["tanggal"]
        awal = o["lunas"] or (not cek.empty and (o["tanggal"] in tgl_cek or umum))
        teks = f"**{_tgl(o['tanggal'])}** · {', '.join(o['teks'])} · {logic.rupiah(o['total'])}"
        if o["n_lunas"] and not o["lunas"]:
            teks += f" · sebagian lunas, sisa {logic.rupiah(o['sisa'])}"
        v = st.checkbox(teks, value=awal, key=f"ct_{kode}_{nama}_{n}_{ver}")
        if v:
            tot += o["total"]
        if v and not o["lunas"]:
            want_lunas += [k for k in o["kunci"]]
        elif not v and o["lunas"]:
            want_belum += o["kunci"]
    _ringkas(tot, nominal_cek)
    ada = bool(want_lunas or want_belum or not cek.empty)
    c1, c2 = st.columns(2)
    if c1.button("Simpan", type="primary", width="stretch", disabled=not ada, key=f"svt_{kode}_{nama}_{ver}"):
        payments.simpan_pelunasan(store, nama, kode, want_lunas, want_belum, tgl=None)
        st.session_state["_toast"] = f"Pembayaran {nama} tersimpan."
        kunci_muat()
    if not cek.empty and c2.button("Tolak bukti", width="stretch", key=f"tkt_{kode}_{nama}_{ver}"):
        payments.tolak_pembayaran(store, nama, kode)
        kunci_muat()
