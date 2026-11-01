from __future__ import annotations

import html
import json
from datetime import date
from types import SimpleNamespace

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import logic
import orders
import payments
import services
import ui_pesanan as ui

store = services.get_store()

# ikon admin: hanya tampil bila admin yang login
if services.is_admin():
    if st.button("", icon=":material/admin_panel_settings:", key="btn_admin", help="Halaman admin"):
        st.switch_page("pages_app/admin.py")

import tema
st.html(tema.hero("UNGKEP JOWO", "REKAP PEMBELIAN", "Nikmati sekarang, bayar nanti"))

# pop up terima kasih (setelah form pesan ditutup)
if (info := st.session_state.pop("_sukses", None)):
    ui.dialog_sukses(info)


# ------------------------------------------------------------------ login
def tampil_login():
    tab_masuk, tab_daftar = st.tabs(["Masuk", "Daftar pelanggan"])
    with tab_masuk:
        nama_list = services.daftar_nama(store)
        with st.form("form_masuk"):
            nama = st.selectbox("Nama (ketik untuk mencari)", nama_list, index=None, placeholder="Ketik nama, mis. “er”…")
            sandi = st.text_input("Sandi", type="password")
            kirim = st.form_submit_button("Masuk", type="primary", width="stretch")
        if kirim:
            if not nama:
                st.error("Pilih nama dulu.")
            elif (err := services.masuk(store, nama, sandi)):
                st.error(err)
            else:
                st.rerun()
        if st.button("Lupa sandi? Tanya admin", width="stretch"):
            st.session_state["_lupa_buka"] = True
        if st.session_state.get("_lupa_buka"):
            n2 = st.selectbox("Nama kamu", nama_list, index=None, placeholder="Pilih nama", key="lupa_nama_pilih")
            if st.button("Kirim permintaan ke admin", disabled=not n2, width="stretch"):
                services.tanya_admin(store, n2)
                st.session_state["_lupa_buka"] = False
                st.success("Permintaan terkirim. Hubungi admin; setelah dikonfirmasi, sandimu kembali ke sandi awal.")
    with tab_daftar:
        with st.form("form_daftar"):
            baru = st.text_input("Nama kamu", placeholder="mis. Budi QC")
            st.caption("Sandi awal sama dengan pelanggan lain (tanya admin). Bisa kamu ganti setelah masuk.")
            kirim = st.form_submit_button("Daftar", type="primary", width="stretch")
        if kirim:
            if (err := services.daftar_baru(store, baru)):
                st.error(err)
            else:
                st.success("Terdaftar! Silakan masuk di tab “Masuk” dengan sandi awal.")


# ------------------------------------------------------------------ data kasbon
def data_periode(start: date, end: date) -> pd.DataFrame:
    df = store.all("Kasbon")
    if df.empty:
        return df
    df = df[df["status_pesanan"] != "Batal"].copy()
    df["tgl"] = pd.to_datetime(df["tanggal"], format="%Y-%m-%d", errors="coerce").dt.date
    df["subtotal"] = pd.to_numeric(df["subtotal"], errors="coerce").fillna(0)
    return df[(df["tgl"] >= start) & (df["tgl"] <= end)]


