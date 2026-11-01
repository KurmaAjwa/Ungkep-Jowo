from __future__ import annotations

from datetime import timedelta

import pandas as pd
import streamlit as st

import base64

import logic
import orders
import payments
import services

store = services.get_store()
_penuh = services.is_penuh()

if not services.is_admin():
    st.error("Halaman ini khusus admin.")
    if st.button("Kembali ke beranda", width="stretch"):
        st.switch_page("pages_app/beranda.py")
    st.stop()

if st.button("← Beranda", key="kembali"):
    st.switch_page("pages_app/beranda.py")
import tema
st.html(tema.hero("ADMIN", "UNGKEP JOWO"))
import streamlit.components.v1 as _components
import kucing as _kucing
(st.iframe if hasattr(st, "iframe") else (lambda h, height: _components.html(h, height=0)))(
    _kucing.js(mode="admin", lengkap=not st.session_state.get("_kucing_ada"), oyen=not st.session_state.get("_oyen_ada")), height=1)
st.session_state["_kucing_ada"] = True
st.session_state["_oyen_ada"] = True

KAT_MASTER = ["Nasi", "Lauk", "Lain-lain"]                 # menu master: makanan saja
KAT_MAKANAN = ["Nasi", "Ayam Sayur", "Lauk", "Lain-lain"]  # urutan tampil (Ayam Sayur = data lama)

import tanya as _tanya
_n_tanya = len(_tanya.menunggu(services.get_store()))
_n_bayar = len(payments.menunggu_semua(store))
_t = st.session_state.pop("_toast", None)
if _t:
    st.toast(_t)
if _n_bayar:
    st.warning(f"🔔 {_n_bayar} bukti bayar menunggu dicek — buka tab **Pembayaran**.")
tab_harian, tab_libur, tab_bayar, tab_master, tab_minuman, tab_sandi, tab_pelanggan, tab_awal, tab_tanya = st.tabs(
    ["Menu harian", "Libur", "Pembayaran", "Menu master", "Minuman", "Sandi", "Pelanggan", "Impor Excel",
     f"Tanya 🐱{' (' + str(_n_tanya) + ')' if _n_tanya else ''}"])


def _angka(x, default=0.0):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    return default if v != v or v in (float("inf"), float("-inf")) else v   # NaN (sel kosong) -> default


def _teks(x) -> str:
    """Teks dari sel tabel; sel kosong (None/NaN) jadi ''."""
    return "" if x is None or (isinstance(x, float) and x != x) else str(x).strip()


# ---------------------------------------------------------------- menu master
with tab_master:
    if not _penuh:
        st.info("🔒 Bagian ini terkunci. Buka dengan 2FA: ketuk **Krish dua kali** di Beranda, masukkan kode 6 angka, lalu kembali ke sini.")
    else:
        st.caption("Makanan saja: nasi, lauk, dan lain-lain (kerupuk). Harga bawaan bisa kamu ubah lagi tiap hari di tab Menu harian. "
                   "Minuman diatur di tab Minuman.")
        master = store.all("Menu")
        master = master[master["kategori"] != "Minuman"] if not master.empty else master
        ed = pd.DataFrame({
            "kategori": master["kategori"].replace("", KAT_MASTER[0]) if not master.empty else pd.Series(dtype=str),
            "nama": master["nama"] if not master.empty else pd.Series(dtype=str),
            "harga": master["harga"].map(_angka) if not master.empty else pd.Series(dtype=float),
            "hpp": master["hpp"].map(_angka) if not master.empty else pd.Series(dtype=float),
            "aktif": (master["aktif"] != "0") if not master.empty else pd.Series(dtype=bool),
        })
        hasil = st.data_editor(
            ed, num_rows="dynamic", width="stretch", hide_index=True, key="ed_master",
            column_config={
                "kategori": st.column_config.SelectboxColumn("Jenis", options=KAT_MASTER + [k for k in sorted(set(ed["kategori"])) if k not in KAT_MASTER], required=True),
                "nama": st.column_config.TextColumn("Nama menu", required=True),
                "harga": st.column_config.NumberColumn("Harga jual", min_value=0, step=500, format="%d"),
                "hpp": st.column_config.NumberColumn("Modal (HPP)", min_value=0, step=500, format="%d"),
                "aktif": st.column_config.CheckboxColumn("Aktif"),
            })
        if (_mm := st.session_state.pop("_master_ok", None)):
            st.success(_mm)
        if st.button("Simpan menu master", type="primary", width="stretch"):
            rows, ada = [], set()
            for i, r in enumerate(hasil.dropna(subset=["nama"]).itertuples(), start=1):
                nm = _teks(r.nama)
                if not nm or nm.lower() in ada:
                    continue
                ada.add(nm.lower())
                rows.append({"id": f"m{i:03d}", "kategori": _teks(r.kategori) or KAT_MASTER[0], "nama": nm,
                             "harga": int(_angka(r.harga)), "hpp": int(_angka(r.hpp)), "aktif": "0" if r.aktif is False or r.aktif == 0 else "1"})
            store.replace_all("Menu", rows)
            st.session_state["_master_ok"] = f"{len(rows)} menu tersimpan. Menu harian yang sudah diunggah tidak ikut berubah: buka tab Menu harian lalu tekan Unggah menu."
            st.rerun()

