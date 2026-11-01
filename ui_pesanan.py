"""Komponen tampilan pesanan: form pesan (dialog), terima kasih, revisi admin, tabel Pesanan Hari Ini."""
from __future__ import annotations

import html
from datetime import date

import streamlit as st

import logic
import orders
import services
from orders import KATEGORI, KELOMPOK

HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
KELAS = {"Dipesan": "s-baru", "Revisi": "s-rev", "Minta batal": "s-rev", "Disetujui": "s-ok", "Dibungkus": "s-pack"}


def label_tgl(d: date) -> str:
    return f"{HARI[d.weekday()]}, {d.day} {logic.BULAN[d.month][:3]}"


def _esc(x) -> str:
    return html.escape(str(x))


# ===================================================================== form pesan (bentuk tabel)
GRUP = [("Lauk", "Lauk", ["Ayam Sayur", "Lauk"]), ("Minuman", "Minuman", ["Minuman"]), ("Lain-lain", "Lain-lain", ["Lain-lain"])]


def _hrg(n: float, aktif: bool = True) -> None:
    st.markdown(f'<div class="hrg">{logic.rupiah(n) if aktif and n else "—"}</div>', unsafe_allow_html=True)


@st.dialog("Pesan makanan")
def dialog_pesan(tgl_iso: str, nama: str, langsung: bool = False):
    store = services.get_store()
    tgl = date.fromisoformat(tgl_iso)
    menu = orders.menu_hari(store, tgl)
    lama = {i["item"]: i for i in orders.items_pesanan(store, tgl, nama)}
    ada = bool(lama)
    rev = orders.revisi_menunggu(store, tgl, nama)
    awal = {i["item"]: i for i in rev["items"]} if rev and rev["jenis"] == "ubah" else lama  # isian awal form
    _gr = orders.nama_gratis(store)
    awal = {k_: v for k_, v in awal.items() if k_.lower() not in _gr}      # pendamping gratis ditambahkan otomatis, bukan dipilih

    st.markdown(f"**{label_tgl(tgl)}** · atas nama **{_esc(nama)}**")
    pengguna = services.user() or nama
    if pengguna != nama:
        st.caption(f"Kamu memesankan untuk {nama}. Tercatat dipesan oleh {pengguna}.")
    if ada and not langsung:
        st.info(f"Mengubah pesanan perlu persetujuan admin. Sebelum disetujui, pesanan lama yang berlaku. Batas ubah: {logic.BATAS_TEKS} WIB.")
    if rev:
        st.warning("Perubahan sebelumnya masih menunggu admin. Mengirim lagi akan menggantikannya.")

    sisa = orders.batas_stok(store, tgl, nama)
    k = f"{tgl_iso}_{nama}"
    pilihan: dict[str, int] = {}
    harga: dict[str, float] = {}
    habis: list[str] = []

    def info(r):
        harga[r.nama] = lama[r.nama]["harga"] if r.nama in lama else float(r.harga)
        cap = sisa.get(r.nama)
        if cap is not None and cap == 0:
            habis.append(f"<b>{_esc(r.nama)}</b>" + (f" (coba: {_esc(r.alternatif)})" if r.alternatif else ""))
            return None
        return cap

    with st.container(key="tabel_psn"):
        h = st.columns([5.2, 3.1, 3.3], gap="small")
        h[0].markdown('<div class="th">Menu</div>', unsafe_allow_html=True)
        h[1].markdown('<div class="th c">Jumlah</div>', unsafe_allow_html=True)
        h[2].markdown('<div class="th r">Harga</div>', unsafe_allow_html=True)

        # --- Nasi: centang (otomatis tercentang untuk pesanan baru) + jumlah + harga
        nasi = menu[menu["kategori"] == "Nasi"]
        if not nasi.empty:
            r = next(nasi.itertuples())
            cap = info(r)
            c = st.columns([5.2, 3.1, 3.3], gap="small", vertical_alignment="center")
            pakai = c[0].checkbox(f"**{r.nama}**", value=(r.nama in awal) if ada else True, key=f"nasi_on_{k}")
            q = c[1].number_input("Jumlah nasi", 1, cap if cap else 99, int(awal[r.nama]["qty"]) if r.nama in awal else 1,
                                  key=f"nasi_q_{k}", disabled=not pakai, label_visibility="collapsed")
            if pakai:
                pilihan[r.nama] = int(q)
            with c[2]:
                _hrg(q * harga[r.nama], pakai)

        # --- Lauk / Minuman / Lain-lain: pilih menu (sejajar dengan Nasi) + jumlah + harga
        for judul, kunci, kats in GRUP:
            sub = menu[menu["kategori"].isin(kats)]
            if sub.empty:
                continue
            ada_item = [i for i in awal.values() if i["kategori"] in kats]
            nbaris = max(1, len(ada_item)) + st.session_state.get(f"ex_{kunci}_{k}", 0)
            tersedia = []
            for r in sub.itertuples():
                if info(r) is not None or sisa.get(r.nama) is None:
                    tersedia.append(r)
            nama_opsi = [r.nama for r in tersedia]
            st.markdown(f'<div class="kat">{judul}</div>', unsafe_allow_html=True)
            for b in range(nbaris):
                aw = ada_item[b] if b < len(ada_item) else None
                idx = nama_opsi.index(aw["item"]) if aw and aw["item"] in nama_opsi else None
                c = st.columns([5.2, 3.1, 3.3], gap="small", vertical_alignment="center")
                pil = c[0].selectbox(f"Pilih {judul.lower()}", nama_opsi, index=idx, placeholder=f"Pilih {judul.lower()}",
                                     key=f"sel_{kunci}_{b}_{k}", label_visibility="collapsed")
                cap = sisa.get(pil) if pil else None
                q = c[1].number_input(f"Jumlah {judul.lower()}", 1, cap if cap else 99, int(aw["qty"]) if aw else 1,
                                      key=f"qty_{kunci}_{b}_{k}", disabled=not pil, label_visibility="collapsed")
                if pil:
                    pilihan[pil] = pilihan.get(pil, 0) + int(q)
                with c[2]:
                    _hrg(q * harga[pil] if pil else 0, bool(pil))
            if st.button(f"Tambah {judul.lower()}", key=f"tambah_{kunci}_{k}", type="tertiary"):
                st.session_state[f"ex_{kunci}_{k}"] = st.session_state.get(f"ex_{kunci}_{k}", 0) + 1
                st.rerun(scope="fragment")

    if habis:
        st.markdown('<div class="habis">Sedang habis: ' + ", ".join(habis) + "</div>", unsafe_allow_html=True)

    catatan = st.text_input("Catatan (opsional)", value=orders.catatan_pesanan(store, tgl, nama),
                            placeholder="mis. sambal dipisah, nasi sedikit", key=f"cat_{k}")
    total = sum(q * harga[n] for n, q in pilihan.items())

    with st.container(key="bar_total"):
        st.markdown(f'<div class="total-bar"><span>TOTAL PESANAN</span><b>{logic.rupiah(total)}</b></div>', unsafe_allow_html=True)
        if st.session_state.get("_konfirm_batal"):
            st.warning("Yakin batalkan seluruh pesanan ini?")
            if st.button("Ya, batalkan pesanan", type="primary", width="stretch"):
                err = orders.batalkan_pesanan(store, tgl, nama, langsung=langsung)
                st.session_state.pop("_konfirm_batal", None)
                if err:
                    st.error(err)
                else:
                    st.session_state["_sukses"] = {"kind": "batal-langsung" if langsung else "batal", "tgl": tgl_iso, "total": 0}
                    st.rerun()
            if st.button("Tidak jadi", width="stretch"):
                st.session_state.pop("_konfirm_batal", None)
                st.rerun(scope="fragment")
        else:
            label = ("Simpan perubahan" if langsung else "Kirim revisi") if ada else "Pesan sekarang"
            if st.button(label, type="primary", width="stretch", disabled=total <= 0):
                err = None
                if langsung and ada and not services.is_penuh() and any(pilihan.get(n, 0) < i["qty"] for n, i in lama.items()
                                                                       if n.lower() not in _gr):
                    st.error("Mode terbatas: admin hanya boleh menambah pesanan. Untuk mengurangi atau membatalkan, "
                             "buka kunci 2FA (ketuk Krish dua kali di Beranda).")
                    st.stop()
                err, kind = orders.simpan_pesanan(store, tgl, nama, pilihan, catatan.strip(), langsung=langsung, oleh=pengguna)
                if err:
                    st.error(err)
                else:
                    st.session_state["_sukses"] = {"kind": kind, "tgl": tgl_iso, "total": total}
                    st.rerun()
            if ada and (not langsung or services.is_penuh()) and st.button("Batalkan pesanan", width="stretch"):
                st.session_state["_konfirm_batal"] = True
                st.rerun(scope="fragment")