def tabel_html(df: pd.DataFrame, nama_semua: list[str], hari: list[date], me: str | None, admin: bool,
               bisa_pesan: set[date], libur: dict[date, str], rev: set[tuple[str, date]], kode: str,
               punyaku: set[tuple[str, date]] = frozenset(),
               bel_h: set = frozenset(), bel_t: set = frozenset(), jual: dict | None = None) -> str:
    """Tabel kasbon. Sel yang boleh diklik diberi data-c (dibaca skrip kecil di bawah)."""
    hari_ini = logic.today_wib()
    pivot = df.groupby(["pelanggan", "tgl"])["subtotal"].sum().to_dict() if not df.empty else {}
    lunas, sisa_orang = {}, {}   # sisa_orang = kasbon yang belum dibayar
    if not df.empty:
        for p, g in df.groupby("pelanggan"):
            lunas[p] = bool((g["status_bayar"] == "Lunas").all())
            sisa_orang[p] = float(g.loc[g["status_bayar"] != "Lunas", "subtotal"].sum())

    lunas_hari = set()
    sisa_hari = {}   # hari yang baru sebagian dibayar -> sisa
    if not df.empty:
        for (p_, t_), g in df.groupby(["pelanggan", "tgl"]):
            ok_ = g["status_bayar"] == "Lunas"
            if ok_.all():
                lunas_hari.add((p_, t_))
            elif ok_.any():
                sisa_hari[(p_, t_)] = float(g.loc[~ok_, "subtotal"].sum())
    urut = sorted(nama_semua, key=lambda n: (n != me, n.lower()))
    bulan_runs: list[tuple[str, int]] = []
    for d in hari:
        lab = f"{logic.BULAN[d.month].upper()} {d.year}"
        if bulan_runs and bulan_runs[-1][0] == lab:
            bulan_runs[-1] = (lab, bulan_runs[-1][1] + 1)
        else:
            bulan_runs.append((lab, 1))
    h = ['<div class="rekap-wrap"><table class="rekap"><thead><tr><th class="nama" rowspan="2">NAMA</th>']
    for lab, n in bulan_runs:
        h.append(f'<th colspan="{n}" style="text-align:left"><span style="position:sticky;left:7.6rem;display:inline-block;padding-left:.2rem">{lab}</span></th>')
    h.append('<th class="tot" rowspan="2">TOTAL</th></tr><tr>')
    for d in hari:
        h.append(f'<th class="{"hari-ini" if d == hari_ini else ""}{" libur" if d in libur else ""}">{d.day}</th>')
    h.append("</tr></thead><tbody>")
    for n in urut:
        mine = n == me
        h.append(f'<tr><td class="nama">{html.escape(n)}</td>')
        total = 0
        for d in hari:
            v = pivot.get((n, d), 0)
            total += v
            boleh = mine or admin or (n, d) in punyaku  # termasuk pesanan teman yang aku masukkan
            klik = boleh and bool(v or d in bisa_pesan)
            pending = (n, d) in rev
            cls = ("me " if mine else "") + ("ada" if v else "kosong") + (" hari-ini" if d == hari_ini else "") \
                + (" klik" if klik else "") + (" rev" if pending else "") + (" libur" if d in libur and not v else "")
            if v and (n, d) in lunas_hari and not pending:
                isi = "LUNAS"
                cls += " lunas-sel"
            elif v and (n, d) in sisa_hari:
                isi = f'<small>sisa</small>{int(sisa_hari[(n, d)]):,}'.replace(",", ".")
                cls += " lunas-sbg"
            elif v:
                isi = ("⏳" if pending else "") + f"{int(v):,}".replace(",", ".")
            elif klik:
                isi = '<span class="pill-pesan">PESAN</span>'
            elif d in libur:
                isi = "libur"
            else:
                isi = "·"
            if admin and (n, d.isoformat()) in bel_h:      # bukti bayar menunggu diperiksa
                isi = '<span class="bel">🔔</span>' + isi
            attr = f' data-c="d|{d.isoformat()}|{html.escape(n, quote=True)}"' if klik else ""
            h.append(f'<td class="{cls}"{attr}>{isi}</td>')
        semua_lunas = bool(total and lunas.get(n))
        tklik = (mine or admin) and total
        attr = f' data-c="t|{kode}|{html.escape(n, quote=True)}"' if tklik else ""
        sisa_n = sisa_orang.get(n, 0.0)
        if semua_lunas:
            isi_tot = '<b>LUNAS</b>'
        elif total and sisa_n < total:      # sebagian sudah dibayar: yang ditampilkan = kasbon yang belum dibayar
            isi_tot = logic.rupiah(sisa_n)
        else:
            isi_tot = logic.rupiah(total) if total else "-"
        if admin and n in bel_t:
            isi_tot = '<span class="bel">🔔</span>' + isi_tot
        h.append(f'<td class="tot{" klik" if tklik else ""}{" lunas-tot" if semua_lunas else ""}"{attr}>{isi_tot}</td></tr>')
    if admin and jual is not None:       # baris penjualan per hari (hanya admin); ketuk untuk rincian per pelanggan
        h.append('<tr class="jual"><td class="nama">PENJUALAN</td>')
        for d in hari:
            v = jual.get(d, 0)
            h.append(f'<td class="jual{" klik" if v else ""}"' + (f' data-c="s|{d.isoformat()}|x"' if v else "") + f'>{f"{int(v):,}".replace(",", ".") if v else "·"}</td>')
        h.append(f'<td class="tot">{logic.rupiah(sum(jual.values()))}</td></tr>')
    h.append("</tbody></table></div>")
    return "".join(h)