# ---------------------------------------------------------------- menu harian
with tab_harian:
    if not _penuh:
        st.info("🔒 Bagian ini terkunci. Buka dengan 2FA: ketuk **Krish dua kali** di Beranda, masukkan kode 6 angka, lalu kembali ke sini.")
    else:
        master = store.all("Menu")
        master = master[master["aktif"] != "0"] if not master.empty else master
        if master.empty:
            st.info("Isi dulu daftar menu di tab “Menu master”.")
        else:
            bawaan = logic.tanggal_menu_default()
            tgl = st.date_input("Tanggal menu", value=bawaan, format="DD/MM/YYYY")
            st.caption(f"Diunggah sebelum jam {logic.UNGGAH_BATAS_JAM}:00 WIB = menu hari ini; setelahnya = menu besok. "
                       f"Tanggal bawaan sekarang: {bawaan.strftime('%d/%m/%Y')}.")
            harian = store.all("MenuHarian")
            sudah = harian[harian["tanggal"] == tgl.isoformat()]
            if not sudah.empty:
                st.success(f"Menu {tgl.strftime('%d/%m/%Y')} sudah diunggah ({len(sudah)} item). Kamu bisa mengubahnya lagi.")
            else:
                terakhir = harian.sort_values("tanggal").tail(1)
                sudah = harian[harian["tanggal"] == terakhir.iloc[0]["tanggal"]] if not terakhir.empty else harian.iloc[0:0]
                if not sudah.empty:
                    st.caption(f"Terisi otomatis dari menu {sudah.iloc[0]['tanggal']}. Ubah seperlunya lalu unggah.")
            if not harian[harian["tanggal"] == tgl.isoformat()].empty:
                if orders.pesanan_tgl(store, tgl).empty:
                    if st.button("Hapus menu tanggal ini", key=f"hapus_menu_{tgl}"):
                        store.replace_where("MenuHarian", "tanggal", tgl.isoformat(), [])
                        st.rerun()
                else:
                    st.caption("Menu tidak bisa dihapus karena sudah ada pesanan. Ubah saja lalu unggah ulang.")
            terpilih = {r.nama: r for r in sudah.itertuples()}
            semua_nama = master["nama"].tolist()

            pilihan_harian = []
            for kat in KAT_MAKANAN:
                sub = master[master["kategori"] == kat]
                if sub.empty:
                    continue
                st.markdown(f"**{kat.upper()}**")
                for m in sub.itertuples():
                    t = terpilih.get(m.nama)
                    k = f"{tgl.isoformat()}_{m.id}"
                    with st.container(border=True):
                        pakai = st.toggle(m.nama, value=t is not None, key=f"hp_{k}")
                        if not pakai:
                            continue
                        harga = st.number_input("Harga hari ini (Rp)", min_value=0, step=500, key=f"hh_{k}",
                                                value=int(_angka(t.harga) if t else _angka(m.harga)))
                        batasi = st.toggle("Batasi stok", value=bool(t and _angka(t.batas_stok) == 1), key=f"hb_{k}")
                        stok, alt = 0, ""
                        if batasi:
                            stok = st.number_input("Jumlah stok", min_value=1, step=1, key=f"hs_{k}",
                                                   value=max(1, int(_angka(t.stok, 10))) if t else 10)
                            pilih_alt = [""] + [n for n in semua_nama if n != m.nama]
                            awal = t.alternatif if t and t.alternatif in pilih_alt else ""
                            alt = st.selectbox("Pengganti bila habis (opsional)", pilih_alt, index=pilih_alt.index(awal),
                                               format_func=lambda x: x or "— tidak ada —", key=f"ha_{k}")
                        pilihan_harian.append({
                            "tanggal": tgl.isoformat(), "menu_id": m.id, "kategori": m.kategori, "nama": m.nama,
                            "harga": int(harga), "hpp": int(_angka(t.hpp) if t else _angka(m.hpp)),
                            "batas_stok": 1 if batasi else 0, "stok": int(stok) if batasi else "", "alternatif": alt})
            # minuman: otomatis semua yang dicentang "ready" di tab Minuman
            drinks = store.all("Minuman")
            drinks = drinks[drinks["ready"] == "1"] if not drinks.empty else drinks
            st.markdown("**MINUMAN READY**")
            if drinks.empty:
                st.warning("Belum ada minuman yang dicentang ready. Atur dulu di tab Minuman.")
            else:
                with st.container(border=True):
                    st.caption(f"{len(drinks)} minuman ikut otomatis (ubah di tab Minuman):")
                    st.write(" · ".join(f"{(r.nama + ' ' + r.varian).strip()} ({logic.rupiah(_angka(r.harga))})" for r in drinks.itertuples()))
                for r in drinks.itertuples():
                    nm = (r.nama + " " + r.varian).strip()
                    pilihan_harian.append({"tanggal": tgl.isoformat(), "menu_id": "", "kategori": "Minuman", "nama": nm,
                                           "harga": int(_angka(r.harga)), "hpp": int(_angka(r.hpp)),
                                           "batas_stok": 0, "stok": "", "alternatif": ""})
            st.caption(f"{len(pilihan_harian)} menu dipilih.")
            _ada = harian[harian["tanggal"] == tgl.isoformat()]
            _sekarang = {(r.nama, int(_angka(r.harga))) for r in _ada.itertuples()}
            _baru = {(r["nama"], r["harga"]) for r in pilihan_harian}
            if _sekarang != _baru:
                st.warning("⚠️ Perubahan ini **belum diunggah**. Pelanggan masih melihat menu lama sampai kamu menekan **Unggah menu**."
                           if not _ada.empty else "⚠️ Menu tanggal ini **belum diunggah**. Tekan **Unggah menu** agar muncul di jendela pesan.")
            _ada = harian[harian["tanggal"] == tgl.isoformat()]
            if not _ada.empty:
                _lama = {(r.nama, int(_angka(r.harga))) for r in _ada.itertuples()}
                _baru = {(m["nama"], int(m["harga"])) for m in pilihan_harian}
                if _lama != _baru:
                    st.warning("Ada perubahan yang **belum diunggah**. Pelanggan masih melihat menu lama sampai kamu menekan **Unggah menu**. "
                               "Menu master hanya daftar pilihan, bukan menu yang tampil di jendela pesanan.")
            st.info("Menu yang saat ini dilihat pelanggan pada " + tgl.strftime('%d/%m/%Y') + ": " + (
                ", ".join(f"{r.nama} ({logic.rupiah(_angka(r.harga))})" for r in _ada.itertuples() if r.kategori != "Minuman") or "belum ada menu diunggah"))
            if st.button("Unggah menu", type="primary", width="stretch"):
                if not pilihan_harian:
                    st.error("Pilih minimal satu menu.")
                else:
                    store.replace_where("MenuHarian", "tanggal", tgl.isoformat(), pilihan_harian)
                    st.success(f"Menu {tgl.strftime('%d/%m/%Y')} terunggah ({len(pilihan_harian)} item). "
                               "Tabel Pesanan Hari Ini di beranda ikut berganti.")

