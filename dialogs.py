"""Jendela (dialog) untuk pesan/ubah, terima kasih, dan tinjau revisi."""
from __future__ import annotations

import hashlib
import html
from datetime import date

import streamlit as st

import logic
import orders
import services

rp = logic.rupiah


def _ringkas_html(items: list[dict]) -> str:
    return "".join(f'<div>{html.escape(i["item"])} ×{i["qty"]}'
                   f'<span style="float:right">{rp(i["qty"] * i["harga"])}</span></div>' for i in items)


@st.dialog("Pesan makanan")
def dialog_pesan(tgl: date, nama: str | None, admin: bool = False):
    store = services.get_store()
    if admin and not nama:
        pilih = st.selectbox("Pesanan untuk siapa?", [n for n in services.daftar_nama(store)
                                                      if n != st.secrets.get("admin_name", "ADMIN")],
                             index=None, placeholder="Ketik nama pelanggan")
        if not pilih:
            st.caption("Pilih pelanggan dulu.")
            return
        nama = pilih

    menu = orders.menu_tanggal(store, tgl)
    if menu.empty:
        st.info("Menu untuk tanggal ini belum diunggah admin.")
        return

    ada = orders.pesanan_saya(store, tgl, nama)
    awal_items = (ada["usulan"] if ada and ada["usulan"] and not ada["usulan_batal"] else ada["items"]) if ada else []
    awal = {i["item"]: i["qty"] for i in awal_items}
    awal_cat = (ada["catatan_usulan"] if ada and ada["usulan"] and not ada["usulan_batal"] else ada["catatan"]) if ada else ""
    sig = hashlib.md5(repr((awal_items, awal_cat, ada["status"] if ada else "")).encode()).hexdigest()[:6]
    kp = f"q_{tgl.isoformat()}_{hashlib.md5(nama.encode()).hexdigest()[:6]}_{sig}"

    st.markdown(f"**{html.escape(nama)}** · {logic.tanggal_panjang(tgl)}")
    if admin:
        st.caption("Mode admin: perubahan langsung berlaku tanpa persetujuan.")
    elif ada:
        if ada["status"] == "Revisi":
            st.info("Perubahan sebelumnya masih menunggu konfirmasi admin. Mengirim lagi akan menggantikannya.")
        else:
            st.caption("Ini mengubah pesananmu. Perubahan berlaku setelah dikonfirmasi admin.")
    if not admin:
        st.caption("Bisa diubah atau dibatalkan sampai pukul 10:15 WIB pada hari itu.")

    nama_menu = set(menu["nama"])
    pilihan: dict[str, int] = {}
    kat_terakhir = None
    for _, b in menu.iterrows():
        if b["kategori"] != kat_terakhir:
            st.markdown(f'<div class="kat-h">{html.escape(b["kategori"])}</div>', unsafe_allow_html=True)
            kat_terakhir = b["kategori"]
        sisa = orders.sisa_stok(store, tgl, b, kecuali_oid=orders.oid(tgl, nama))
        habis = sisa is not None and sisa <= 0
        tag = '<span class="habis-tag">HABIS</span>' if habis else ""
        kls = "habis" if habis else ""
        st.markdown(f'<div class="mi {kls}"><span class="n">{html.escape(b["nama"])}{tag}</span>'
                    f'<span class="h">{rp(b["harga"])}</span></div>', unsafe_allow_html=True)
        if habis:
            alt = [a for a in b["alternatif"] if a in nama_menu]
            if alt:
                st.markdown(f'<div class="alt">Coba menu lain: <b>{" · ".join(html.escape(a) for a in alt)}</b></div>',
                            unsafe_allow_html=True)
            continue
        maks = orders.MAKS_QTY if sisa is None else min(orders.MAKS_QTY, sisa)
        if sisa is not None and sisa <= orders.MAKS_QTY:
            st.markdown(f'<div class="sisa">Sisa {sisa}</div>', unsafe_allow_html=True)
        default = min(awal.get(b["nama"], 0), maks)
        v = st.segmented_control(b["nama"], list(range(0, maks + 1)), default=default,
                                 key=f"{kp}_{b['nama']}", label_visibility="collapsed")
        pilihan[b["nama"]] = int(v or 0)

    catatan = st.text_input("Catatan (opsional)", value=awal_cat, key=f"{kp}_cat",
                            placeholder="mis. sambal dipisah, nasi sedikit")
    total = sum(q * float(menu.loc[menu["nama"] == n, "harga"].iloc[0]) for n, q in pilihan.items() if q)
    jml = sum(pilihan.values())

    with st.container(key="bar_pesan"):
        st.markdown(f'<div class="bar-total"><span>{jml} item</span><b>{rp(total)}</b></div>', unsafe_allow_html=True)
        label = "Simpan perubahan" if ada else "Pesan sekarang"
        if st.button(label, type="primary", width="stretch", disabled=jml == 0, key=f"{kp}_go"):
            ok, msg, mode = orders.simpan_pesanan(store, tgl, nama, pilihan, catatan.strip(), admin=admin)
            if ok:
                orders.snapshot_harian(store, tgl)
                st.session_state["thanks"] = {
                    "nama": nama, "tgl": tgl, "mode": mode, "msg": msg, "total": total,
                    "items": [{"item": n, "qty": q, "harga": float(menu.loc[menu["nama"] == n, "harga"].iloc[0])}
                              for n, q in pilihan.items() if q]}
                st.rerun()
            else:
                st.error(msg)
        if ada:
            kc = f"{kp}_konf"
            if st.session_state.get(kc):
                st.warning("Yakin ingin membatalkan seluruh pesanan?" + ("" if admin else " Pembatalan menunggu konfirmasi admin."))
                with st.container(key=f"row_{kp}_c"):
                    a, b2 = st.columns(2)
                    if a.button("Ya, batalkan", type="primary", width="stretch", key=f"{kp}_ya"):
                        ok, msg, mode = orders.batalkan_pesanan(store, tgl, nama, admin=admin)
                        if ok:
                            orders.snapshot_harian(store, tgl)
                            st.session_state["thanks"] = {"nama": nama, "tgl": tgl, "mode": "batal-" + mode, "msg": msg,
                                                          "total": 0, "items": []}
                            st.rerun()
                        else:
                            st.error(msg)
                    if b2.button("Tidak", width="stretch", key=f"{kp}_tdk"):
                        st.session_state[kc] = False
                        st.rerun(scope="fragment")
            elif st.button("Batalkan pesanan", width="stretch", key=f"{kp}_batal"):
                st.session_state[kc] = True
                st.rerun(scope="fragment")