# ------------------------------------------------------------------ tampilan utama
me = services.user()
admin = services.is_admin()
if not me:
    tampil_login()
    st.divider()

hari_ini = logic.today_wib()
p_start, _ = logic.periode_untuk(hari_ini)
opsi = [logic.geser_periode(p_start, -i) for i in range(0, 6)]
labels = [logic.label_periode(a, b) + (" (berjalan)" if i == 0 else "") for i, (a, b) in enumerate(opsi)]
pilih = st.selectbox("Periode", labels, index=0, label_visibility="collapsed")
start, end = opsi[labels.index(pilih)]
hari = logic.daftar_hari(start, end)
JEDA = "5s" if admin else "12s"   # seberapa sering bagian "hidup" menyegarkan diri (membaca cache memori, bukan Google)
kode = logic.kode_periode(start)


def turunan(cari_: str = "") -> SimpleNamespace:
    """Semua data turunan untuk tampilan; dipakai sidang utama dan bagian yang menyegarkan diri."""
    df_ = data_periode(start, end)
    buka = orders.tanggal_pesan_pelanggan(store)        # tombol PESAN hanya satu tanggal
    buka_admin = orders.tanggal_pesan_admin(store)
    punya = set()                                       # pesanan teman yang dimasukkan pengguna ini
    if me and not admin and not df_.empty and "dipesan_oleh" in df_:
        punya = {(r.pelanggan, r.tgl) for r in df_[(df_["dipesan_oleh"] == me) & (df_["pelanggan"] != me)].itertuples()}
    rv = store.all("Revisi")
    rev_ = {(r.pelanggan, orders._tgl(r.tanggal)) for r in rv[rv["status"] == "Menunggu"].itertuples()} if not rv.empty else set()
    akun = store.all("Pelanggan")
    nama = sorted(akun[(akun["aktif"] != "0") & (akun["role"] != "admin")]["nama"].tolist(), key=str.lower)
    semua = list(nama)
    if cari_:
        nama = [n for n in nama if cari_.lower() in n.lower() or n == me]
    bel_h, bel_t = (payments.lonceng(store, kode) if admin else (set(), set()))
    return SimpleNamespace(bel_h=bel_h, bel_t=bel_t, df=df_, libur=orders.libur_map(store), buka=buka, buka_admin=buka_admin, punyaku=punya, rev=rev_,
                           nama=nama, semua=semua, sel_kosong=(({buka_admin} if buka_admin else set()) if admin else ({buka} if buka else set())))


D = turunan()
_buka, _buka_admin, punyaku, nama_semua = D.buka, D.buka_admin, D.punyaku, D.semua
tgl_buka = [_buka] if _buka else []


