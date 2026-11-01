"""Membuat folder hosting statis kucing: docs/kucing/ (kucing.js, krish.webp, oyen.webp, tema.json, index.html).
Jalankan:  python bangun_statis.py   lalu commit folder docs/ ke GitHub dan aktifkan GitHub Pages (Settings > Pages > Branch main, folder /docs)."""
import base64, json, shutil
from pathlib import Path

import kucing

A = Path(__file__).parent / "assets"
OUT = Path(__file__).parent / "docs" / "kucing"
OUT.mkdir(parents=True, exist_ok=True)
meta = json.loads((A / "kucing_meta.json").read_text())
body = (A / "kucing.js").read_text()
bundle = ("// Mesin kucing Krish & Oyen (hosting statis). Dibuat otomatis oleh bangun_statis.py dari assets/kucing.js\n"
          "(function(){window.__ujBoot=function(P,CFG){CFG.css=CFG.css||" + json.dumps(kucing.css()) + ";CFG.meta=CFG.meta||" + json.dumps(meta) + ";\n"
          + body + "\n};})();\n")
(OUT / "kucing.js").write_text(bundle)
for n in ("krish", "oyen"):
    (OUT / f"{n}.webp").write_bytes(base64.b64decode((A / f"{n}.b64").read_text()))
tema = OUT / "tema.json"
if not tema.exists():      # jangan menimpa tema yang sudah diubah
    tema.write_text(json.dumps({
        "aktif": "normal",
        "tema": {
            "normal": {},
            "dingin": {"tint": "rgba(170,205,255,.13)", "css": ":root{--brand:#3E7CB1 !important;--brand-d:#1F3B57 !important;--cream:#EAF4FB !important;--cream2:#D8EAF7 !important;--bg:#EAF4FB !important;--line:#B9D6EC !important;--ink:#1F3B57 !important}",
                       "partikel": {"emoji": ["❄️", "❄️", "🧊"], "jumlah": 14, "durasi": 14}},
            "panas": {"tint": "rgba(255,200,80,.10)", "css": "",
                      "partikel": {"emoji": ["✨", "☀️", "🌴"], "jumlah": 8, "durasi": 16, "arah": "naik"}},
            "hujan": {"tint": "rgba(120,150,190,.12)", "css": "",
                      "partikel": {"emoji": ["💧", "☔"], "jumlah": 14, "durasi": 7}},
        }}, ensure_ascii=False, indent=1))
(OUT / "index.html").write_text("""<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kucing Krish &amp; Oyen</title><body style="margin:0;min-height:100vh;background:#FFF1DB;font-family:system-ui;padding:1rem">
<h3>Uji kucing &amp; tema</h3><p>Tambahkan <code>?musim=dingin</code> / <code>panas</code> / <code>hujan</code> / <code>normal</code>; <code>&amp;admin=1</code> untuk melihat Krish &amp; Oyen.</p>
<script src="kucing.js"></script><script>
var q=new URLSearchParams(location.search);
__ujBoot(window,{mode:q.get('admin')?'admin':'user',sapa:'',nama:'',kabar:'',url:{krish:'krish.webp',oyen:'oyen.webp'},tema:'tema.json',musim:q.get('musim')||''});
</script>""")
print("selesai:", OUT, [p.name + f" {p.stat().st_size//1024}KB" for p in OUT.iterdir()])