# ===================================================================== rincian pesanan (riwayat, hanya baca)
def _rincian_tabel(items: list[dict]) -> str:
    if not items:
        return '<div class="kosong-info">— kosong (dibatalkan) —</div>'
    rows = "".join(f"<tr><td>{_esc(i['item'])}</td><td class='c'>{i['qty']}</td><td>{logic.rupiah(i['harga'])}</td>"
                   f"<td>{logic.rupiah(i['qty'] * i['harga'])}</td></tr>" for i in items)
    tot = sum(i["qty"] * i["harga"] for i in items)
    return (f'<table class="mini rinci"><tr><th>Menu</th><th class="c">Jml</th><th>Harga</th><th>Total</th></tr>{rows}'
            f'<tr class="gt"><td colspan="3">TOTAL</td><td>{logic.rupiah(tot)}</td></tr></table>')


def _muat_ulang(iso: str, nama: str) -> None:
    """Segarkan seluruh halaman (tabel ikut berubah); jendela tertutup dan kabar singkat muncul sebagai toast."""
    st.rerun()


def _blok_bayar(store, tgl: date, nama: str, admin: bool) -> None:
    """Baris pembayaran tepat di bawah TOTAL: status + tombol (pelanggan: Bayar sekarang, admin: Konfirmasi lunas)."""
    import payments
    kode = logic.kode_periode(logic.periode_untuk(tgl)[0])
    iso = tgl.isoformat()
    if admin and not services.is_penuh():
        t = payments.tagihan(store, nama, kode, iso)
        st.markdown(f'<div class="bayar-stat {"ok" if t["lunas"] else "belum"}"><small>Pembayaran</small><b>{"✓ LUNAS" if t["lunas"] else "BELUM LUNAS"}</b></div>',
                    unsafe_allow_html=True)
        st.caption("🔒 Konfirmasi pembayaran terkunci. Buka dengan 2FA: ketuk Krish dua kali di Beranda.")
        return
    if admin:    # admin: lihat bukti, centang item yang lunas, simpan / batalkan (tanpa muat ulang halaman sampai disimpan)
        import ui_bayar
        ui_bayar.blok_harian(store, tgl, nama, lambda: _muat_ulang(iso, nama))
        return
    t = payments.tagihan(store, nama, kode, iso)
    cek = payments.menunggu_cek(store, nama, kode, iso)
    its = payments.item_belum_lunas(store, nama, kode, iso)
    sebagian = (not t["lunas"]) and any(i["lunas"] for i in its)
    if t["lunas"]:
        stat, kls = "✓ LUNAS", "ok"
    elif not cek.empty:
        stat, kls = "⏳ MENUNGGU CEK ADMIN", "cek"
    elif sebagian:
        stat, kls = f"SEBAGIAN LUNAS · sisa {logic.rupiah(t['sisa'])}", "cek"
    else:
        stat, kls = "BELUM DIBAYAR", "belum"
    pemilik = nama == services.user()
    bisa_pilih = (admin or pemilik) and not t["lunas"] and cek.empty
    pilih: list[str] | None = None
    if bisa_pilih:   # centang item yang mau dibayar
        st.markdown("**Pilih yang dibayar**")
        pilih = []
        for i in its:
            if i["lunas"]:
                st.markdown(f'<div class="cap">✓ {_esc(i["item"])} ×{i["qty"]} · {logic.rupiah(i["subtotal"])} — sudah lunas</div>', unsafe_allow_html=True)
            elif st.checkbox(f'{i["item"]} ×{i["qty"]} · {logic.rupiah(i["subtotal"])}', value=True, key=f"pil_{iso}_{nama}_{i['item']}"):
                pilih.append(i["item"])
        tot_pilih = sum(i["subtotal"] for i in its if i["item"] in pilih)
        st.caption(f"Dibayar sekarang: **{logic.rupiah(tot_pilih)}**")
    with st.container(key="bar_bayar"):
        c = st.columns([1.15, 1], gap="small", vertical_alignment="center")
        c[0].markdown(f'<div class="bayar-stat {kls}"><small>Pembayaran</small><b>{stat}</b></div>', unsafe_allow_html=True)
        kosong = pilih is not None and not pilih
        if admin:
            if t["lunas"] or sebagian:
                if c[1].button("Batalkan lunas", key=f"bl_{iso}_{nama}", width="stretch"):
                    payments.batalkan_lunas(store, nama, kode, iso)
                    _muat_ulang(iso, nama)
            if not t["lunas"]:
                tbl = st.columns(1)[0] if sebagian else c[1]
                if tbl.button("Konfirmasi lunas", key=f"kl_{iso}_{nama}", type="primary", width="stretch", disabled=kosong):
                    payments.konfirmasi_lunas(store, nama, kode, tgl=iso, pilih=pilih)
                    _muat_ulang(iso, nama)
        elif not t["lunas"] and cek.empty and pemilik:
            if c[1].button("Bayar sekarang", key=f"by_{iso}_{nama}", type="primary", width="stretch", disabled=kosong):
                st.session_state["_open"] = ("bayar", kode, nama, iso, pilih)
                st.rerun()
        elif not t["lunas"] and pemilik:       # sudah ada bukti menunggu cek: boleh kirim bukti tambahan
            if c[1].button("Kirim bukti lagi", key=f"by2_{iso}_{nama}", width="stretch"):
                st.session_state["_open"] = ("bayar", kode, nama, iso, None)
                st.rerun()
    if admin and services.is_penuh():
        for p in cek.itertuples():
            st.warning(f"Bukti transfer {logic.rupiah(float(p.jumlah))} dari pelanggan, tagihan {logic.rupiah(float(p.tagihan))}.")
            _bukti_img(p.bukti)
            if st.button("Tolak bukti transfer", key=f"tb_{iso}_{nama}", width="stretch"):
                payments.tolak_pembayaran(store, nama, kode, iso)
                _muat_ulang(iso, nama)