@st.dialog("Terima kasih!")
def dialog_terima_kasih(info: dict):
    mode = info["mode"]
    if mode.startswith("batal"):
        ikon, judul = ("🗑️", "Pembatalan dikirim") if mode == "batal-revisi" else ("🗑️", "Pesanan dibatalkan")
        sub = info["msg"]
    elif mode == "revisi":
        ikon, judul, sub = "⏳", "Perubahan terkirim", "Admin akan mengonfirmasi perubahanmu. Sampai itu, pesanan lamamu yang berlaku."
    elif mode == "admin":
        ikon, judul, sub = "✅", "Pesanan diperbarui", f"Pesanan {info['nama']} sudah diubah."
    else:
        ikon, judul, sub = "🍛", "Terima kasih atas pembeliannya!", f"Pesananmu untuk {logic.tanggal_panjang(info['tgl'])} sudah masuk."
    ring = ""
    if info["items"]:
        ring = f'<div class="ringkas">{_ringkas_html(info["items"])}<hr style="margin:.4rem 0;border:0;border-top:1px solid #EADBC8">' \
               f'<b>Total <span style="float:right">{rp(info["total"])}</span></b></div>'
    st.markdown(f'<div class="thanks"><div class="ic">{ikon}</div><h3>{judul}</h3><p>{html.escape(sub)}</p>{ring}</div>',
                unsafe_allow_html=True)
    if st.button("Tutup", type="primary", width="stretch"):
        st.rerun()


def _tabel_mini(items: list[dict]) -> str:
    if not items:
        return "<i>—</i>"
    rows = "".join(f'<tr><td>{html.escape(i["item"])}</td><td>×{i["qty"]}</td></tr>' for i in items)
    return f'<table class="mini">{rows}</table>'


@st.dialog("Pesanan lama vs baru")
def dialog_tinjau(order_id: str, tgl: date, nama: str):
    store = services.get_store()
    o = orders.pesanan_saya(store, tgl, nama)
    if not o or o["usulan"] is None:
        st.info("Tidak ada revisi yang menunggu.")
        return
    st.markdown(f"**{html.escape(nama)}** · {logic.tanggal_panjang(tgl)}")
    st.markdown("**Pesanan lama**", help="Versi yang berlaku sekarang")
    st.markdown(_tabel_mini(o["items"]) + (f'<div class="sisa">Catatan: {html.escape(o["catatan"])}</div>' if o["catatan"] else ""),
                unsafe_allow_html=True)
    st.markdown("**Pesanan baru**")
    if o["usulan_batal"]:
        st.markdown('<div class="diff-minus">Pelanggan membatalkan seluruh pesanan.</div>', unsafe_allow_html=True)
    else:
        st.markdown(_tabel_mini(o["usulan"]) + (f'<div class="sisa">Catatan: {html.escape(o["catatan_usulan"])}</div>' if o["catatan_usulan"] else ""),
                    unsafe_allow_html=True)
        lama = {i["item"]: i["qty"] for i in o["items"]}
        baru = {i["item"]: i["qty"] for i in o["usulan"]}
        baris = []
        for n in sorted(set(lama) | set(baru)):
            a, b = lama.get(n, 0), baru.get(n, 0)
            if a == b:
                continue
            if b == 0:
                baris.append(f'<div class="diff-minus">− {html.escape(n)} ×{a} (dihapus)</div>')
            elif a == 0:
                baris.append(f'<div class="diff-plus">+ {html.escape(n)} ×{b} (tambah)</div>')
            else:
                baris.append(f'<div class="{"diff-plus" if b > a else "diff-minus"}">{"+" if b > a else "−"} {html.escape(n)}: {a} → {b}</div>')
        if o["catatan"] != o["catatan_usulan"]:
            baris.append('<div class="sisa">Catatan diubah.</div>')
        st.markdown('<div class="rbox"><div class="jdl">Perubahan</div>' + "".join(baris) + "</div>", unsafe_allow_html=True)
    with st.container(key="row_tinjau"):
        a, b = st.columns(2)
        if a.button("Konfirmasi", type="primary", width="stretch"):
            orders.setujui(store, order_id)
            orders.snapshot_harian(store, tgl)
            st.rerun()
        if b.button("Tolak", width="stretch"):
            orders.tolak(store, order_id)
            orders.snapshot_harian(store, tgl)
            st.rerun()
