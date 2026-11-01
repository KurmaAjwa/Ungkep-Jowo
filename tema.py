"""Tampilan umum: warung manis (hangat, pastel, imut) — logo, kepala halaman, dan pola latar vektor.
Semua gambar dibuat dari SVG sederhana buatan sendiri (tanpa berkas gambar), jadi ringan dan tajam di layar HP."""
from __future__ import annotations

from functools import lru_cache
from urllib.parse import quote


# ----------------------------------------------------------------- motif (koordinat lokal ± 0..64)
def _wajah(x: float, y: float, s: float = 1.0) -> str:
    return (f'<circle cx="{x-5*s}" cy="{y}" r="{1.7*s}" fill="#4A2412"/><circle cx="{x+5*s}" cy="{y}" r="{1.7*s}" fill="#4A2412"/>'
            f'<path d="M{x-2.2*s} {y+3*s} q{2.2*s} {2.4*s} {4.4*s} 0" stroke="#4A2412" stroke-width="{1.3*s}" fill="none" stroke-linecap="round"/>'
            f'<circle cx="{x-9*s}" cy="{y+3*s}" r="{2.3*s}" fill="#FF9E6B" opacity=".65"/><circle cx="{x+9*s}" cy="{y+3*s}" r="{2.3*s}" fill="#FF9E6B" opacity=".65"/>')