@st.fragment(run_every=JEDA)
def kartu_live():
    df_ = data_periode(start, end)
    total_saya = float(df_.loc[(df_["pelanggan"] == me) & (df_["status_bayar"] != "Lunas"), "subtotal"].sum()) if not df_.empty else 0.0
    st.markdown(
        f'<div class="kartu"><small>Halo, <b>{html.escape(me)}</b> · kasbon yang belum dibayar</small>'
        f'<div class="besar">{logic.rupiah(total_saya)}</div>'
        f'<small>Dibayar tanggal {logic.CUTOFF_HARI} {logic.BULAN[end.month]} {end.year}</small></div>', unsafe_allow_html=True)
    if st.button("Lihat tagihan / Bayar sekarang" if total_saya > 0 else "Lihat riwayat tagihan", key="btn_tagihan", width="stretch"):
        st.session_state["_open"] = ("tagihan", kode, me)
        st.rerun()


if me and not admin:
    kartu_live()
if admin and services._rahasia_2fa():
    st.caption(f"🔓 Akses penuh terbuka · sisa {services.sisa_penuh() // 60} menit" if services.is_penuh()
               else "🔒 Mode terbatas: boleh memesankan, menambah pesanan, konfirmasi revisi, dan membalas chat. Ketuk Krish dua kali untuk akses penuh.")

cari = st.text_input("Cari nama", placeholder="Cari nama di tabel…", label_visibility="collapsed") if len(nama_semua) > 12 else ""

# kotak tersembunyi: skrip kecil mengisinya saat sel tabel diketuk (kuncinya berganti tiap dipakai)
n_klik = st.session_state.setdefault("_n_klik", 0)
klik = st.text_input("sel", key=f"cellsel_{n_klik}", label_visibility="collapsed")
if klik:
    st.session_state["_n_klik"] += 1
    jenis, a1, a2 = (klik.split("#")[0].split("|", 2) + ["", "", ""])[:3]
    _tg_ok = None
    try:
        _tg_ok = date.fromisoformat(a1) if jenis in ("d", "s") else None
    except ValueError:
        pass
    if jenis == "k":      # ketuk kucing: buka obrolan
        st.session_state["_open"] = ("kucing",)
    if jenis == "k2":     # ketuk dua kali: admin membuka kunci 2FA (selain itu sama seperti ketuk biasa)
        st.session_state["_open"] = ("kunci2fa",) if (admin and services._rahasia_2fa() and not services.is_penuh()) else ("kucing",)
    if jenis == "s" and admin and _tg_ok:      # baris penjualan: rincian per pelanggan
        st.session_state["_open"] = ("penjualan", a1)
    if jenis == "r":      # baris rekap pesanan: siapa saja yang memesan
        _tgl_r = orders.tanggal_aktif(store)
        if _tgl_r:
            st.session_state["_open"] = ("siapa", _tgl_r.isoformat(), klik.split("#")[0].split("|", 1)[1])
    if me and jenis in ("d", "t") and (a2 == me or admin or (jenis == "d" and _tg_ok and (a2, _tg_ok) in punyaku)):
        if jenis == "t":
            st.session_state["_open"] = ("tagihan", a1, a2)
        else:
            tg = date.fromisoformat(a1)
            ada = bool(orders.items_pesanan(store, tg, a2))
            if ada:
                st.session_state["_open"] = ("rincian", a1, a2)
            elif admin and tg == _buka_admin:
                st.session_state["_open"] = ("pesan", a1, a2, True)
            elif not admin and tg == _buka:
                st.session_state["_open"] = ("pesan", a1, a2, False)

_MEMO_TBL: dict = {}