@st.dialog("Rincian pesanan")
def dialog_rincian(tgl_iso: str, nama: str, admin: bool = False):
    store = services.get_store()
    if admin and st.session_state.get("_lihat_bukti"):
        import ui_bayar
        ui_bayar.halaman_bukti(store, st.session_state["_lihat_bukti"])
        return
    tgl = date.fromisoformat(tgl_iso)
    items = orders.items_pesanan(store, tgl, nama)
    rev = orders.revisi_menunggu(store, tgl, nama)
    st.markdown(f"**{label_tgl(tgl)} {tgl.year}** · **{_esc(nama)}**")
    if not items:
        st.info("Tidak ada pesanan pada tanggal ini.")
    else:
        st.markdown(_rincian_tabel(items), unsafe_allow_html=True)
        oleh = orders.pemesan(store, tgl, nama)
        if oleh and oleh != nama:
            st.caption(f"🧾 Dipesan oleh {oleh}")
        cat = orders.catatan_pesanan(store, tgl, nama)
        if cat:
            st.caption(f"📝 {cat}")
    if items:
        _blok_bayar(store, tgl, nama, admin)
    if rev:
        st.markdown('<div class="psn s-rev"><b>Menunggu konfirmasi admin</b> — perubahan yang diajukan:</div>', unsafe_allow_html=True)
        st.markdown(_rincian_tabel(rev["items"]) if rev["jenis"] != "batal" else '<div class="kosong-info">Permintaan batal pesanan</div>',
                    unsafe_allow_html=True)
        if admin:
            c1, c2 = st.columns(2)
            if c1.button("Konfirmasi", type="primary", width="stretch"):
                orders.konfirmasi_revisi(store, tgl, nama)
                st.rerun()
            if c2.button("Tolak", width="stretch"):
                orders.tolak_revisi(store, tgl, nama)
                st.rerun()
    if admin and tgl < logic.today_wib():
        st.caption("🔒 Pesanan tanggal yang sudah lewat tidak bisa diubah.")
    elif admin:
        if st.button("Ubah pesanan (admin)" if items else "Buat pesanan", width="stretch"):
            st.session_state["_open"] = ("pesan", tgl_iso, nama, True)
            st.rerun()
    elif items and orders.bisa_ubah(store, tgl):
        if st.button("Ubah / batalkan pesanan", type="primary", width="stretch"):
            st.session_state["_open"] = ("pesan", tgl_iso, nama, False)
            st.rerun()
    elif items:
        st.caption("🔒 Order ditutup admin, pesanan ini tidak bisa diubah lagi." if orders.is_tutup(store, tgl)
                   else f"🔒 Sudah lewat batas {logic.BATAS_TEKS} WIB, pesanan ini tidak bisa diubah lagi.")