def udang() -> str:
    """Udang goreng krispi: badan melengkung bertepung keemasan, ruas jelas, ekor oranye mengembang, mata imut."""
    return ('<g transform="translate(14.1 38.5) rotate(-20)">'
            '<g fill="#E8501E" stroke="#B93A12" stroke-width="1.3" stroke-linejoin="round">'
            '<ellipse cx="-6" cy="10" rx="3.8" ry="9" transform="rotate(26 -6 10)"/><ellipse cx="6" cy="10" rx="3.8" ry="9" transform="rotate(-26 6 10)"/>'
            '<ellipse cx="0" cy="12" rx="4" ry="10" fill="#F77F35"/></g></g>'
            '<g fill="#C9731A" stroke="#C9731A" stroke-width="1.2"><circle cx="49.9" cy="38.5" r="5.3"/><circle cx="50.6" cy="36.0" r="6.9"/><circle cx="50.9" cy="33.4" r="8.0"/><circle cx="51.0" cy="30.8" r="8.9"/><circle cx="50.6" cy="28.2" r="9.7"/><circle cx="49.9" cy="25.7" r="10.4"/><circle cx="48.9" cy="23.3" r="11.0"/><circle cx="47.6" cy="21.1" r="11.5"/><circle cx="45.9" cy="19.1" r="11.9"/><circle cx="44.0" cy="17.3" r="12.2"/><circle cx="41.9" cy="15.8" r="12.4"/><circle cx="39.6" cy="14.6" r="12.5"/><circle cx="37.1" cy="13.7" r="12.5"/><circle cx="34.6" cy="13.2" r="12.4"/><circle cx="32.0" cy="13.0" r="12.3"/><circle cx="29.4" cy="13.2" r="12.1"/><circle cx="26.9" cy="13.7" r="11.8"/><circle cx="24.4" cy="14.6" r="11.5"/><circle cx="22.1" cy="15.8" r="11.1"/><circle cx="20.0" cy="17.3" r="10.7"/><circle cx="18.1" cy="19.1" r="10.2"/><circle cx="16.4" cy="21.1" r="9.6"/><circle cx="15.1" cy="23.3" r="9.1"/><circle cx="14.1" cy="25.7" r="8.5"/><circle cx="13.4" cy="28.2" r="7.9"/><circle cx="13.0" cy="30.8" r="7.2"/><circle cx="13.1" cy="33.4" r="6.6"/><circle cx="13.4" cy="36.0" r="5.9"/><circle cx="14.1" cy="38.5" r="5.3"/></g>'
            '<g fill="#F4AE38"><circle cx="49.9" cy="38.5" r="4.0"/><circle cx="50.6" cy="36.0" r="5.6"/><circle cx="50.9" cy="33.4" r="6.7"/><circle cx="51.0" cy="30.8" r="7.6"/><circle cx="50.6" cy="28.2" r="8.4"/><circle cx="49.9" cy="25.7" r="9.1"/><circle cx="48.9" cy="23.3" r="9.7"/><circle cx="47.6" cy="21.1" r="10.2"/><circle cx="45.9" cy="19.1" r="10.6"/><circle cx="44.0" cy="17.3" r="10.9"/><circle cx="41.9" cy="15.8" r="11.1"/><circle cx="39.6" cy="14.6" r="11.2"/><circle cx="37.1" cy="13.7" r="11.2"/><circle cx="34.6" cy="13.2" r="11.1"/><circle cx="32.0" cy="13.0" r="11.0"/><circle cx="29.4" cy="13.2" r="10.8"/><circle cx="26.9" cy="13.7" r="10.5"/><circle cx="24.4" cy="14.6" r="10.2"/><circle cx="22.1" cy="15.8" r="9.8"/><circle cx="20.0" cy="17.3" r="9.4"/><circle cx="18.1" cy="19.1" r="8.9"/><circle cx="16.4" cy="21.1" r="8.3"/><circle cx="15.1" cy="23.3" r="7.8"/><circle cx="14.1" cy="25.7" r="7.2"/><circle cx="13.4" cy="28.2" r="6.6"/><circle cx="13.0" cy="30.8" r="5.9"/><circle cx="13.1" cy="33.4" r="5.3"/><circle cx="13.4" cy="36.0" r="4.6"/><circle cx="14.1" cy="38.5" r="4.0"/></g>'
            '<path d="M49.0 25.9 A21 21 0 0 0 34.6 5.7" stroke="#FFE49A" stroke-width="3" fill="none" stroke-linecap="round" opacity=".9"/>'
            '<g stroke="#C9731A" stroke-width="1.5" stroke-linecap="round" opacity=".55"><path d="M52.7 30.7 L58.4 30.4" /><path d="M50.9 22.3 L57.4 19.0" /><path d="M45.6 15.4 L50.8 9.0" /><path d="M37.8 11.3 L40.1 3.1" /><path d="M29.1 10.8 L28.0 2.7" /><path d="M20.9 13.9 L17.1 7.6" /><path d="M14.9 20.0 L9.8 16.4" /><path d="M11.8 27.9 L7.1 27.0" /></g>'
            '<g fill="#B9601A" opacity=".75"><circle cx="54.9" cy="27.4" r="1.3"/><circle cx="52.6" cy="26.6" r="1.3"/><circle cx="44.0" cy="14.1" r="1.3"/><circle cx="44.8" cy="11.0" r="1.3"/><circle cx="42.7" cy="13.2" r="1.3"/><circle cx="26.8" cy="11.0" r="1.3"/><circle cx="25.4" cy="8.6" r="1.3"/><circle cx="25.1" cy="11.8" r="1.3"/><circle cx="14.0" cy="21.1" r="1.3"/><circle cx="11.5" cy="21.5" r="1.3"/><circle cx="12.8" cy="24.7" r="1.3"/><circle cx="12.2" cy="36.3" r="1.3"/></g>'
            '<circle cx="51.9" cy="35.5" r="3.4" fill="#fff"/><circle cx="52.5" cy="35.9" r="2" fill="#5A2A22"/>'
            '<path d="M55.5 38.8 l8 -1 l-4 6 Z" fill="#E8501E" stroke="#B93A12" stroke-width="1"/>')