@st.fragment(run_every=JEDA)
def tabel_live():
    menit = logic.now_wib().strftime("%Y-%m-%d %H:%M")   # batas jam pesan ikut mempengaruhi tampilan
    kunci = (id(store), store.stamp("Kasbon", "Revisi", "Libur", "MenuHarian", "Pelanggan", "Tutup", "Pembayaran"), me, admin, start, cari, menit)
    isi = _MEMO_TBL.get(kunci)
    if isi is None:
        d = turunan(cari)
        isi = tabel_html(d.df, d.nama, hari, me, admin, d.sel_kosong, d.libur, d.rev, kode, d.punyaku, d.bel_h, d.bel_t,
                        d.df.groupby('tgl')['subtotal'].sum().to_dict() if (admin and not d.df.empty) else ({} if admin else None))
        isi += ('<div class="cap">Ketuk <b>PESAN</b> untuk memesan · ketuk angka untuk rincian dan pembayaran hari itu · '
                'ketuk TOTAL untuk tagihan satu periode · ⏳ menunggu admin · hijau = lunas' + (' · 🔔 bukti bayar menunggu diperiksa' if admin else '') + '</div>')
        lib = {t: k for t, k in d.libur.items() if t >= hari_ini}
        if lib:
            isi += '<div class="kartu libur-info"><b>Libur pemesanan:</b> ' + ", ".join(
                f"{ui.label_tgl(t)}" + (f" ({html.escape(k)})" if k else "") for t, k in sorted(lib.items())) + "</div>"
        if len(_MEMO_TBL) > 60:
            _MEMO_TBL.clear()
        _MEMO_TBL[kunci] = isi
    st.html(isi)


tabel_live()
_INJ = "(function(){\n var last=0;\n var kt=null;function kirim(c){var b=document.querySelector('[class*=st-key-cellsel] input');if(!b)return;\n  var st=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;b.focus({preventScroll:true});\n  st.call(b,c+'#'+Date.now());b.dispatchEvent(new Event('input',{bubbles:true}));b.blur();}\n var px=0,py=0;document.addEventListener('click',function(e){\n  if(kt&&Math.hypot(e.clientX-px,e.clientY-py)<140){clearTimeout(kt);kt=null;kirim('k2|x');return;}\n  var td=e.target.closest&&e.target.closest('[data-c]');if(!td)return;var c=td.getAttribute('data-c');\n  if(c.indexOf('k|')===0){px=e.clientX;py=e.clientY;kt=setTimeout(function(){kt=null;kirim(c);},420);return;}\n  kirim(c);},true);\n document.addEventListener('scroll',function(e){var t=e.target;if(t&&t.classList&&t.classList.contains('rekap-wrap')){last=t.scrollLeft;window.__ujLast=last;}},true);\n new MutationObserver(function(){var w=document.querySelector('.rekap-wrap');if(w&&!w.__uj){w.__uj=1;if(last>0)w.scrollLeft=last;}}).observe(document.body,{childList:true,subtree:true});\n})();"
_js = ("""<script>
(function(){
 var P=window.parent,D=P.document;
 if(!P.__ujKlik4){
  var s=D.createElement('script'); s.textContent=%INJ%; D.head.appendChild(s); P.__ujKlik4=true;
 }
 var n=0,t=setInterval(function(){try{var w=D.querySelector('.rekap-wrap'),h=D.querySelector('th.hari-ini');
 if(w&&h){if(!(P.__ujLast>0))w.scrollLeft=Math.max(0,h.offsetLeft-215);clearInterval(t);}}catch(e){clearInterval(t);} if(++n>20)clearInterval(t);},150);
})();
</script>""").replace("%INJ%", json.dumps(_INJ))
if hasattr(st, "iframe"):          # components.html dihapus di Streamlit baru
    st.iframe(_js, height=1)
else:
    components.html(_js, height=0)

# Meong si kucing: menyapa sekali setelah masuk, lalu berkeliaran di halaman
import kucing
import tanya as _tanya
_sapa = ""
if me and not st.session_state.get("_disapa"):
    st.session_state["_disapa"] = True
    _sapa = f"Selamat datang, {me.title()}! Meong~ 🧡"
_kjs = kucing.js(mode="user", sapa=_sapa, nama=(me or "").title(), kabar=_tanya.kabar(services.get_store(), me),
                 lengkap=not st.session_state.get("_kucing_ada"))