# ===================================================================== tagihan & pembayaran
def rekening() -> dict:
    return {"bank": services.secret("rekening_bank", "BNI"), "nomor": services.secret("rekening_nomor", "0258578828"),
            "nama": services.secret("rekening_nama", "NUR HABIBAH")}


def _bukti_img(b64: str) -> None:
    import base64
    if b64 and len(b64) > 20:
        st.image(base64.b64decode(b64), width=220)


@st.dialog("Tagihan kasbon")
def dialog_tagihan(kode: str, nama: str, admin: bool = False):
    import payments
    store = services.get_store()
    if admin and st.session_state.get("_lihat_bukti"):
        import ui_bayar
        ui_bayar.halaman_bukti(store, st.session_state["_lihat_bukti"])
        return
    th, bl = (int(x) for x in kode.split("-"))
    start = date(th, bl, logic.CUTOFF_HARI + 1)
    a, b = logic.periode_untuk(start)
    t = payments.tagihan(store, nama, kode)
    st.markdown(f"**{_esc(nama)}** · periode {logic.label_periode(a, b)}")
    if not t["per_hari"]:
        st.info("Belum ada pembelian pada periode ini.")
        return
    rows = "".join(f"<tr><td>{label_tgl(date.fromisoformat(d))}</td><td>{logic.rupiah(v['total'])}{' ✓ lunas' if v['lunas'] else (' · sisa ' + logic.rupiah(v['sisa']) if v['sisa'] < v['total'] else '')}</td></tr>"
                   for d, v in t["per_hari"].items())
    st.markdown(f'<table class="mini rinci"><tr><th>Tanggal</th><th>Total</th></tr>{rows}'
                f'<tr><td>Total pembelian</td><td>{logic.rupiah(t["total"])}</td></tr>'
                f'<tr class="gt"><td>TOTAL KASBON (belum dibayar)</td><td>{logic.rupiah(t["sisa"])}</td></tr></table>', unsafe_allow_html=True)
    stat = payments.status_periode(store, nama, kode)
    if t["lunas"]:
        st.success("✓ LUNAS")
    else:
        st.markdown(f'<div class="kartu"><small>Belum dibayar</small><div class="besar">{logic.rupiah(t["sisa"])}</div>'
                    f'<small>Jatuh tempo {logic.CUTOFF_HARI} {logic.BULAN[b.month]} {b.year} · status: {stat}</small></div>', unsafe_allow_html=True)
    cek = payments.menunggu_cek(store, nama, kode)
    if admin and not services.is_penuh():
        st.caption("🔒 Konfirmasi pembayaran terkunci. Buka dengan 2FA: ketuk Krish dua kali di Beranda.")
    elif admin:
        import ui_bayar

        def _buka_lagi():
            st.rerun()
        ui_bayar.blok_total(store, kode, nama, _buka_lagi)
    else:
        for p in cek.itertuples():
            st.warning(f"Bukti transfer {logic.rupiah(float(p.jumlah))} menunggu dicek admin.")
        if not t["lunas"] and st.button("Bayar sekarang", type="primary", width="stretch"):
            st.session_state["_open"] = ("bayar", kode, nama)
            st.rerun()