def ikan() -> str:
    """Ikan goreng keemasan dengan garis bakar."""
    return ('<path d="M50 22 L69 8 Q64 22 69 36 Z" fill="#E58A25" stroke="#B9661A" stroke-width="1.2" stroke-linejoin="round"/>'
            '<path d="M20 9 Q30 -3 42 9 Z" fill="#E58A25" stroke="#B9661A" stroke-width="1.2" stroke-linejoin="round"/>'
            '<ellipse cx="28" cy="22" rx="25" ry="16" fill="#F4A93A" stroke="#C9731A" stroke-width="1.4"/>'
            '<ellipse cx="28" cy="29" rx="19" ry="8" fill="#FFD68A" opacity=".85"/>'
            '<path d="M30 10 q6 12 0 25 M39 11 q6 11 0 23 M48 14 q4 8 0 16" stroke="#C9731A" stroke-width="1.6" fill="none" opacity=".6" stroke-linecap="round"/>'
            '<circle cx="14" cy="18" r="4.2" fill="#fff"/><circle cx="14.6" cy="18.4" r="2.2" fill="#5A2A22"/>'
            '<path d="M7 25 q4 4 8 0" stroke="#5A2A22" stroke-width="1.4" fill="none" stroke-linecap="round"/>'
            '<circle cx="19" cy="27" r="3" fill="#FF9A6B" opacity=".75"/>')


def paha_ayam() -> str:
    return ('<g transform="rotate(-30 30 30)">'
            '<path d="M36 36 L58 54" stroke="#FFF3DC" stroke-width="7" stroke-linecap="round"/>'
            '<circle cx="60" cy="50" r="4.4" fill="#FFF3DC"/><circle cx="55" cy="58" r="4.4" fill="#FFF3DC"/>'
            '<path d="M8 28 C-2 10 22 -4 40 6 C56 15 52 36 34 41 C22 44 13 38 8 28 Z" fill="#E9992B" stroke="#B8661A" stroke-width="1.6"/>'
            '<circle cx="18" cy="14" r="2.2" fill="#B8661A"/><circle cx="32" cy="10" r="2" fill="#B8661A"/><circle cx="40" cy="24" r="2.4" fill="#B8661A"/>'
            '<circle cx="24" cy="28" r="2" fill="#B8661A"/><circle cx="28" cy="20" r="1.6" fill="#FFD27A"/>'
            '<ellipse cx="20" cy="18" rx="7" ry="3.2" fill="#FFE2A0" opacity=".6" transform="rotate(-25 20 18)"/>'
            '</g>')


def telur() -> str:
    return ('<path d="M8 26 C3 11 20 2 32 6 C46 -3 63 10 56 27 C62 41 44 51 32 46 C18 54 2 41 8 26 Z" fill="#FFFDF6" stroke="#F4E4C6" stroke-width="2"/>'
            '<circle cx="32" cy="26" r="12" fill="#FFAE1F"/><circle cx="27.5" cy="21.5" r="3.4" fill="#fff" opacity=".7"/>' + _wajah(32, 28, .8))


def mangkok() -> str:
    return ('<path d="M-4 10 C-2 -4 6 -4 8 4 M62 8 C64 -4 72 -2 70 8" stroke="#FFC9BC" stroke-width="2.2" fill="none" stroke-linecap="round" opacity="0"/>'
            '<path d="M18 -2 c-4 -5 4 -8 0 -13 M32 0 c-4 -5 4 -8 0 -13 M46 -2 c-4 -5 4 -8 0 -13" stroke="#F6B87A" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
            '<path d="M5 26 C5 6 59 6 59 26 Z" fill="#fff" stroke="#F4E4C6" stroke-width="2"/>'
            '<circle cx="20" cy="17" r="1.6" fill="#EBDCC0"/><circle cx="32" cy="12" r="1.6" fill="#EBDCC0"/><circle cx="43" cy="18" r="1.6" fill="#EBDCC0"/>'
            '<path d="M2 26 H62 C62 46 48 58 32 58 C16 58 2 46 2 26 Z" fill="#D9531E"/>'
            '<path d="M5 33 H59" stroke="#FFC48A" stroke-width="3" stroke-linecap="round"/>' + _wajah(32, 43, .85))