# ---------------------------------------------------------------- minuman
with tab_minuman:
    if not _penuh:
        st.info("🔒 Bagian ini terkunci. Buka dengan 2FA: ketuk **Krish dua kali** di Beranda, masukkan kode 6 angka, lalu kembali ke sini.")
    else:
        st.caption("Centang **Ready** untuk minuman/varian yang tersedia. Yang dicentang otomatis masuk menu harian. "
                   "Tambah baris baru di bagian bawah tabel untuk varian lain.")
        dr = store.all("Minuman")
        tabel = pd.DataFrame({
            "ready": (dr["ready"] == "1") if not dr.empty else pd.Series(dtype=bool),
            "nama": dr["nama"] if not dr.empty else pd.Series(dtype=str),
            "varian": dr["varian"] if not dr.empty else pd.Series(dtype=str),
            "harga": dr["harga"].map(_angka) if not dr.empty else pd.Series(dtype=float),
            "hpp": dr["hpp"].map(_angka) if not dr.empty else pd.Series(dtype=float),
        })
        c1, c2 = st.columns(2)
        if c1.button("Semua ready", width="stretch") and not dr.empty:
            store.replace_all("Minuman", [{**r._asdict(), "ready": "1"} for r in dr.itertuples(index=False)])
            st.rerun()
        if c2.button("Kosongkan", width="stretch") and not dr.empty:
            store.replace_all("Minuman", [{**r._asdict(), "ready": "0"} for r in dr.itertuples(index=False)])
            st.rerun()
        hasil_m = st.data_editor(
            tabel, num_rows="dynamic", width="stretch", hide_index=True, key="ed_minuman",
            column_config={
                "ready": st.column_config.CheckboxColumn("Ready"),
                "nama": st.column_config.TextColumn("Minuman", required=True),
                "varian": st.column_config.TextColumn("Varian"),
                "harga": st.column_config.NumberColumn("Harga", min_value=0, step=500, format="%d"),
                "hpp": st.column_config.NumberColumn("Modal", min_value=0, step=500, format="%d"),
            })
        st.caption(f"{int(hasil_m['ready'].sum())} dari {len(hasil_m)} minuman ready.")
        if st.button("Simpan minuman", type="primary", width="stretch"):
            rows, ada = [], set()
            for r in hasil_m.dropna(subset=["nama"]).itertuples():
                nm, vr = _teks(r.nama), _teks(r.varian)
                if not nm or (nm.lower(), vr.lower()) in ada:
                    continue
                ada.add((nm.lower(), vr.lower()))
                rows.append({"nama": nm, "varian": vr, "harga": int(_angka(r.harga)), "hpp": int(_angka(r.hpp)),
                             "ready": "0" if r.ready is False or r.ready == 0 else "1"})
            store.replace_all("Minuman", rows)
            st.success(f"{len(rows)} minuman tersimpan. Unggah ulang menu harian agar perubahan ikut masuk.")
            st.rerun()