@st.dialog("Bayar kasbon")
def dialog_bayar(kode: str, nama: str, tgl_iso: str | None = None, pilih: list[str] | None = None):
    import payments
    from pathlib import Path
    store = services.get_store()
    t = payments.tagihan(store, nama, kode, tgl_iso, pilih)
    if t["sisa"] <= 0:
        st.success("Tidak ada tagihan yang tersisa. Terima kasih!")
        return
    rek = rekening()
    st.markdown(f'<div class="kartu"><small>Yang harus dibayar{" · pesanan " + label_tgl(date.fromisoformat(tgl_iso)) if tgl_iso else ""}{" · " + ", ".join(pilih) if pilih else ""}</small><div class="besar">{logic.rupiah(t["sisa"])}</div></div>',
                unsafe_allow_html=True)
    st.markdown("**Transfer ke rekening:**")
    logo = Path(__file__).parent / "assets" / "bni.png"
    if logo.exists():
        import base64
        lg = f'<img class="bank-logo" src="data:image/png;base64,{base64.b64encode(logo.read_bytes()).decode()}">'
    else:
        lg = f'<span class="bank-badge">{_esc(rek["bank"])}</span>'
    st.markdown(f'<div class="bank-row">{lg}<span class="bank-nama">Bank {_esc(rek["bank"])}</span></div>', unsafe_allow_html=True)
    with st.container(key="rek"):
        st.code(rek["nomor"], language=None)  # ikon salin ada di pojok kanan kotak
    st.markdown(f'<div class="bank-an">a.n. <b>{_esc(rek["nama"])}</b></div>', unsafe_allow_html=True)
    st.divider()
    jumlah = st.number_input("Jumlah yang kamu transfer (Rp)", min_value=0, value=int(t["sisa"]), step=1000, key=f"bayar_jml_{kode}_{tgl_iso}_{int(t['sisa'])}")
    foto = st.file_uploader("Unggah foto bukti pembayaran", type=["jpg", "jpeg", "png", "webp"], key=f"bayar_foto_{kode}_{tgl_iso}")
    if foto:
        st.image(foto, width=200)
    st.caption("Bukti dikirim ke admin. Status lunas berubah setelah admin mengecek bukti pembayaranmu.")
    if st.button("Kirim bukti pembayaran", type="primary", width="stretch"):
        err, status = payments.kirim_pembayaran(store, nama, kode, float(jumlah), foto.getvalue() if foto else None, tgl_iso, pilih)
        if err:
            st.error(err)
        else:
            st.session_state["_sukses"] = {"kind": "bayar-cek",
                                           "tgl": logic.today_wib().isoformat(), "total": float(jumlah)}
            st.rerun()


@st.dialog("Terima kasih 🙏")
def dialog_sukses(info: dict):
    tgl = date.fromisoformat(info["tgl"])
    kind = info["kind"]
    if kind == "baru":
        st.markdown(f"### Terima kasih atas pembeliannya!")
        st.markdown(f"Pesanan **{label_tgl(tgl)}** sebesar **{logic.rupiah(info['total'])}** sudah tercatat sebagai kasbon.")
        st.caption(f"Masih bisa diubah atau dibatalkan sampai pukul {logic.BATAS_TEKS} WIB hari itu.")
    elif kind == "revisi":
        st.markdown("### Perubahan terkirim")
        st.markdown("Admin akan mengecek. Sampai disetujui, **pesanan lama** yang berlaku dan tertagih.")
    elif kind == "batal":
        st.markdown("### Permintaan batal terkirim")
        st.markdown("Pesanan baru benar-benar batal setelah admin mengonfirmasi.")
    elif kind == "bayar-cek":
        st.markdown("### Bukti pembayaran tersimpan")
        st.markdown(f"Nominal **{logic.rupiah(info['total'])}**. Admin akan mengecek bukti ini lalu menandai pembelian yang lunas.")
    elif kind == "batal-langsung":
        st.markdown("### Pesanan dibatalkan")
    else:
        st.markdown("### Tersimpan")
    if st.button("Tutup", type="primary", width="stretch"):
        st.rerun()


# ===================================================================== revisi (admin)
def _tabel_mini(items: list[dict]) -> str:
    if not items:
        return '<div class="kosong-info">— kosong (dibatalkan) —</div>'
    rows = "".join(f"<tr><td>{_esc(i['item'])}</td><td>{i['qty']}</td></tr>" for i in items)
    return f'<table class="mini"><tr><th>Item</th><th>Jml</th></tr>{rows}</table>'


@st.dialog("Perubahan pesanan")
def dialog_revisi(tgl_iso: str, nama: str):
    store = services.get_store()
    tgl = date.fromisoformat(tgl_iso)
    rev = orders.revisi_menunggu(store, tgl, nama)
    if not rev:
        st.info("Tidak ada perubahan yang menunggu.")
        if st.button("Tutup", width="stretch"):
            st.rerun()
        return
    lama = orders.items_pesanan(store, tgl, nama)
    st.markdown(f"**{_esc(nama)}** · {label_tgl(tgl)}")
    diff = "".join(
        f'<span class="diff {"tambah" if s == "+" else "kurang"}">{"tambah" if s == "+" else "kurang"} {n} {_esc(i)}</span>'
        for s, i, n in orders.selisih(lama, rev["items"]) if s != "=")
    st.markdown(f"**Yang berubah:** {diff or '—'}", unsafe_allow_html=True)
    st.markdown("**Pesanan lama**")
    st.markdown(_tabel_mini(lama), unsafe_allow_html=True)
    st.markdown("**Pesanan baru**")
    st.markdown(_tabel_mini(rev["items"]), unsafe_allow_html=True)
    if rev["catatan"]:
        st.caption(f"Catatan baru: {rev['catatan']}")
    if st.button("Konfirmasi", type="primary", width="stretch"):
        orders.konfirmasi_revisi(store, tgl, nama)
        st.rerun()
    if st.button("Tolak (tetap pesanan lama)", width="stretch"):
        orders.tolak_revisi(store, tgl, nama)
        st.rerun()