def gelas_teh() -> str:
    return ('<path d="M36 40 L44 -6" stroke="#E8452C" stroke-width="4.5" stroke-linecap="round"/>'
            '<path d="M12 8 H52 L47 60 H17 Z" fill="#FFE0A8" stroke="#F0A94A" stroke-width="2"/>'
            '<path d="M13.5 22 H50.5 L47 60 H17 Z" fill="#E8922B" opacity=".85"/>'
            '<rect x="22" y="26" width="10" height="10" rx="2.5" fill="#fff" opacity=".7" transform="rotate(14 27 31)"/>'
            '<rect x="33" y="36" width="9" height="9" rx="2.5" fill="#fff" opacity=".65" transform="rotate(-12 37 40)"/>'
            '<circle cx="52" cy="8" r="9.5" fill="#FFE680" stroke="#F7C948" stroke-width="2"/>'
            '<path d="M52 8 L52 -1.5 M52 8 L60 3 M52 8 L60 13 M52 8 L52 17.5 M52 8 L44 13 M52 8 L44 3" stroke="#F7C948" stroke-width="1.3"/>'
            + _wajah(32, 48, .7))


def cabai() -> str:
    j = "M8 10 C34 6 54 24 56 54"
    return (f'<path d="{j}" fill="none" stroke="#D93A2B" stroke-width="11" stroke-linecap="round"/>'
            f'<path d="M12 5 C32 2 48 14 52 30" fill="none" stroke="#FF8A70" stroke-width="3" stroke-linecap="round" opacity=".7"/>'
            '<path d="M6 8 C0 4 -2 -2 2 -8" stroke="#6FA03C" stroke-width="5" fill="none" stroke-linecap="round"/>')


def tomat() -> str:
    return ('<circle cx="22" cy="26" r="17" fill="#E8512C"/><ellipse cx="15" cy="19" rx="5" ry="3" fill="#fff" opacity=".45" transform="rotate(-30 15 19)"/>'
            '<path d="M22 10 L17 3 L22 6 L27 2 L26 10 L33 11 L25 14 Z" fill="#6FA03C"/>' + _wajah(22, 28, .65))


def bunga() -> str:
    p = "".join(f'<circle cx="{20+11*__import__("math").cos(a*1.2566):.1f}" cy="{20+11*__import__("math").sin(a*1.2566):.1f}" r="8" fill="#FFC857"/>' for a in range(5))
    return p + '<circle cx="20" cy="20" r="6" fill="#E8842B"/>'


def hati() -> str:
    return '<path d="M16 30 C-8 12 6 -6 16 8 C26 -6 40 12 16 30 Z" fill="#F2784B"/><ellipse cx="9" cy="8" rx="3" ry="2" fill="#fff" opacity=".5"/>'


def kilau() -> str:
    return '<path d="M12 0 C13 8 16 11 24 12 C16 13 13 16 12 24 C11 16 8 13 0 12 C8 11 11 8 12 0 Z" fill="#FFC857"/>'


def daun() -> str:
    return '<path d="M2 28 C0 8 16 0 32 2 C34 18 24 32 2 28 Z" fill="#A9C96A"/><path d="M4 26 C12 18 20 12 30 4" stroke="#fff" stroke-width="1.6" fill="none" opacity=".7"/>'


def _g(motif: str, x: float, y: float, rot: float = 0, s: float = 1.0) -> str:
    return f'<g transform="translate({x} {y}) rotate({rot}) scale({s})">{motif}</g>'


# ----------------------------------------------------------------- pola latar & logo
@lru_cache(maxsize=1)
def pola_uri() -> str:
    """Ubin latar 400×400: lauk, minuman, dan hiasan imut berwarna pastel."""
    isi = "".join([
        _g(udang(), 24, 30, -12, .95), _g(ikan(), 190, 24, 8, .9), _g(paha_ayam(), 312, 34, 10, .95),
        _g(telur(), 120, 108, -8, .9), _g(mangkok(), 262, 120, 6, .95), _g(gelas_teh(), 24, 150, -6, .9),
        _g(cabai(), 350, 150, 14, .8), _g(tomat(), 176, 200, 0, .95), _g(bunga(), 98, 205, 0, .9),
        _g(ikan(), 28, 290, -14, .85), _g(telur(), 232, 258, 10, .8), _g(udang(), 318, 262, 16, .9),
        _g(mangkok(), 120, 305, -4, .85), _g(paha_ayam(), 230, 345, -8, .85), _g(gelas_teh(), 340, 350, 8, .8),
        _g(hati(), 90, 22, 0, .9), _g(hati(), 168, 128, 12, .7), _g(hati(), 372, 80, -10, .7),
        _g(kilau(), 70, 100, 0, .9), _g(kilau(), 300, 214, 0, .8), _g(kilau(), 20, 232, 0, .7), _g(kilau(), 190, 292, 0, .8),
        _g(daun(), 368, 224, 20, .8), _g(daun(), 70, 262, -30, .8), _g(bunga(), 362, 304, 0, .75), _g(bunga(), 214, 78, 0, .6),
        _g(hati(), 20, 360, 0, .6), _g(kilau(), 126, 372, 0, .7), _g(daun(), 280, 70, -40, .6),
    ])
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">'
           f'<g opacity=".55">{isi}</g></svg>')
    return "data:image/svg+xml;utf8," + quote(svg, safe="")


