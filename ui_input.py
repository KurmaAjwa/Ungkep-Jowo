"""Input pesanan oleh admin (jendela tabel): nama, nasi, lauk, kerupuk, minuman, porsi, harga, simpan.
Hanya untuk admin dengan akses penuh (2FA). Pesanan ditambahkan ke pesanan yang sudah ada (jumlah dijumlahkan)."""
from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

import logic
import orders
import rekap_excel
import services


def _rp(n: float) -> str:
    return logic.rupiah(n) if n else "–"


def tambah_ke_pesanan(store, tgl: date, nama: str, baru: list[dict], oleh: str, buat_akun: bool = False,
                      pakai_aturan: bool = True) -> str | None:
    """Tambahkan item ke pesanan `nama` pada `tgl` (jumlah dijumlahkan, pendamping gratis mengikuti aturan lauk).
    Kembalikan pesan galat atau None."""
    if not baru:
        return "Pilih minimal satu item."
    akun = store.all("Pelanggan")
    if nama.upper() not in {n.upper() for n in akun["nama"]}:
        if not buat_akun:
            return "Nama belum terdaftar. Centang untuk mendaftarkannya."
        store.append("Pelanggan", [{"nama": nama, "sandi_hash": logic.hash_sandi(services.sandi_awal()), "role": "pelanggan",
                                    "aktif": "1", "dibuat": logic.now_wib().isoformat(timespec="seconds")}])
    else:
        nama = next(n for n in akun["nama"] if n.upper() == nama.upper())
    lama_df = orders.pesanan_tgl(store, tgl)
    milik = lama_df[lama_df["pelanggan"] == nama]
    gabung: dict[str, dict] = {r.item: {"kategori": r.kategori, "item": r.item, "qty": int(orders._num(r.qty)),
                                         "harga": orders._num(r.harga), "hpp": orders._num(r.hpp)} for r in milik.itertuples()}
    lunas = {(r.item, int(orders._num(r.qty))) for r in milik.itertuples() if r.status_bayar == "Lunas"}
    # pendamping dari menu harian dicentang langsung di jendela (pakai_aturan=False); selain itu mengikuti aturan lembar Gratis
    for it in orders.tambah_gratis(store, [dict(i) for i in baru], None if pakai_aturan else []):
        if it["item"] in gabung:
            gabung[it["item"]]["qty"] += int(it["qty"])
        else:
            gabung[it["item"]] = dict(it)
    wkt = logic.now_wib().isoformat(timespec="seconds")
    ada = not milik.empty
    ket = str(milik.iloc[0]["catatan"]) if ada else ""
    pemesan = (str(milik.iloc[0]["dipesan_oleh"]) or oleh) if ada else oleh
    dibuat = str(milik.iloc[0]["dibuat"]) if ada else wkt
    rows = [r for r in lama_df.to_dict("records") if r["pelanggan"] != nama]
    baris = orders._baris(tgl, nama, list(gabung.values()), ket, "Disetujui" if ada else "Dipesan", dibuat, pemesan)
    for r in baris:
        if (r["item"], int(r["qty"])) in lunas:
            r["status_bayar"] = "Lunas"
    store.replace_where("Kasbon", "tanggal", tgl.isoformat(), rows + baris)
    orders._tutup_revisi(store, tgl, nama, "Diganti admin")
    orders.simpan_record(store, tgl)
    return None