# ===================================================================== tabel Pesanan Hari Ini
def _kartu_html(o: dict, no: int, me: str | None) -> str:
    kelas = KELAS.get(o["status"], "s-baru")
    utama = o["utama"] or o["ekstra"]
    ekstra = o["ekstra"] if o["utama"] else ""
    jml = f'×{o["jumlah"]}' if o["seragam"] else ""
    info = ""
    if o["revisi"]:
        info = ('<div class="info">Minta dibatalkan · menunggu admin</div>' if o["revisi"]["jenis"] == "batal"
                else '<div class="info">Minta ubah pesanan · menunggu admin</div>')
    aku = " me" if o["nama"] == me else ""
    return (f'<div class="psn {kelas}{aku}"><div class="r1"><span class="no">{no}.</span>'
            f'<span class="nm">{_esc(o["nama"]).upper()}</span><span class="jml">{jml}</span>'
            f'<span class="chip {kelas}">{_esc(o["status"]).upper()}</span></div>'
            f'<div class="isi">{_esc(utama)}</div>'
            + (f'<div class="ekstra">{_esc(ekstra)}</div>' if ekstra else "")
            + (f'<div class="cat">📝 {_esc(o["catatan"])}</div>' if o["catatan"] else "")
            + (f'<div class="oleh">🧾 dipesan oleh {_esc(o["oleh"])}</div>' if o.get("oleh") else "")
            + info + "</div>")


def _rekap_html(semua: list[dict], admin: bool) -> str:
    """Rekap pesanan hari ini. Setiap baris bisa diketuk untuk melihat siapa saja yang memesan (dan menandai dibungkus)."""
    paket = lauk_saja = nasi_saja = 0
    for o in semua:
        p, l, n = orders.porsi_orang(o)
        paket, lauk_saja, nasi_saja = paket + p, lauk_saja + l, nasi_saja + n
    per_kat: dict[str, list[tuple[str, int]]] = {}
    kat_item = {i["item"]: i["kategori"] for o in semua for i in o["items"]}
    for nm, q in orders.rekap(semua).items():
        per_kat.setdefault(kat_item[nm], []).append((nm, q))

    def baris(label: str, q: int, kunci: str) -> str:
        return (f'<tr class="klik" data-c="r|{html.escape(kunci, quote=True)}"><td>{_esc(label)}</td>'
                f'<td class="q">{q}</td><td class="pn">›</td></tr>')

    rows = ['<tr class="sec"><td colspan="3">PORSI</td></tr>']
    if paket:
        rows.append(baris("Paket nasi & lauk", paket, "paket"))
    if lauk_saja:
        rows.append(baris("Lauk saja (tanpa nasi)", lauk_saja, "lauk"))
    if nasi_saja:
        rows.append(baris("Nasi saja (tanpa lauk)", nasi_saja, "nasi"))
    for kat in KATEGORI:
        if kat in per_kat and kat != "Nasi":
            rows.append(f'<tr class="sec"><td colspan="3">{kat.upper()}</td></tr>')
            rows += [baris(n, q, "i:" + n) for n, q in per_kat[kat]]
    belum = sum(1 for o in semua if o["status"] != "Dibungkus")
    rows.append(f'<tr class="tot"><td>Pelanggan</td><td class="q" colspan="2">{len(semua)} orang</td></tr>')
    rows.append(f'<tr class="tot"><td>Sudah dibungkus</td><td class="q" colspan="2">{len(semua) - belum} / {len(semua)}</td></tr>')
    if admin:
        rows.append(f'<tr class="tot"><td>Total tagihan</td><td class="q" colspan="2">{logic.rupiah(sum(o["total"] for o in semua))}</td></tr>')
    return (f'<div class="rk-akhir"><h4>REKAP PESANAN</h4><div class="cap2">Ketuk baris untuk melihat siapa yang memesan</div>'
            f'<table>{"".join(rows)}</table></div>')


def _revisi_html(o: dict) -> str:
    """Kartu permintaan revisi: pesanan lama vs baru, perubahan disorot, plus catatan otomatis."""
    rev = o["revisi"]
    lama = {i["item"]: i["qty"] for i in o["items"]}
    if rev["jenis"] == "batal":
        baru = {}
        notes = ["Pelanggan meminta pesanan dibatalkan"]
    else:
        baru = {i["item"]: i["qty"] for i in rev["items"]}
        notes = orders.catatan_perubahan(o["items"], rev["items"], o["catatan"], rev["catatan"])
    rows = []
    for nm in list(dict.fromkeys(list(lama) + list(baru))):
        a, b = lama.get(nm), baru.get(nm)
        kls = "tambah" if a is None else "hapus" if b is None else "ubah" if a != b else ""
        rows.append(f'<tr class="{kls}"><td>{_esc(nm)}</td><td class="c">{a if a is not None else "—"}</td>'
                    f'<td class="c">{b if b is not None else "—"}</td></tr>')
    cat = ""
    if rev["jenis"] != "batal" and rev["catatan"]:
        cat = f'<div class="cat">📝 Catatan baru: {_esc(rev["catatan"])}</div>'
    return (f'<div class="psn s-rev"><div class="r1"><span class="nm">{_esc(o["nama"]).upper()}</span>'
            f'<span class="chip s-rev">MINTA {"BATAL" if rev["jenis"] == "batal" else "REVISI"}</span></div>'
            f'<table class="rev"><tr><th>Item</th><th class="c">Sebelum</th><th class="c">Sesudah</th></tr>{"".join(rows)}</table>'
            f'<div class="notes"><b>Perubahan:</b> {"; ".join(_esc(n) for n in notes) or "—"}</div>{cat}</div>')


_MEMO_HI: dict = {}


def _html_hari_ini(store, tgl: date, me: str | None, admin: bool) -> dict:
    semua = orders.daftar_pesanan(store, tgl)
    tahun = f"{tgl.day} {logic.BULAN[tgl.month]} {tgl.year}"
    kepala = (f'<div class="judul-sec"><h3>PESANAN HARI INI</h3><span class="tg">{HARI[tgl.weekday()]}, {tahun}</span></div>')
    if not semua:
        return {"kepala": kepala, "kosong": '<div class="kartu"><small>Belum ada yang memesan untuk menu ini.</small></div>'}
    return {"kepala": kepala, "semua": semua, "akhir": _rekap_html(semua, admin),
            "revisi": [(o, _revisi_html(o)) for o in semua if o["revisi"]]}