@lru_cache(maxsize=1)
def logo_svg() -> str:
    """Logo buatan sendiri: mangkok kuah gurih berisi ayam goreng kriuk, sayur segar, dan nasi hangat. Tanpa tulisan & tanpa latar."""
    defs = ('<defs>'
            '<linearGradient id="mk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F0763A"/><stop offset="1" stop-color="#B9381A"/></linearGradient>'
            '<linearGradient id="rm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFD25E"/><stop offset="1" stop-color="#F0A21E"/></linearGradient>'
            '<radialGradient id="ku" cx=".5" cy=".4" r=".7"><stop offset="0" stop-color="#F28A25"/><stop offset="1" stop-color="#B8401A"/></radialGradient>'
            '<radialGradient id="ay" cx=".4" cy=".3" r=".8"><stop offset="0" stop-color="#FFD76A"/><stop offset=".6" stop-color="#F2A52E"/><stop offset="1" stop-color="#C9701A"/></radialGradient>'
            '<linearGradient id="dn" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8ED36A"/><stop offset="1" stop-color="#3E9A4A"/></linearGradient>'
            '</defs>')
    ayam = ('<g transform="translate(30 50) rotate(160) scale(.8) translate(-24 -22)">'
            '<path d="M30 38 L50 58" stroke="#FFF1D2" stroke-width="7" stroke-linecap="round"/>'
            '<circle cx="53" cy="55" r="4.4" fill="#FFF1D2"/><circle cx="47" cy="62" r="4.4" fill="#FFF1D2"/>'
            '<g fill="#E8991F" stroke="#B9601A" stroke-width="1.3"><circle cx="43.0" cy="20.0" r="4.4"/><circle cx="39.4" cy="28.8" r="4.4"/><circle cx="29.9" cy="34.3" r="4.4"/><circle cx="18.1" cy="34.3" r="4.4"/><circle cx="8.6" cy="28.8" r="4.4"/><circle cx="5.0" cy="20.0" r="4.4"/><circle cx="8.6" cy="11.2" r="4.4"/><circle cx="18.1" cy="5.7" r="4.4"/><circle cx="29.9" cy="5.7" r="4.4"/><circle cx="39.4" cy="11.2" r="4.4"/></g>'
            '<ellipse cx="24" cy="20" rx="20.5" ry="16" fill="url(#ay)"/>'
            '<path d="M8 13 C13 4 26 2 35 6" stroke="#FFF0A8" stroke-width="3.2" fill="none" stroke-linecap="round" opacity=".95"/>'
            '<g fill="#B9601A" opacity=".85"><circle cx="13" cy="20" r="1.9"/><circle cx="22" cy="13" r="1.6"/><circle cx="32" cy="18" r="1.9"/><circle cx="20" cy="27" r="1.7"/>'
            '<circle cx="30" cy="28" r="1.6"/><circle cx="38" cy="23" r="1.4"/></g>'
            '<g fill="#FFF0A8"><circle cx="25" cy="19" r="1.5"/><circle cx="16" cy="26" r="1.2"/><circle cx="36" cy="12" r="1.2"/></g>'
            '</g>')
    daun = ('<path d="M36 56 C22 46 24 28 38 20 C48 30 46 48 36 56 Z" fill="url(#dn)"/><path d="M36 54 C36 42 38 32 38 22" stroke="#D9F5C6" stroke-width="1.8" fill="none"/>'
            '<path d="M46 56 C40 40 48 24 64 22 C68 38 58 52 46 56 Z" fill="url(#dn)"/><path d="M48 54 C52 42 58 34 64 24" stroke="#D9F5C6" stroke-width="1.8" fill="none"/>'
            '<path d="M56 58 C56 48 68 42 80 46 C78 56 68 60 56 58 Z" fill="#4FAE5B"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">' + defs +
            '<path d="M32 22 c-4 -5 4 -8 0 -13 M50 18 c-4 -5 4 -8 0 -13 M68 22 c-4 -5 4 -8 0 -13" stroke="#FFF3D6" stroke-width="3.2" fill="none" stroke-linecap="round"/>'
            '<g transform="translate(2 22) scale(.6)">' + kilau() + '</g>'
            '<g transform="translate(86 14) scale(.5)">' + kilau() + '</g>'
            '<ellipse cx="50" cy="55" rx="42" ry="10" fill="url(#rm)"/>'
            '<ellipse cx="50" cy="55" rx="37" ry="7.5" fill="url(#ku)"/>'
            '<ellipse cx="46" cy="53" rx="22" ry="2.6" fill="#FFB347" opacity=".6"/>'
            + daun +
            '<path d="M62 58 C62 47 87 47 87 58 Z" fill="#FFFBF0" stroke="#F1DDB8" stroke-width="1.5"/>'
            '<circle cx="69" cy="54" r="1.2" fill="#E6D2AA"/><circle cx="76" cy="52" r="1.2" fill="#E6D2AA"/><circle cx="81" cy="56" r="1.2" fill="#E6D2AA"/>'
            + ayam +
            '<path d="M18 58 L30 59 L24 52 Z" fill="#E8403A" stroke="#B82A22" stroke-width="1" stroke-linejoin="round"/>'
            '<circle cx="52" cy="59" r="2.8" fill="#D9381E"/><circle cx="52" cy="59" r="1" fill="#FF9A80"/>'
            '<g fill="#FFD66B"><circle cx="44" cy="58.5" r="1.2"/><circle cx="58" cy="59.5" r="1.1"/><circle cx="36" cy="59" r="1"/><circle cx="48" cy="60" r="1"/></g>'
            '<g fill="#8A3A12"><circle cx="40" cy="57.5" r="1"/><circle cx="56" cy="57.8" r=".9"/><circle cx="62" cy="60" r=".9"/></g>'
            '<path d="M9 54 Q50 72 91 54 C91 80 73 96 50 96 C27 96 9 80 9 54 Z" fill="url(#mk)"/>'
            '<path d="M9 54 Q50 72 91 54 C91 57 90.6 60 90 63 Q50 80 10 63 C9.4 60 9 57 9 54 Z" fill="#FFC94D"/>'
            '<path d="M18 76 q5 -4 10 0 t10 0 t10 0 t10 0 t10 0 t10 0" stroke="#FFD9A8" stroke-width="2" fill="none" opacity=".7" stroke-linecap="round"/>'
            '<path d="M16 66 Q18 78 28 88" stroke="#fff" stroke-width="2.4" fill="none" opacity=".35" stroke-linecap="round"/>'
            + _wajah(50, 85, 1.0) + '</svg>')