def _isi(besar: bool) -> None:
    store = services.get_store()
    if not services.is_penuh():
        st.error("Terkunci. Buka dengan 2FA: ketuk Krish dua kali di Beranda.")
        return
    n = st.session_state.setdefault("_inp_n", 0)
    k = lambda x: f"inp{n}_{x}"          # noqa: E731  (kunci widget; n naik setelah simpan = formulir kosong lagi)

    st.html("<style>[role=dialog] [data-testid=stHorizontalBlock]{flex-wrap:nowrap!important;gap:.4rem!important}"
            "[role=dialog] [data-testid=stColumn]{min-width:0!important}"
            "[role=dialog] [data-testid=stRadio] label{font-size:.82rem}</style>")
    c1, c2 = st.columns([3, 2])
    c1.caption("Pesanan akan ditambahkan ke pesanan yang sudah ada.")
    if c2.button("🗕 Perkecil" if besar else "⛶ Perbesar", key=k("ukuran"), width="stretch"):
        st.session_state["_open"] = ("input", not besar)
        st.rerun()

    hari_ini = logic.today_wib()
    a, b = st.columns([3, 2])
    nama_terdaftar = sorted(store.all("Pelanggan").query("role != 'admin' and aktif != '0'")["nama"].tolist(), key=str.lower)
    nama = a.selectbox("Nama", nama_terdaftar, index=None, accept_new_options=True, placeholder="Ketik nama pelanggan…", key=k("nama"))
    tgl = b.date_input("Tanggal", value=hari_ini, min_value=hari_ini - timedelta(days=120), max_value=hari_ini + timedelta(days=60),
                       format="DD/MM/YYYY", key=k("tgl"))
    nama = " ".join(str(nama or "").split())
    baru_nama = bool(nama) and nama.upper() not in {x.upper() for x in nama_terdaftar}
    daftarkan = False
    if baru_nama:
        st.warning(f"Nama “{nama}” belum terdaftar.")
        daftarkan = st.checkbox(f"Daftarkan “{nama}” sebagai pelanggan baru", key=k("daftar"))

    kat = rekap_excel.katalog(store, tgl)
    hari = orders.menu_hari(store, tgl)
    lauk = list(hari[hari["kategori"].isin(orders.LAUK)]["nama"]) if not hari.empty else []     # lauk yang aktif di menu harian
    telur = next((m for m in kat if m.lower() == "telur dadar"), None)                           # selalu tersedia bila pelanggan tak suka ayam
    if telur and telur not in lauk:
        lauk.append(telur)
    if not [m for m in lauk if m != telur]:
        st.caption("Menu harian lauk tanggal ini belum diisi: hanya Telur Dadar dan kerupuk yang tampil.")
    pend = [] if hari.empty else list(hari[hari["kategori"] == "Pendamping"]["nama"])        # lauk pendamping gratis menu harian
    kerupuk = [m for m, v in kat.items() if v["kategori"] == "Lain-lain" and ("krupuk" in m.lower() or "kerupuk" in m.lower())]
    minuman = sorted([m for m, v in kat.items() if v["kategori"] == "Minuman"], key=str.lower)
    # nasi hanya dua jenis tetap: putih (bawaan Rp3.000) dan kuning (Rp5.000); harga dari menu bila ada
    def _nasi(nm: str, harga_awal: int) -> dict:
        v = next((kat[m] for m in kat if m.lower() == nm.lower() and kat[m]["kategori"] == "Nasi"), None)
        return {"kategori": "Nasi", "harga": v["harga"] if v else harga_awal, "hpp": v["hpp"] if v else 0}
    for nm, hg in (("Nasi", 3000), ("Nasi Kuning", 5000)):
        kat.setdefault(nm, _nasi(nm, hg))
    nasi = ["Nasi", "Nasi Kuning"]

    lm = [4, 1.5, 2.2] if besar else [3.4, 1.6, 2.2]
    h = st.columns(lm)
    for col, t in zip(h, ("Pesanan", "Porsi", "Harga")):
        col.markdown(f"**{t}**")

    items: list[dict] = []

    def pendamping(nm: str, kunci: str) -> None:
        item = nm if nm.lower().startswith("free") else f"Free {nm}"
        x = st.columns(lm)
        on = x[0].checkbox(item, value=True, key=k("c_" + kunci))
        q = x[1].number_input("porsi", 1, 50, 1, key=k("q_" + kunci), disabled=not on, label_visibility="collapsed")
        x[2].markdown(f"<div style='text-align:right;padding-top:.45rem'>{'Free' if on else '–'}</div>", unsafe_allow_html=True)
        if on:
            items.append({"kategori": "Lain-lain", "item": item, "qty": int(q), "harga": 0, "hpp": 0})

    def baris(label: str, item: str, kunci: str, awal: bool = False, ekstra=None) -> None:
        x = st.columns(lm)
        on = x[0].checkbox(label, value=awal, key=k("c_" + kunci))
        q = x[1].number_input("porsi", 1, 50, 1, key=k("q_" + kunci), disabled=not on, label_visibility="collapsed")
        sub = int(q * kat[item]["harga"]) if on else 0
        x[2].markdown(f"<div style='text-align:right;padding-top:.45rem'>{_rp(sub)}</div>", unsafe_allow_html=True)
        if on:
            items.append({"kategori": kat[item]["kategori"], "item": item, "qty": int(q), "harga": kat[item]["harga"], "hpp": kat[item]["hpp"]})

    # nasi: otomatis tercentang, hanya satu jenis
    if nasi:
        x = st.columns(lm)
        on = x[0].checkbox("Nasi", value=True, key=k("c_nasi"))
        pil = x[0].radio("Jenis nasi", nasi, horizontal=True, label_visibility="collapsed", key=k("r_nasi"), disabled=not on,
                         format_func=lambda m: f"{'Nasi putih' if m.lower() == 'nasi' else m} ({logic.rupiah(kat[m]['harga'])})")
        q = x[1].number_input("porsi", 1, 50, 1, key=k("q_nasi"), disabled=not on, label_visibility="collapsed")
        x[2].markdown(f"<div style='text-align:right;padding-top:.45rem'>{_rp(int(q * kat[pil]['harga']) if on else 0)}</div>", unsafe_allow_html=True)
        if on:
            items.append({"kategori": "Nasi", "item": pil, "qty": int(q), "harga": kat[pil]["harga"], "hpp": kat[pil]["hpp"]})
    harian_lauk = set(hari[hari["kategori"].isin(orders.LAUK)]["nama"]) if not hari.empty else set()
    for m in lauk:
        baris(m, m, "l_" + m, awal=m in harian_lauk)       # lauk menu harian tercentang otomatis; Telur Dadar tambahan tidak
    for m in pend:
        pendamping(m, "p_" + m)
    for m in kerupuk:
        baris(m, m, "k_" + m)
    if minuman:
        for i in range(2):          # baris minuman ke-2 muncul setelah baris pertama terisi
            if i == 1 and not st.session_state.get(k("minum0")):
                break
            x = st.columns(lm)
            pm = x[0].selectbox(f"Minuman {i + 1}", minuman, index=None, placeholder="Pilih minuman…" if i == 0 else "Minuman kedua (opsional)…",
                                label_visibility="collapsed", key=k(f"minum{i}"),
                                format_func=lambda m: f"{m} ({logic.rupiah(kat[m]['harga'])})")
            q = x[1].number_input("porsi", 1, 50, 1, key=k(f"q_minum{i}"), disabled=pm is None, label_visibility="collapsed")
            x[2].markdown(f"<div style='text-align:right;padding-top:.45rem'>{_rp(int(q * kat[pm]['harga']) if pm else 0)}</div>", unsafe_allow_html=True)
            if pm:
                items.append({"kategori": "Minuman", "item": pm, "qty": int(q), "harga": kat[pm]["harga"], "hpp": kat[pm]["hpp"]})

    total = sum(int(i["qty"] * i["harga"]) for i in items)
    st.markdown(f"<div style='display:flex;justify-content:space-between;border-top:2px solid var(--line,#E9D3B0);margin-top:.4rem;padding-top:.4rem;font-size:1.05rem'>"
                f"<b>Jumlah harga</b><b>{logic.rupiah(total)}</b></div>", unsafe_allow_html=True)
    if nama:
        ada = orders.items_pesanan(store, tgl, nama)
        if ada:
            st.caption("Sudah ada pesanan: " + ", ".join(f"{i['item']} ×{i['qty']}" for i in ada) + ". Item di atas akan **ditambahkan**.")
    boleh = bool(nama) and bool(items) and (not baru_nama or daftarkan)
    if st.button("Simpan", type="primary", width="stretch", disabled=not boleh, key=k("simpan")):
        err = tambah_ke_pesanan(store, tgl, nama, items, services.user() or "admin", buat_akun=daftarkan, pakai_aturan=not pend)
        if err:
            st.error(err)
        else:
            st.session_state["_inp_n"] = n + 1
            st.session_state["_toast"] = f"Pesanan {nama} tersimpan ({logic.rupiah(total)})"
            st.rerun()


@st.dialog("Input pesanan", width="medium")
def dialog_input():
    _isi(False)


@st.dialog("Input pesanan", width="large")
def dialog_input_besar():
    st.html("<style>[role=dialog]{width:96vw!important;max-width:1280px!important}</style>")
    _isi(True)