def _kontrol_tutup(store, tgl: date, admin: bool) -> None:
    tutup = orders.is_tutup(store, tgl)
    if tutup:
        st.html('<div class="kosong-info">🔒 Order ditutup. Pelanggan tidak bisa memesan atau mengubah pesanan.</div>')
    if admin and services.is_penuh():
        if tutup:
            if st.button("Buka kembali order", key="buka_order", width="stretch"):
                orders.set_tutup(store, tgl, False)
                st.rerun()
        elif st.button("Close order", key="tutup_order", type="primary", width="stretch"):
            orders.set_tutup(store, tgl, True)
            st.rerun()


def render_hari_ini(store, tgl: date, me: str | None, admin: bool):
    kunci = (id(store), tgl, store.stamp("Kasbon", "Revisi", "MenuHarian"), me, admin)
    bag = _MEMO_HI.get(kunci)
    if bag is None:
        bag = _html_hari_ini(store, tgl, me, admin)
        if len(_MEMO_HI) > 40:
            _MEMO_HI.clear()
        _MEMO_HI[kunci] = bag
    st.html(bag["kepala"])
    if "kosong" in bag:
        st.html(bag["kosong"])
        _kontrol_tutup(store, tgl, admin)
        return
    punya_saya = bool(me and not admin and any(o["nama"] == me for o in bag["semua"]))
    if punya_saya and orders.bisa_ubah(store, tgl):
        if st.button("Ubah / batalkan pesanan saya", key="ubahku", width="stretch"):
            st.session_state["_open"] = ("pesan", tgl.isoformat(), me, False)
            st.rerun()
    if bag["revisi"]:
        st.html(f'<div class="grp-h">PERMINTAAN REVISI<span>{len(bag["revisi"])} orang</span></div>')
        for no, (o, kartu) in enumerate(bag["revisi"], 1):
            st.html(kartu)
            if admin:
                with st.container(key=f"aksi_rev_{no}"):
                    c1, c2 = st.columns(2)
                    if c1.button("Konfirmasi revisi", key=f"kf_{no}", type="primary", width="stretch"):
                        orders.konfirmasi_revisi(store, tgl, o["nama"])
                        st.rerun()
                    if c2.button("Tolak revisi", key=f"tl_{no}", width="stretch"):
                        orders.tolak_revisi(store, tgl, o["nama"])
                        st.rerun()
    st.html(bag["akhir"])
    _kontrol_tutup(store, tgl, admin)


@st.dialog("Siapa yang memesan")
def dialog_siapa(tgl_iso: str, kunci: str, admin: bool = False):
    store = services.get_store()
    tgl = date.fromisoformat(tgl_iso)
    semua = orders.daftar_pesanan(store, tgl)
    judul = {"paket": "Paket nasi & lauk", "lauk": "Lauk saja (tanpa nasi)", "nasi": "Nasi saja (tanpa lauk)"}.get(kunci, kunci[2:])
    daftar = orders.siapa(semua, kunci)
    st.markdown(f"**{_esc(judul)}** · {sum(q for _, q in daftar)} porsi · {len(daftar)} orang")
    if not daftar:
        st.info("Belum ada yang memesan.")
        return
    belum = [o for o, _ in daftar if o["status"] != "Dibungkus"]
    for no, (o, q) in enumerate(daftar, 1):
        bungkus = o["status"] == "Dibungkus"
        c = st.columns([3, 1.4] if admin else [3, 1.4], vertical_alignment="center", gap="small")
        extra = " · ⏳ revisi" if o["revisi"] else ""
        c[0].markdown(f'**{no}. {_esc(o["nama"])}** ×{q}{extra}' + ("  ✓" if bungkus else ""))
        if admin and services.is_penuh():
            if c[1].button("✓ Dibungkus" if bungkus else "Bungkus", key=f"sq_{kunci}_{no}", width="stretch",
                           type="secondary" if bungkus else "primary"):
                orders.set_dibungkus(store, tgl, o["nama"], not bungkus)
                st.session_state["_open"] = ("siapa", tgl_iso, kunci)
                st.rerun()
        else:
            c[1].caption("dibungkus" if bungkus else "")
    if admin and services.is_penuh() and belum:
        if st.button(f"Bungkus semua ({len(belum)})", key=f"sq_all_{kunci}", width="stretch"):
            for o in belum:
                orders.set_dibungkus(store, tgl, o["nama"], True)
            st.session_state["_open"] = ("siapa", tgl_iso, kunci)
            st.rerun()
    st.caption("Status bungkus berlaku untuk seluruh pesanan orang itu.")