@lru_cache(maxsize=1)
def logo_uri() -> str:
    return "data:image/svg+xml;utf8," + quote(logo_svg(), safe="")


@lru_cache(maxsize=1)
def _stiker_svg() -> str:
    isi = "".join([_g(udang(), 6, 4, 10, .55), _g(ikan(), 88, 44, -8, .5), _g(paha_ayam(), 150, 6, 6, .5),
                   _g(hati(), 70, 10, 0, .5), _g(kilau(), 130, 54, 0, .6), _g(kilau(), 2, 56, 0, .5), _g(daun(), 190, 54, 20, .5)])
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 230 90" aria-hidden="true">{isi}</svg>'


@lru_cache(maxsize=8)
def hero(judul: str, sub: str, tagline: str = "") -> str:
    tag = f'<div class="sub2">{tagline}</div>' if tagline else ""
    return (f'<div class="hero"><div class="stiker"><img alt="" src="data:image/svg+xml;utf8,{quote(_stiker_svg(), safe="")}"></div>'
            f'<div class="logo"><img alt="Logo Ungkep Jowo" src="{logo_uri()}"></div>'
            f'<div class="tt"><h1>{judul}</h1><div class="sub">{sub}</div>{tag}</div></div>')


def css() -> str:
    """Gaya tema (dimuat setelah style.css supaya menimpa gaya lama)."""
    return _CSS.replace("%POLA%", pola_uri())