# ---------------------------------------------------------------- data awal
with tab_awal:
    if not _penuh:
        st.info("🔒 Bagian ini terkunci. Buka dengan 2FA: ketuk **Krish dua kali** di Beranda, masukkan kode 6 angka, lalu kembali ke sini.")
    else:
        st.markdown("**Unggah rekap pesanan (Excel)**")
        st.caption("Format sama seperti REKAP_PEMBELIAN: sel A1 \"TANGGAL\", baris 2 berisi tanggal, lalu kolom NAMA dan PESANAN. "
                   "Data digabung: yang ada di berkas menimpa, yang hanya ada di aplikasi **tetap dipertahankan**. Tanggal lain tidak tersentuh dan tidak ada yang dobel.")
        import rekap_excel
        from datetime import date as _d
        _hari = logic.now_wib().date()
        c1, c2 = st.columns(2)
        _bln = c1.selectbox("Bulan", list(range(1, 13)), index=_hari.month - 1, key="xl_bln")
        _thn = c2.number_input("Tahun", 2024, 2100, _hari.year, key="xl_thn")
        _fx = st.file_uploader("Berkas Excel (.xlsx)", type=["xlsx"], key="xl_file")
        if _fx is not None:
            try:
                _data, _info = rekap_excel.baca(_fx.getvalue(), int(_bln), int(_thn))
            except Exception as e:
                st.error(f"Berkas tidak bisa dibaca: {e}")
                _data = None
            if _data:
                import menu_excel
                _hm1 = menu_excel.baca(_fx.getvalue()) if menu_excel.ada_menu(_fx.getvalue()) else None
                if _hm1 and not (_hm1["makanan"] or _hm1["minuman"]):
                    _hm1 = None
                if _hm1:
                    st.info(f"Berkas ini juga berisi lembar Menu: {len(_hm1['makanan'])} makanan, {len(_hm1['minuman'])} minuman, "
                            f"{len(_hm1['gratis'])} aturan gratis. Ikut diperbarui saat kamu menekan Impor.")
                _rc0 = rekap_excel.rencana(store, _data, menu=_hm1)
                _akun = [n for n in store.all("Pelanggan")["nama"]]
                _menu = sorted(rekap_excel.katalog(store, max(_data)))
                peta_i, peta_n = {}, {}
                if _rc0["tak_dikenal"]:
                    st.warning("Item berikut tidak dikenali. Pilih padanannya atau biarkan untuk dilewati.")
                    for k, n in _rc0["tak_dikenal"].items():
                        v = st.selectbox(f"{k} ({n}x)", ["(lewati)"] + _menu, key=f"xl_i_{k}")
                        peta_i[k] = None if v == "(lewati)" else v
                if _rc0["nama_baru"]:
                    st.info("Nama berikut belum punya akun. Pilih akun yang sudah ada, atau biarkan untuk dibuatkan akun baru.")
                    for k, n in _rc0["nama_baru"].items():
                        v = st.selectbox(f"{k} ({n} baris)", ["(buat akun baru)"] + _akun, key=f"xl_n_{k}")
                        peta_n[k] = None if v == "(buat akun baru)" else v
                _rc = rekap_excel.rencana(store, _data, peta_i, peta_n, menu=_hm1)
                _rows = rekap_excel.ringkas(store, _rc)
                st.dataframe(pd.DataFrame([{"Tanggal": r["tanggal"].strftime("%d %b %Y"), "Pelanggan": r["pelanggan"],
                                            "Total": logic.rupiah(r["total"]),
                                            "Keterangan": (f"Sudah ada {r['ada_sekarang']} pelanggan → digabung" if r["ada_sekarang"] else "Baru")}
                                           for r in _rows]), hide_index=True, width="stretch")
                _bd = rekap_excel.bandingkan(store, _rc)
                for _b in _bd:
                    _t = _b["tanggal"].strftime("%d %b %Y")
                    if _b["lebih_sedikit"]:
                        st.warning(f"⚠️ {_t}: berkas ini **lebih sedikit** ({_b['item_file']} item) dari data di aplikasi ({_b['item_lama']} item). "
                                   "Yang tidak ada di berkas **tetap dipertahankan**, tidak dihapus.")
                    if _b["baru"] or _b["berubah"] or _b["dipertahankan"]:
                        with st.expander(f"{_t}: {len(_b['baru'])} baru · {len(_b['berubah'])} berubah · {len(_b['dipertahankan'])} dipertahankan · {_b['sama']} sama"):
                            if _b["baru"]:
                                st.markdown("**Baru:** " + ", ".join(_b["baru"]))
                            if _b["berubah"]:
                                st.markdown("**Berubah:**\n" + "\n".join(f"- {n}: {k}" for n, k in _b["berubah"]))
                            if _b["dipertahankan"]:
                                st.markdown("**Dipertahankan (tidak ada di berkas):**\n" + "\n".join(f"- {n}: {k}" for n, k in _b["dipertahankan"]))
                _ganti_penuh = st.checkbox("Mode ganti penuh: hapus yang tidak ada di berkas (jarang dipakai)", key="xl_penuh")
                _ok = st.checkbox("Saya sudah memeriksa ringkasan di atas", key="xl_ok")
                if st.button("Impor (gabung)" if not _ganti_penuh else "Impor & ganti penuh", type="primary", disabled=not _ok, width="stretch", key="xl_go"):
                    if _hm1:
                        menu_excel.terapkan(store, _hm1)
                    h = rekap_excel.impor(store, _rc, True, services.sandi_awal(), ganti_penuh=_ganti_penuh)
                    st.session_state["_xl_ok"] = (f"Selesai: {h['pesanan']} pesanan pada {', '.join(h['tanggal'])}; {h['akun_baru']} akun baru. "
                                                  "Data yang tidak ada di berkas tetap utuh." if not _ganti_penuh else f"Selesai (ganti penuh): {h['pesanan']} pesanan.")
                    st.rerun()
        st.divider()
        st.markdown("**Menu dari Excel**")
        import menu_excel
        st.caption("Lembar “Menu” (makanan + pendamping gratis) dan “Minuman” (harga, jumbo, + susu). Boleh satu berkas dengan rekap pesanan di atas. "
                   "Aturan tidak permanen: ubah angka di Excel, unggah lagi.")
        st.download_button("⬇️ Unduh templat menu (.xlsx)", menu_excel.templat(), "templat_menu_ungkep_jowo.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
        _fm = st.file_uploader("Berkas menu (.xlsx)", type=["xlsx"], key="mx_file")
        if _fm is not None:
            try:
                _hm = menu_excel.baca(_fm.getvalue())
            except Exception as e:
                st.error(f"Berkas tidak bisa dibaca: {e}")
                _hm = None
            if _hm and (_hm["makanan"] or _hm["minuman"]):
                for _c in _hm["catatan"]:
                    st.warning(_c)
                if _hm["makanan"]:
                    st.dataframe(pd.DataFrame([{"Jenis": m["kategori"], "Nama": m["nama"], "Harga": logic.rupiah(m["harga"]),
                                                "Gratis": next((g["pendamping"] for g in _hm["gratis"] if g["lauk"] == m["nama"]), "")}
                                               for m in _hm["makanan"]]), hide_index=True, width="stretch")
                if _hm["minuman"]:
                    st.dataframe(pd.DataFrame([{"Minuman": (m["nama"] + " " + m["varian"]).strip(), "Harga": logic.rupiah(m["harga"]),
                                                "Ready": "ya" if m["ready"] == "1" else "tidak"} for m in _hm["minuman"]]),
                                 hide_index=True, width="stretch", height=260)
                _pasang = st.date_input("Pasang juga sebagai menu harian tanggal (opsional)", value=None, format="DD/MM/YYYY", key="mx_tgl")
                if st.button("Terapkan menu", type="primary", width="stretch", key="mx_go"):
                    _n = menu_excel.terapkan(store, _hm)
                    _msg = f"Menu diterapkan: {_n.get('makanan', 0)} makanan, {_n.get('minuman', 0)} minuman."
                    if _pasang:
                        _rows = menu_excel.menu_harian_rows(store, _pasang.isoformat())
                        store.replace_where("MenuHarian", "tanggal", _pasang.isoformat(), _rows)
                        _msg += f" Menu harian {_pasang.strftime('%d/%m/%Y')} diunggah ({len(_rows)} item)."
                    st.session_state["_xl_ok"] = _msg
                    st.rerun()
            elif _hm is not None:
                st.info("Tidak ada lembar “Menu” atau “Minuman” di berkas ini.")
        if (_m := st.session_state.pop("_xl_ok", None)):
            st.success(_m)

# ---------------------------------------------------------------- sandi
with tab_sandi:
    if not _penuh:
        st.info("🔒 Bagian ini terkunci. Buka dengan 2FA: ketuk **Krish dua kali** di Beranda, masukkan kode 6 angka, lalu kembali ke sini.")
    else:
        minta = store.all("Permintaan")
        minta = minta[(minta["jenis"] == "reset_sandi") & (minta["status"] == "Menunggu")]
        st.subheader("Permintaan reset sandi")
        if minta.empty:
            st.caption("Tidak ada permintaan.")
        for r in minta.itertuples():
            c = st.container(border=True)
            c.markdown(f"**{r.nama}** · {r.waktu.replace('T', ' ')[:16]}")
            if c.button(f"Reset {r.nama} ke sandi awal", key=f"rs_{r.nama}_{r.waktu}", width="stretch"):
                services.reset_sandi(store, r.nama)
                st.rerun()
        st.subheader("Reset manual")
        nama_list = services.daftar_nama(store)
        n = st.selectbox("Pelanggan", nama_list, index=None, placeholder="Ketik nama")
        if st.button("Reset ke sandi awal", disabled=not n, width="stretch"):
            services.reset_sandi(store, n)
            st.success(f"Sandi {n} dikembalikan ke sandi awal.")
        st.caption("Sandi pelanggan disimpan terenkripsi (hash), jadi tidak bisa dibaca siapa pun, termasuk admin. "
                   "Jika lupa, cukup di-reset ke sandi awal.")

        st.subheader("Keamanan admin (verifikasi 2 langkah)")
        if services._rahasia_2fa():
            st.success("2FA admin **aktif**. Hanya admin yang diminta kode saat masuk; pelanggan masuk seperti biasa.")
        else:
            st.caption("Saat aktif, admin harus memasukkan kode 6 angka dari aplikasi authenticator setelah sandi. Pelanggan tidak terpengaruh.")
            _rh = st.session_state.setdefault("_totp_baru", services.totp_baru())
            st.markdown("1. Di HP, buka **Google Authenticator / Authy / Microsoft Authenticator** → tambah akun → **masukkan kunci setelan**.")
            st.code(_rh, language=None)
            st.markdown("2. Uji dulu kodenya:")
            _kd = st.text_input("Kode 6 angka dari aplikasi", max_chars=8, key="totp_uji")
            if _kd:
                if services.totp_cek(_rh, _kd):
                    st.success("Kode cocok. Terakhir, tempel baris ini di **Secrets** Streamlit (di bagian paling atas), simpan, lalu reboot aplikasi:")
                    st.code(f'admin_totp_secret = "{_rh}"', language="toml")
                    st.warning("Simpan juga kunci di atas di tempat aman sebagai cadangan bila HP hilang.")
                else:
                    st.error("Kode belum cocok. Periksa kunci yang dimasukkan dan jam HP.")


# ---------------------------------------------------------------- pelanggan
with tab_pelanggan:
    if not _penuh:
        st.info("🔒 Bagian ini terkunci. Buka dengan 2FA: ketuk **Krish dua kali** di Beranda, masukkan kode 6 angka, lalu kembali ke sini.")
    else:
        df = store.all("Pelanggan")
        df = df[df["role"] != "admin"]
        st.metric("Jumlah pelanggan aktif", int((df["aktif"] != "0").sum()))
        st.subheader("Impor daftar pelanggan lama")
        st.caption("Tempel satu nama per baris (atau unggah CSV dengan kolom “nama”). Semua mendapat sandi awal.")
        teks = st.text_area("Daftar nama", height=140, placeholder="Budi QC\nErry QC\nErix Kama")
        file = st.file_uploader("…atau CSV", type=["csv"])
        nama_baru = [logic.bersih_nama(x) for x in teks.splitlines() if x.strip()]
        if file is not None:
            try:
                nama_baru += [logic.bersih_nama(str(x)) for x in pd.read_csv(file)["nama"].dropna()]
            except Exception:
                st.error("CSV harus punya kolom “nama”.")
        if st.button("Impor", disabled=not nama_baru, type="primary", width="stretch"):
            ada = {n.lower() for n in store.all("Pelanggan")["nama"]}
            tambah, lewati = [], 0
            for nm in dict.fromkeys(nama_baru):
                if nm.lower() in ada or len(nm) < 2:
                    lewati += 1
                    continue
                ada.add(nm.lower())
                tambah.append({"nama": nm, "sandi_hash": logic.hash_sandi(services.sandi_awal()), "role": "pelanggan",
                               "aktif": "1", "dibuat": logic.now_wib().isoformat(timespec="seconds")})
            store.append("Pelanggan", tambah)
            st.success(f"{len(tambah)} pelanggan diimpor, {lewati} dilewati (sudah ada).")
        st.subheader("Daftar")
        st.dataframe(df[["nama", "aktif", "dibuat"]], hide_index=True, width="stretch")


# ---------------------------------------------------------------- pembayaran kasbon
with tab_bayar:
    hari_ini = logic.today_wib()
    p0, _ = logic.periode_untuk(hari_ini)
    opsi = [logic.geser_periode(p0, -i) for i in range(0, 6)]
    lab = [logic.label_periode(a, b) + (" (berjalan)" if i == 0 else "") for i, (a, b) in enumerate(opsi)]
    pil = st.selectbox("Periode kasbon", lab, key="bayar_periode")
    mulai, akhir = opsi[lab.index(pil)]
    kode = logic.kode_periode(mulai)
    akun = store.all("Pelanggan")
    nama_pel = sorted(akun[(akun["role"] != "admin") & (akun["aktif"] != "0")]["nama"].tolist(), key=str.lower)
    baris = []
    for n in nama_pel:
        t = payments.tagihan(store, n, kode)
        if t["total"] > 0:
            baris.append({"Nama": n, "Total": t["total"], "Sisa": t["sisa"], "Status": payments.status_periode(store, n, kode)})
    total_semua = sum(b["Total"] for b in baris)
    total_sisa = sum(b["Sisa"] for b in baris)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total kasbon", logic.rupiah(total_semua))
    c2.metric("Sudah lunas", logic.rupiah(total_semua - total_sisa))
    c3.metric("Belum lunas", logic.rupiah(total_sisa))
    st.caption(f"Jatuh tempo {logic.CUTOFF_HARI} {logic.BULAN[akhir.month]} {akhir.year}. Pelanggan membayar lewat tombol “Bayar sekarang” dan mengirim bukti; "
               "lunas baru berlaku setelah kamu mengonfirmasi.")

    import ui_bayar
    cek = payments.menunggu_semua(store)
    if not _penuh:
        st.caption("🔒 Konfirmasi dan penolakan bukti bayar terkunci (lihat bukti tetap bisa). Buka dengan 2FA: ketuk Krish dua kali di Beranda.")
    st.markdown(f"#### Menunggu konfirmasi bayar{' (' + str(len(cek)) + ')' if len(cek) else ''}")
    if cek.empty:
        st.caption("Belum ada bukti bayar yang perlu dicek.")
    for p in cek.itertuples():
        with st.container(border=True):
            st.markdown(f"**{p.pelanggan}** mengirim bukti bayar")
            st.caption(f"{ui_bayar.waktu_teks(p.waktu)} · Rp {int(float(p.jumlah or 0)):,}".replace(",", ".")
                       + f" · periode {ui_bayar._label_periode(p.periode)}"
                       + (f" · pesanan {ui_bayar._tgl(p.tanggal)}" if p.tanggal else ""))
            a1, a2, a3 = st.columns(3)
            if a1.button("Bukti bayar", key=f"bb_{p.id}", width="stretch"):
                ui_bayar.dialog_bukti(p.id)
            if a2.button("Konfirmasi pelunasan", key=f"kp_{p.id}", type="primary", width="stretch", disabled=not _penuh):
                ui_bayar.dialog_konfirmasi(p.id)
            if a3.button("Tolak", key=f"tl_{p.id}", width="stretch", disabled=not _penuh):
                payments.tolak_bukti(store, p.id)
                st.rerun()

    st.markdown("#### Rekap per pelanggan")
    if baris:
        tbl = pd.DataFrame(baris)
        tbl["Total"] = tbl["Total"].map(logic.rupiah)
        tbl["Sisa"] = tbl["Sisa"].map(logic.rupiah)
        st.dataframe(tbl, hide_index=True, width="stretch")
    else:
        st.info("Belum ada kasbon pada periode ini.")

    st.markdown("#### Tandai lunas (tunai / lainnya)")
    belum = [b["Nama"] for b in baris if b["Sisa"] > 0]
    n_lunas = st.selectbox("Pelanggan", belum, index=None, placeholder="Pilih pelanggan yang belum lunas", key="bayar_pilih")
    if st.button("Konfirmasi lunas", disabled=not n_lunas, key="bayar_tunai", width="stretch"):
        payments.konfirmasi_lunas(store, n_lunas, kode)
        st.rerun()
    sudah = [b["Nama"] for b in baris if b["Sisa"] == 0]
    if sudah:
        n_batal = st.selectbox("Salah tandai? Pilih pelanggan", sudah, index=None, placeholder="Batalkan status lunas", key="bayar_batal")
        if st.button("Batalkan status lunas", disabled=not n_batal, key="bayar_batal_btn", width="stretch"):
            payments.batalkan_lunas(store, n_batal, kode)
            st.rerun()

    riwayat = payments.daftar(store, kode=kode)
    if not riwayat.empty:
        st.markdown("#### Riwayat pembayaran")
        r = riwayat.drop(columns=["bukti", "id", "periode"]).rename(columns={
            "waktu": "Waktu", "pelanggan": "Nama", "jumlah": "Dibayar", "tagihan": "Tagihan", "metode": "Metode",
            "status": "Status", "catatan": "Catatan"})
        st.dataframe(r.iloc[::-1], hide_index=True, width="stretch")


# ---------------------------------------------------------------- libur pemesanan

with tab_libur:
    if not _penuh:
        st.info("🔒 Bagian ini terkunci. Buka dengan 2FA: ketuk **Krish dua kali** di Beranda, masukkan kode 6 angka, lalu kembali ke sini.")
    else:
        st.caption("Pilih tanggal yang libur lalu konfirmasi. Di tanggal itu tombol PESAN tidak muncul dan kolomnya bertanda “libur”.")
        hari_ini_l = logic.today_wib()
        tgl_l = st.date_input("Tanggal libur", value=hari_ini_l, min_value=hari_ini_l, key="libur_tgl", format="DD/MM/YYYY")
        ket_l = st.text_input("Keterangan (opsional)", placeholder="mis. libur nasional, warung tutup", key="libur_ket")
        sudah_libur = orders.libur_map(store)
        if tgl_l in sudah_libur:
            st.info("Tanggal ini sudah libur.")
        elif st.button("Jadikan libur", type="primary", width="stretch", key="libur_btn"):
            st.session_state["_libur_konfirm"] = (tgl_l.isoformat(), ket_l.strip())
        pend = st.session_state.get("_libur_konfirm")
        if pend and pend[0] == tgl_l.isoformat() and tgl_l not in sudah_libur:
            n_psn = len(orders.pesanan_tgl(store, tgl_l)["pelanggan"].unique())
            st.warning(f"Yakin **{logic.tanggal_panjang(tgl_l)}** libur pemesanan?"
                       + (f" Sudah ada {n_psn} pelanggan yang memesan; pesanan mereka tidak dihapus otomatis." if n_psn else ""))
            c1, c2 = st.columns(2)
            if c1.button("Ya, libur", type="primary", width="stretch", key="libur_ya"):
                orders.set_libur(store, tgl_l, pend[1])
                st.session_state.pop("_libur_konfirm", None)
                st.rerun()
            if c2.button("Batal", width="stretch", key="libur_batal"):
                st.session_state.pop("_libur_konfirm", None)
                st.rerun()
        mendatang = {d: k for d, k in sudah_libur.items() if d >= hari_ini_l}
        st.markdown("#### Libur yang akan datang")
        if not mendatang:
            st.caption("Belum ada.")
        for d, k in sorted(mendatang.items()):
            with st.container(border=True):
                st.markdown(f"**{logic.tanggal_panjang(d)}**" + (f" · {k}" if k else ""))
                if st.button("Batalkan libur", key=f"hl_{d}", width="stretch"):
                    orders.hapus_libur(store, d)
                    st.rerun()


# ---------------------------------------------------------------- pertanyaan dari pelanggan (lewat Meong)
with tab_tanya:
    _st = services.get_store()
    _df = _tanya.menunggu(_st)
    if _df.empty:
        st.info("Tidak ada pertanyaan yang menunggu jawaban.")
    for _, _r in _df.iterrows():
        with st.container(border=True):
            st.markdown(f"**{_r['pelanggan'].title()}** · {str(_r['waktu'])[:16].replace('T', ' ')}")
            st.write(_r["pertanyaan"])
            _j = st.text_area("Jawaban", key=f"tj_{_r['id']}", placeholder="Tulis jawaban untuk pelanggan…")
            if st.button("Kirim jawaban", key=f"tk_{_r['id']}", type="primary"):
                if _j.strip():
                    _tanya.jawab(_st, _r["id"], _j)
                    st.rerun()
                else:
                    st.warning("Jawaban masih kosong.")
    _sel = _st.all("Tanya")
    _sel = _sel[_sel["status"] == "Dijawab"] if len(_sel) else _sel
    if len(_sel):
        with st.expander(f"Sudah dijawab ({len(_sel)})"):
            for _, _r in _sel.iloc[::-1].head(20).iterrows():
                st.markdown(f"**{_r['pelanggan'].title()}**: {_r['pertanyaan']}\n\n↳ {_r['jawaban']}")