# ===================================================================== Meong (kucing maskot) — obrolan
@st.dialog("Ngobrol sama Meong 🐱")
def dialog_kucing(nama: str | None = None):
    import kucing
    store = services.get_store()
    riwayat = st.session_state.setdefault("_chat", [])
    if not riwayat:
        riwayat.append(("bot", f"Meong! Halo{' ' + nama if nama else ''} 😺 Aku penjaga warung. Mau tanya apa? Pilih di bawah atau ketik sendiri."))

    def tanya(q: str):
        riwayat.append(("user", q))
        riwayat.append(("bot", kucing.jawab(store, nama, q)))

    with st.container(key="chat_atas"):
        with st.form("form_chat", clear_on_submit=True, border=False):
            c = st.columns([3.2, 1.2], vertical_alignment="bottom")
            isi = c[0].text_input("Pertanyaan", placeholder="Ketik pertanyaanmu…", label_visibility="collapsed")
            kirim = c[1].form_submit_button("Kirim", type="primary", width="stretch")
    if kirim and isi.strip():
        tanya(isi.strip())
    with st.container(key="chat_saran"):
        for i in range(0, len(kucing.SARAN), 3):
            cols = st.columns(3)
            for j, s in enumerate(kucing.SARAN[i:i + 3]):
                if cols[j].button(s, key=f"saran_{i + j}", width="stretch"):
                    tanya(s)
    if nama:
        import tanya
        for _, r in tanya.belum_dibaca(store, nama).iterrows():
            riwayat.append(("bot", f"💌 **Jawaban admin** untuk \"{r['pertanyaan']}\":\n\n{r['jawaban']}"))
        tanya.tandai_dibaca(store, nama)
        tgu = tanya.milik(store, nama)
        tgu = tgu[tgu["status"] == "Menunggu"] if len(tgu) else tgu
        if len(tgu):
            st.info(f"⏳ {len(tgu)} pertanyaanmu menunggu jawaban admin. Mohon tunggu ya.")
    for peran, teks in riwayat[-8:][::-1]:
        with st.chat_message("assistant" if peran == "bot" else "user", avatar="🐱" if peran == "bot" else None):
            st.markdown(teks)


def _kolom_jual(kat: str) -> str:
    return {"Nasi": "Nasi", "Ayam Sayur": "Lauk", "Lauk": "Lauk", "Minuman": "Minuman"}.get(kat, "Kerupuk / lain-lain")


@st.dialog("Penjualan hari ini", width="large")
def dialog_penjualan(tgl_iso: str):
    store = services.get_store()
    tgl = date.fromisoformat(tgl_iso)
    kolom = ["Nasi", "Lauk", "Minuman", "Kerupuk / lain-lain"]
    baris, jml = [], {k: 0 for k in kolom}
    total = 0
    for o in orders.daftar_pesanan(store, tgl):
        sel = {k: [] for k in kolom}
        for i in o["items"]:
            k = _kolom_jual(i["kategori"])
            sel[k].append(f'{_esc(i["item"])}' + (f' ×{i["qty"]}' if i["qty"] != 1 else ""))
            jml[k] += i["qty"]
        total += o["total"]
        baris.append((o["nama"], sel, o["total"]))
    st.markdown(f"**{tgl.strftime('%d/%m/%Y')}** · {len(baris)} pelanggan · total **{logic.rupiah(total)}**")
    if not baris:
        st.info("Belum ada pesanan.")
        return
    h = ['<div style="overflow-x:auto"><style>.pj th,.pj td{padding:3px 4px!important;font-size:.68rem!important;white-space:normal!important;min-width:0!important}</style><table class="rekap pj" style="width:100%"><thead><tr><th>Nama</th>'
         + "".join(f"<th>{k}</th>" for k in kolom) + "<th>Total</th></tr></thead><tbody>"]
    for nama, sel, t in sorted(baris, key=lambda b: b[0].lower()):
        h.append(f'<tr><td class="nama" style="position:static">{_esc(nama)}</td>'
                 + "".join(f'<td style="text-align:left;font-size:.78rem">{"<br>".join(sel[k]) or "·"}</td>' for k in kolom)
                 + f'<td class="tot" style="position:static">{logic.rupiah(t)}</td></tr>')
    h.append('<tr class="jual"><td class="nama" style="position:static"><b>TOTAL</b></td>'
             + "".join(f'<td><b>{jml[k]} porsi</b></td>' for k in kolom)
             + f'<td class="tot" style="position:static"><b>{logic.rupiah(total)}</b></td></tr></tbody></table></div>')
    st.html("".join(h))


@st.dialog("Kode 2FA")
def dialog_kunci2fa():
    """Krish berdiri dan meminta kode; kode benar membuka akses penuh admin selama 30 menit."""
    import streamlit.components.v1 as components
    if not services.is_admin():
        st.error("Khusus admin.")
        return
    js = ("<script>(function(){var K=window.parent.__ujKucing;if(!K||!K.pom||!K.AK)return;"
          "K.jalankan('kunci',async function(my){await K.AK.berdiri(K.pom,my);K.pom.say('Masukkan kode 2FA ya 🔐',30000);});})();</script>")
    (st.iframe(js, height=1) if hasattr(st, "iframe") else components.html(js, height=0))
    if services.is_penuh():
        st.success(f"Akses penuh terbuka, sisa {services.sisa_penuh() // 60} menit.")
        if st.button("Kunci lagi", width="stretch"):
            services.kunci_lagi()
            st.rerun()
        return
    st.markdown("🐱 **Masukkan kode 2FA** dari aplikasi authenticator di HP.")
    with st.form("form_kunci2fa", clear_on_submit=True):
        kode = st.text_input("Kode 6 angka", max_chars=8, placeholder="123456")
        ok = st.form_submit_button("Buka kunci", type="primary", width="stretch")
    if ok:
        if (err := services.buka_penuh(kode)):
            st.error(err)
        else:
            st.session_state["_toast"] = "Akses penuh terbuka selama 30 menit 🔓"
            st.rerun()