st.session_state["_kucing_ada"] = True
if hasattr(st, "iframe"):
    st.iframe(_kjs, height=1)
else:
    components.html(_kjs, height=0)

# buka jendela yang diminta (dari ketukan sel atau dari tombol di dalam jendela lain)
_toast = st.session_state.pop("_toast", None)
if _toast:
    st.toast(_toast)
if (spec := st.session_state.pop("_open", None)):
    st.session_state.pop("_lihat_bukti", None)          # jendela baru selalu mulai dari rincian, bukan dari gambar bukti
if spec and spec[0] == "siapa":
    ui.dialog_siapa(spec[1], spec[2], admin=admin)
elif spec and spec[0] == "kunci2fa" and admin:
    ui.dialog_kunci2fa()
elif spec and spec[0] == "penjualan" and admin:
    ui.dialog_penjualan(spec[1])
elif spec and spec[0] == "kucing":
    ui.dialog_kucing(me)
elif spec and me:
    jenis = spec[0]
    if jenis == "pesan":
        ui.dialog_pesan(spec[1], spec[2], langsung=bool(spec[3]) and admin)
    elif jenis == "revisi" and admin:
        ui.dialog_revisi(spec[1], spec[2])
    elif jenis == "rincian":
        ui.dialog_rincian(spec[1], spec[2], admin=admin)
    elif jenis == "tagihan":
        ui.dialog_tagihan(spec[1], spec[2], admin=admin)
    elif jenis == "bayar" and (spec[2] == me and not admin):
        ui.dialog_bayar(spec[1], spec[2], spec[3] if len(spec) > 3 else None, spec[4] if len(spec) > 4 else None)

# ---- cadangan: tombol biasa bila sel tabel tidak merespons di perangkatmu
if me and not admin and tgl_buka:
    with st.expander("Tombol cadangan"):
        for d in tgl_buka:
            ada = bool(orders.items_pesanan(store, d, me))
            if st.button(("Lihat / ubah pesanan " if ada else "PESAN ") + ui.label_tgl(d), key=f"pesan_{d}", width="stretch"):
                ui.dialog_pesan(d.isoformat(), me)
if me and not admin and not tgl_buka:
    st.markdown('<div class="kartu"><small>Tombol PESAN aktif setelah admin mengunggah menu berikutnya (biasanya setelah jam 12 siang).</small></div>',
                unsafe_allow_html=True)

# ---- Pesanan Hari Ini (semua orang bisa melihat; kontrol hanya untuk admin)
@st.fragment(run_every=JEDA)
def hari_ini_live():
    tg = orders.tanggal_aktif(store)
    if tg:
        ui.render_hari_ini(store, tg, me, admin)
    else:
        st.markdown('<div class="kartu"><small>Belum ada menu yang dibuka. Pesanan hari ini akan tampil lagi setelah admin mengunggah menu berikutnya.</small></div>', unsafe_allow_html=True)


hari_ini_live()
tgl_aktif = orders.tanggal_aktif(store)
if tgl_aktif and admin:
    with st.expander("Tambah pesanan atas nama pelanggan"):
        n = st.selectbox("Pelanggan", nama_semua, index=None, placeholder="Ketik nama", key="admin_tambah_nama")
        if st.button("Buka form pesan", disabled=not n, width="stretch"):
            ui.dialog_pesan(tgl_aktif.isoformat(), n, langsung=True)

# ---- akun
if me:
    with st.expander("Akun saya" if not admin else "Akun admin"):
        with st.form("form_sandi", clear_on_submit=True):
            lama = st.text_input("Sandi lama", type="password")
            baru = st.text_input("Sandi baru", type="password")
            if st.form_submit_button("Ganti sandi", width="stretch"):
                if (err := services.ganti_sandi(store, me, lama, baru)):
                    st.error(err)
                else:
                    st.success("Sandi diganti.")
        if st.button("Keluar", width="stretch"):
            services.keluar()
            st.rerun()