_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@400;600;700;800&display=swap');
:root{--brand:#D9501E;--brand-d:#5E2A12;--amber:#F29A2E;--gold:#F7B733;--sand:#FFE3B8;--sand2:#FFEBCB;
--cream:#FFF1DB;--cream2:#FFE6C2;--line:#F0CC9C;--ink:#4A2410;--muted:#9A6F4E;--bg:#FFF1DB;--peach:#FFE3B8;}
html,body,.stApp,[data-testid="stAppViewContainer"]{font-family:'Nunito',system-ui,sans-serif;color:var(--ink);}
h1,h2,h3,h4,.kartu .besar,.hero h1,.grp-h,.pill-pesan{font-family:'Fredoka','Nunito',sans-serif;}
.stApp{background-color:#FFEFD6;background-image:url("%POLA%");background-size:400px 400px;}
[data-testid="stHeader"]{background:transparent;}
.block-container{background:rgba(255,241,219,.55);border-radius:0 0 28px 28px;}
.block-container{padding-top:5.4rem!important;}
h2,h3{color:var(--brand-d);}

/* kepala halaman: senja hangat + tenda warung */
.hero{position:relative;display:flex;align-items:center;gap:.9rem;text-align:left;padding:1.7rem 1rem 1.05rem;margin:.2rem 0 1.1rem;overflow:hidden;
 background:radial-gradient(circle at 14% 35%,rgba(255,236,170,.9),transparent 48%),linear-gradient(160deg,#FFC24F 0%,#FF9232 45%,#E2551F 100%);
 border-radius:26px;border:3px solid #FFE9BF;box-shadow:0 8px 22px rgba(190,70,20,.35),0 0 0 2px #E8742A;}
.hero::before{content:"";position:absolute;left:0;right:0;top:0;height:.7rem;
 background:repeating-linear-gradient(90deg,#B8381A 0 1.2rem,#FFF1DB 1.2rem 2.4rem);}
.hero::after{content:"";position:absolute;left:0;right:0;top:.7rem;height:.6rem;
 background:radial-gradient(circle at 1.2rem 0,#B8381A .6rem,transparent .62rem) 0 0/2.4rem .6rem repeat-x,
            radial-gradient(circle at 2.4rem 0,#FFF1DB .6rem,transparent .62rem) 0 0/2.4rem .6rem repeat-x;}
.hero .stiker{display:none;}
.hero .stiker img{display:block;width:100%;height:auto;}
.hero .logo{position:relative;flex:0 0 auto;width:5.6rem;margin-top:.5rem;filter:drop-shadow(0 4px 5px rgba(120,40,10,.4));}
.hero .logo img{display:block;width:100%;height:auto;}
.hero .tt{position:relative;flex:1;margin-top:.5rem;}
.hero h1{margin:0;padding:0;font-size:1.65rem;font-weight:700;letter-spacing:.05em;color:#FFF8E6;line-height:1.1;
 text-shadow:0 2px 0 #B8381A,0 3px 10px rgba(120,30,5,.45);-webkit-text-stroke:.5px #B8381A;}
.hero .sub{display:inline-block;margin-top:.45rem;padding:.14rem .8rem;border-radius:999px;background:#FFF1DB;color:var(--brand);
 font-weight:800;font-size:.72rem;letter-spacing:.14em;box-shadow:0 2px 0 #B8381A;}
.hero .sub2{margin-top:.4rem;font-size:.78rem;color:#5E1E08;font-weight:800;}

/* kartu & komponen */
.kartu,.rekap-wrap,.rk-akhir,.psn{background:#FFFAF0;border:2px solid var(--line);border-radius:20px;box-shadow:0 4px 0 rgba(224,160,90,.45);}
.kartu .besar{color:var(--brand);}
.kartu small,.cap,.rk-akhir .cap2{color:var(--muted);}
.judul-sec{flex-wrap:wrap;gap:.1rem .6rem;} .judul-sec h3{white-space:nowrap;font-size:1.05rem!important;}
.judul-sec h3::before{content:"🍗 ";}
.grp-h{background:linear-gradient(135deg,#E2551F,#F29A2E);color:#fff;border-radius:999px;padding:.45rem 1rem;box-shadow:0 3px 0 #B8381A;}
.grp-h span{background:rgba(255,255,255,.3);}
.stButton>button,.stFormSubmitButton>button{border-radius:999px;border:2px solid var(--line);background:#FFFAF0;color:var(--brand-d);font-weight:800;}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"]{background:linear-gradient(180deg,#F58A30,#D9501E);
 border-color:#B13E12;color:#fff;box-shadow:0 3px 0 #B13E12;}
.stButton>button:active{transform:translateY(2px);}
.stTextInput input,div[data-baseweb="select"]>div,.stNumberInput input,[data-baseweb="input"]{background:#FFF7E8!important;border-radius:16px!important;}
.stTextInput input{border:2px solid var(--line)!important;}
.stTabs [data-baseweb="tab-highlight"]{background:var(--brand)!important;}
.stTabs [aria-selected="true"]{color:var(--brand)!important;}
[data-testid="stDialog"]>div,div[role="dialog"]{border-radius:26px!important;background:#FFF8EA!important;}
.stCheckbox [data-baseweb="checkbox"] span:first-child{border-radius:7px;}

/* tabel kasbon */
table.rekap th{background:var(--sand);color:var(--brand-d);}
table.rekap .nama,table.rekap .tot{background:var(--sand2);color:var(--ink);}
table.rekap td,table.rekap th{border-color:var(--line);}
table.rekap tr.jual td{background:#FFE7B0;font-weight:800;border-top:2px solid var(--line);}
table.rekap tr.jual td.klik{cursor:pointer;}
table.rekap td.me{background:#FFEFB8;}
table.rekap th.hari-ini{box-shadow:inset 0 -3px 0 var(--brand);}
.pill-pesan{background:linear-gradient(180deg,#F58A30,#D9501E);box-shadow:0 2px 0 #B13E12;border-radius:999px;}
table.rekap td.lunas-sel{background:#D8F3E2!important;color:#1E7F4B;}
table.rekap td.tot.lunas-tot{background:#BDEBD0!important;color:#17653B;}
/* libur: kolom merah muda, tulisan merah menyala */
table.rekap th.libur{background:#FFC2D1!important;color:#E0002B!important;}
table.rekap td.libur{background:#FFE3EA!important;color:#E0002B!important;font-weight:800;font-style:normal;font-size:.66rem;letter-spacing:.03em;}
.libur-info{background:#FFE3EA;border-color:#F8A9BE;color:#B0102A;}
.rk-akhir tr.tot td{border-top:2px dashed var(--line);}
.rk-akhir td.q{color:var(--brand);}
.psn.s-rev{background:#FFF1C2;border-color:#F2CF6A;}
/* obrolan Meong: baris tetap sejajar di HP */
.st-key-chat_atas [data-testid="stHorizontalBlock"],.st-key-chat_saran [data-testid="stHorizontalBlock"]{flex-direction:row!important;flex-wrap:nowrap!important;gap:.4rem!important;}
.st-key-chat_atas [data-testid="stColumn"],.st-key-chat_saran [data-testid="stColumn"]{min-width:0!important;}
.st-key-chat_saran .stButton>button{min-height:2.3rem;padding:.2rem .3rem;font-size:.74rem;line-height:1.15;}
"""
