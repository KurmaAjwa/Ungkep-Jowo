// Mesin kucing Krish & Oyen (hosting statis). Dibuat otomatis oleh bangun_statis.py dari assets/kucing.js
(function(){window.__ujBoot=function(P,CFG){CFG.css=CFG.css||"\n.uj-cat{position:fixed;left:0;top:0;z-index:90;pointer-events:none;perspective:720px;will-change:transform,opacity;user-select:none;-webkit-user-select:none;}\n.uj-cat.sembunyi{display:none!important;}\n.uj-cat .tilt{position:absolute;inset:0;transform-origin:50% 96%;transform-style:preserve-3d;will-change:transform;}\n.uj-cat .spr{position:absolute;left:0;top:0;background-repeat:no-repeat;pointer-events:none;}\n.uj-cat .bayang{position:absolute;left:50%;bottom:0;width:78px;height:12px;border-radius:50%;transform:translateX(-50%);\n background:radial-gradient(ellipse at center,rgba(90,45,20,.38),rgba(90,45,20,0) 70%);pointer-events:none;}\n.uj-cat .hit{position:absolute;left:50%;bottom:0;width:84px;height:92px;transform:translateX(-50%);pointer-events:auto;cursor:pointer;\n -webkit-tap-highlight-color:transparent;touch-action:manipulation;}\n.uj-gelembung{position:fixed;z-index:95;max-width:220px;background:#FFFAF0;color:#4A2410;border:2px solid #F0CC9C;border-radius:16px;\n padding:.45rem .7rem;font:700 .8rem/1.3 'Nunito',system-ui,sans-serif;box-shadow:0 4px 0 rgba(224,160,90,.5),0 6px 14px rgba(120,60,20,.2);\n opacity:0;transform:translateY(-6px);transition:opacity .25s;pointer-events:none;left:0;top:0;min-width:96px;}\n.uj-gelembung.tampil{opacity:1;}\n.uj-gelembung.menu{pointer-events:auto;}\n.uj-gelembung::after{content:\"\";position:absolute;left:var(--ekor,24px);top:-8px;width:12px;height:12px;background:#FFFAF0;border-left:2px solid #F0CC9C;border-top:2px solid #F0CC9C;transform:rotate(45deg);}\n.uj-gelembung.atas::after{top:auto;bottom:-8px;border:0;border-right:2px solid #F0CC9C;border-bottom:2px solid #F0CC9C;}\n.uj-gelembung .mkn{display:flex;gap:.3rem;margin-top:.4rem;flex-wrap:wrap}\n.uj-gelembung .mkn button{font-size:1.25rem;line-height:1;border:2px solid #F0CC9C;background:#FFF1DB;border-radius:12px;padding:.25rem .4rem;cursor:pointer;transition:transform .12s}\n.uj-gelembung .mkn button:active{transform:scale(.88)}\n.uj-fx{position:fixed;z-index:96;pointer-events:none;left:0;top:0;will-change:transform,opacity;}\n.uj-musim{position:fixed;left:0;top:0;right:0;bottom:0;pointer-events:none;z-index:80;overflow:hidden;}\n.uj-musim span{position:absolute;top:-30px;opacity:.85;will-change:transform;animation:uj-turun linear infinite;}\n.uj-musim.naik span{top:auto;bottom:-30px;animation-name:uj-naik;}\n@keyframes uj-turun{0%{transform:translate3d(0,0,0) rotate(0)}100%{transform:translate3d(var(--dx,0),110vh,0) rotate(200deg)}}\n@keyframes uj-naik{0%{transform:translate3d(0,0,0);opacity:0}15%{opacity:.85}100%{transform:translate3d(var(--dx,0),-110vh,0);opacity:0}}\n@media (prefers-reduced-motion:reduce){.uj-cat,.uj-gelembung,.uj-musim{display:none}}\n";CFG.meta=CFG.meta||{"names": ["walk0", "walk1", "walk2", "walk3", "walk4", "walkF", "jump0", "jump1", "jump2", "jump3", "jump4", "jump5", "sit0", "sit1", "sit2", "sit3", "sit4", "sit5", "lick0", "lick1", "wave0", "wave1", "laugh0", "laugh1", "laugh2", "laugh3", "laugh4", "walk0>walk1:1", "walk0>walk1:2", "walk0>walk1:3", "walk0>walk1:4", "walk1>walk2:1", "walk1>walk2:2", "walk1>walk2:3", "walk1>walk2:4", "walk2>walk3:1", "walk2>walk3:2", "walk2>walk3:3", "walk2>walk3:4", "walk3>walk4:1", "walk3>walk4:2", "walk3>walk4:3", "walk3>walk4:4", "walk4>walk0:1", "walk4>walk0:2", "walk4>walk0:3", "walk4>walk0:4", "jump0>jump1:1", "jump0>jump1:2", "jump1>jump2:1", "jump1>jump2:2", "jump2>jump3:1", "jump2>jump3:2", "jump3>jump4:1", "jump3>jump4:2", "jump4>jump5:1", "jump4>jump5:2", "sit0>sit1:1", "sit0>sit1:2", "sit0>sit1:3", "sit0>sit1:4", "sit1>sit5:1", "sit1>sit5:2", "sit1>sit5:3", "sit1>sit5:4", "sit5>sit0:1", "sit5>sit0:2", "sit5>sit0:3", "sit5>sit0:4", "sit1>sit3:1", "sit1>sit3:2", "sit1>sit3:3", "sit1>sit3:4", "sit3>sit2:1", "sit3>sit2:2", "sit3>sit2:3", "sit3>sit2:4", "sit0>sit2:1", "sit0>sit2:2", "sit0>sit2:3", "sit0>sit2:4", "lick0>lick1:1", "lick0>lick1:2", "lick0>lick1:3", "lick0>lick1:4", "wave0>wave1:1", "wave0>wave1:2", "wave0>wave1:3", "wave0>wave1:4", "laugh1>laugh2:1", "laugh1>laugh2:2", "laugh1>laugh2:3", "laugh1>laugh2:4", "laugh2>laugh3:1", "laugh2>laugh3:2", "laugh2>laugh3:3", "laugh2>laugh3:4", "laugh3>laugh4:1", "laugh3>laugh4:2", "laugh3>laugh4:3", "laugh3>laugh4:4", "wave0>laugh1:1", "wave0>laugh1:2", "wave0>laugh1:3", "wave0>laugh1:4", "sit0>walkF:1", "sit0>walkF:2", "sit0>walkF:3", "sit0>walkF:4", "walkF>walk3:1", "walkF>walk3:2", "walkF>walk3:3", "walkF>walk3:4", "walk0>jump0:1", "walk0>jump0:2", "sit1>jump0:1", "sit1>jump0:2", "sit1>jump0:3", "sit1>jump0:4", "jump5>sit1:1", "jump5>sit1:2", "jump5>sit1:3", "jump5>sit1:4", "sit1>lick0:1", "sit1>lick0:2", "sit1>lick0:3", "sit1>lick0:4", "sit0>wave0:1", "sit0>wave0:2", "sit0>wave0:3", "sit0>wave0:4", "sit0>laugh4:1", "sit0>laugh4:2", "sit0>laugh4:3", "sit0>laugh4:4", "sit5>sit4:1", "sit5>sit4:2", "sit5>sit4:3", "sit5>sit4:4"], "edges": [["walk0", "walk1", [27, 28, 29, 30]], ["walk1", "walk2", [31, 32, 33, 34]], ["walk2", "walk3", [35, 36, 37, 38]], ["walk3", "walk4", [39, 40, 41, 42]], ["walk4", "walk0", [43, 44, 45, 46]], ["jump0", "jump1", [47, 48]], ["jump1", "jump2", [49, 50]], ["jump2", "jump3", [51, 52]], ["jump3", "jump4", [53, 54]], ["jump4", "jump5", [55, 56]], ["sit0", "sit1", [57, 58, 59, 60]], ["sit1", "sit5", [61, 62, 63, 64]], ["sit5", "sit0", [65, 66, 67, 68]], ["sit1", "sit3", [69, 70, 71, 72]], ["sit3", "sit2", [73, 74, 75, 76]], ["sit0", "sit2", [77, 78, 79, 80]], ["lick0", "lick1", [81, 82, 83, 84]], ["wave0", "wave1", [85, 86, 87, 88]], ["laugh1", "laugh2", [89, 90, 91, 92]], ["laugh2", "laugh3", [93, 94, 95, 96]], ["laugh3", "laugh4", [97, 98, 99, 100]], ["wave0", "laugh1", [101, 102, 103, 104]], ["sit0", "walkF", [105, 106, 107, 108]], ["walkF", "walk3", [109, 110, 111, 112]], ["walk0", "jump0", [113, 114]], ["sit1", "jump0", [115, 116, 117, 118]], ["jump5", "sit1", [119, 120, 121, 122]], ["sit1", "lick0", [123, 124, 125, 126]], ["sit0", "wave0", [127, 128, 129, 130]], ["sit0", "laugh4", [131, 132, 133, 134]], ["sit5", "sit4", [135, 136, 137, 138]]], "cw": 240, "ch": 172, "cols": 8, "scale": 1.5};
// Krish & Oyen: kucing gembul. Gambar karakter (atlas pose + frame perantara hasil interpolasi gerak) digerakkan mesin animasi 60 fps:
// gerak berbasis fase langkah, fisika lompatan, pegas (squash & stretch), putaran 3D semu, bayangan, dan lintasan antar-pose.
// Dijalankan di jendela induk. P = window, CFG = {mode, sapa, nama, kabar, css, meta, b64}.
var D = P.document;
if (P.__ujKucing) { P.__ujKucing.mode(CFG.mode, CFG); return; }

function blobUrl(b64) {                       // gambar dikirim sebagai teks base64 lalu diubah jadi URL lokal (tidak bergantung pada berkas statis)
  var bin = P.atob(b64), n = bin.length, u = new Uint8Array(n);
  for (var i = 0; i < n; i++) u[i] = bin.charCodeAt(i);
  return P.URL.createObjectURL(new P.Blob([u], { type: 'image/webp' }));
}
var URLS = {};
if (CFG.url) { URLS.krish = CFG.url.krish; URLS.oyen = CFG.url.oyen; }                      // mode hosting statis: gambar berupa berkas biasa (di-cache browser)
if (CFG.b64 && CFG.b64.krish) URLS.krish = blobUrl(CFG.b64.krish);
if (CFG.b64 && CFG.b64.oyen) URLS.oyen = blobUrl(CFG.b64.oyen);
var M = CFG.meta, SC = M.scale, BW = M.cw / SC, BH = M.ch / SC, COLS = M.cols;
var st = D.createElement('style'); st.id = 'uj-kucing-css'; st.textContent = CFG.css; D.head.appendChild(st);

// ------------------------------------------------------------------ utilitas umum
function rnd(a, b) { return a + Math.random() * (b - a); }
function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
function pick(a) { return a[Math.floor(Math.random() * a.length)]; }
function vw() { return P.innerWidth || 360; }
function vh() { return P.innerHeight || 640; }
var E = {
  io: function (t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; },
  out: function (t) { return 1 - Math.pow(1 - t, 3); },
  inn: function (t) { return t * t * t; },
  lin: function (t) { return t; },
  sine: function (t) { return -(Math.cos(Math.PI * t) - 1) / 2; },
  back: function (t) { var c = 1.7; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); }
};
var K = { sembunyi: false, kenyang: 0, kenyangT: 0, fedLast: 0, lastAct: '', timer: 0, wt: 0, sibuk: '', mod: 'user', cats: [], siap: false };
P.addEventListener('unhandledrejection', function (e) { if (e.reason === 'batal') e.preventDefault(); });
var GT = 0, T = [], nowS = 0, lastT = 0;      // GT: token pembatal global; T: daftar tween

function tw(o, to, dur, ease) {
  return new Promise(function (res) {
    for (var i = 0; i < T.length; i++) if (T[i].o === o) for (var k in to) delete T[i].to[k];
    var tk = { o: o, from: {}, to: to, t0: P.performance.now(), dur: Math.max(1, dur), ease: ease || E.io, res: res };
    for (var k2 in to) tk.from[k2] = o[k2];
    T.push(tk);
  });
}
function chk(my) { if (my !== GT) throw 'batal'; }
function w(ms, my) { return new Promise(function (res) { K.wt = setTimeout(res, ms); }).then(function () { chk(my); }); }
function pz(o, to, ms, e, my) { return tw(o, to, ms, e).then(function () { chk(my); }); }
function par(list, my) { return Promise.all(list).then(function () { chk(my); }); }
function stopAll() {
  GT++; var t = T; T = []; t.forEach(function (x) { x.res(); }); clearTimeout(K.timer); clearTimeout(K.wt);
  K.cats.forEach(function (c) { c.berhenti(); });
}

// ------------------------------------------------------------------ peta pose (graf jalur antar-pose lewat frame perantara)
var IDX = {}; M.names.forEach(function (n, i) { IDX[n] = i; });
var G = {};
M.edges.forEach(function (e) {
  (G[e[0]] = G[e[0]] || {})[e[1]] = e[2];
  (G[e[1]] = G[e[1]] || {})[e[0]] = e[2].slice().reverse();
});
function route(a, b) {
  if (a === b) return [];
  if (!G[a] || !G[b]) return null;
  var q = [[a]], seen = {}; seen[a] = 1;
  while (q.length) {
    var p = q.shift(), l = p[p.length - 1];
    for (var n in G[l]) if (!seen[n]) { var np = p.concat(n); if (n === b) return np; seen[n] = 1; q.push(np); }
  }
  return null;
}
var RING = [];                               // siklus jalan: 5 pose kunci + frame perantara
for (var wi = 0; wi < 5; wi++) { RING.push(IDX['walk' + wi]); RING = RING.concat(G['walk' + wi]['walk' + ((wi + 1) % 5)]); }
var JUMP = [];                               // lintasan terbang: jump0 … jump5
for (var ji = 0; ji < 5; ji++) { JUMP.push(IDX['jump' + ji]); JUMP = JUMP.concat(G['jump' + ji]['jump' + (ji + 1)]); }
JUMP.push(IDX.jump5);
var PEGAS = { k: 190, c: 15 };

// ------------------------------------------------------------------ kelas kucing
function Cat(id, url, nama) {
  var c = this; c.id = id; c.nama = nama; c.seed = rnd(0, 6);
  c.S = { x: 0, y: 0, jy: 0, sq: 0, sqv: 0, yaw: 0, yawv: 0, yawT: 0, roll: 0, rollv: 0, rollT: 0, pit: 0, pitv: 0, pitT: 0, sc: 1, op: 0 };
  c.face = 1; c.pose = 'sit0'; c.cur = -1; c.seq = null; c.cyc = null; c.xf = null; c.walkOn = false; c.ph = 0; c.stride = 100;
  c.vx = 0; c.vy = 0; c.lx = 0; c.ly = 0; c.bt = 0; c.run = false;
  var r = D.createElement('div'); r.className = 'uj-cat'; r.id = 'uj-' + id;
  r.innerHTML = '<div class="bayang"></div><div class="tilt"><div class="spr"></div><div class="spr"></div></div><div class="hit"></div>';
  r.style.width = BW + 'px'; r.style.height = BH + 'px'; D.body.appendChild(r); c.el = r; c.tilt = r.querySelector('.tilt'); c.bay = r.querySelector('.bayang'); c.hit = r.querySelector('.hit');
  c.L = [].slice.call(r.querySelectorAll('.spr')); c.front = 0;
  c.L.forEach(function (l) { l.style.width = BW + 'px'; l.style.height = BH + 'px'; l.style.backgroundImage = 'url("' + url + '")'; l.style.backgroundSize = (COLS * BW) + 'px auto'; });
  c.L[1].style.opacity = 0;
  var g = D.createElement('div'); g.className = 'uj-gelembung'; D.body.appendChild(g); c.gl = g;
  c.show(IDX.sit0, true);
}
Cat.prototype.show = function (i, force) {
  var c = this; if (i === c.cur && !force) return; c.cur = i;
  var l = c.L[c.front]; l.style.backgroundPosition = (-(i % COLS) * BW) + 'px ' + (-Math.floor(i / COLS) * BH) + 'px';
};
Cat.prototype.setFace = function (f) {
  var c = this; c.face = f; c.L.forEach(function (l) { l.style.transform = 'scaleX(' + f + ')'; });
};
Cat.prototype.snapXf = function () {
  var c = this; if (!c.xf) return; var x = c.xf; c.xf = null;
  var back = c.L[1 - c.front]; c.front = 1 - c.front; back.style.opacity = 0; c.L[c.front].style.opacity = 1; c.cur = x.to; if (x.res) x.res();
};
Cat.prototype.cross = function (pose, ms) {      // ganti pose langsung (tanpa lintas-pudar yang membuat gambar dobel), lalu tekan/pantul lewat pegas
  var c = this, i = typeof pose === 'number' ? pose : IDX[pose];
  return new Promise(function (res) {
    c.snapXf(); c.seq = null; c.show(i, true); if (typeof pose === 'string') c.pose = pose;
    c.kick(5); setTimeout(res, Math.min(ms || 120, 150));
  });
};
Cat.prototype.go = function (target, fps) {      // putar frame perantara dari pose sekarang ke pose tujuan
  var c = this; fps = fps || 26;
  return new Promise(function (res) {
    c.snapXf();
    if (c.seq && c.seq.res) c.seq.res();
    var p = route(c.pose, target), fr = [];
    if (c.pose === target) { c.show(IDX[target]); c.seq = null; return res(); }
    if (!p) { c.cross(target, 170).then(res); return; }
    for (var i = 0; i < p.length - 1; i++) { fr = fr.concat(G[p[i]][p[i + 1]]); fr.push(IDX[p[i + 1]]); }
    c.seq = { f: fr, fps: fps, t0: P.performance.now(), res: res, tujuan: target };
  });
};
Cat.prototype.set = function (pose) { var c = this; c.snapXf(); c.seq = null; c.cyc = null; c.pose = pose; c.show(IDX[pose]); };
Cat.prototype.loop = function (poses, fps) { var c = this; c.cyc = poses ? { f: poses.map(function (p) { return typeof p === 'number' ? p : IDX[p]; }), fps: fps || 6, t0: P.performance.now() } : null; };
Cat.prototype.berhenti = function () {
  var c = this; c.walkOn = false; c.cyc = null; c.run = false;
  if (c.seq) { var s = c.seq; c.seq = null; c.pose = s.tujuan; c.show(s.f[s.f.length - 1]); if (s.res) s.res(); }
  c.snapXf(); c.S.yawT = 0; c.S.rollT = 0; c.S.pitT = 0;
};
Cat.prototype.kick = function (v) { this.S.sqv += v; };           // dorongan squash/stretch (positif = menekan)
Cat.prototype.home = function (slot) {
  var s = slot == null ? this.slot : slot; return { x: clamp(vw() - 58 - (s || 0) * 104, 56, 9999), y: 122 };
};
Cat.prototype.maxY = function () { return Math.max(150, vh() - 14); };
Cat.prototype.clampPos = function (x, y) { return { x: clamp(x, 56, Math.max(60, vw() - 56)), y: clamp(y, 122, this.maxY()) }; };

// ------------------------------------------------------------------ gelembung ucapan & efek
Cat.prototype.say = function (t, ms, menu) {
  var c = this, g = c.gl; K.cats.forEach(function (o) { if (o !== c && !menu) o.diam(); }); g.innerHTML = ''; var sp = D.createElement('span'); sp.textContent = t; g.appendChild(sp);
  g.classList.toggle('menu', !!menu);
  if (menu) {
    var box = D.createElement('div'); box.className = 'mkn';
    [['🍗', 'ayam goreng'], ['🍤', 'udang'], ['🐟', 'ikan'], ['🥩', 'daging'], ['🥛', 'susu'], ['🍚', 'nasi']].forEach(function (f) {
      var b = D.createElement('button'); b.type = 'button'; b.textContent = f[0]; b.title = f[1]; b.setAttribute('aria-label', f[1]);
      b.addEventListener('click', function (ev) { ev.stopPropagation(); K.beriMakan(c, f[0], b); }); box.appendChild(b);
    });
    g.appendChild(box);
  }
  g.classList.add('tampil'); c.posGl(); clearTimeout(c.bt);
  if (ms) c.bt = setTimeout(function () { g.classList.remove('tampil'); g.classList.remove('menu'); }, ms);
};
Cat.prototype.diam = function () { this.gl.classList.remove('tampil'); this.gl.classList.remove('menu'); clearTimeout(this.bt); };
Cat.prototype.posGl = function () {
  var c = this, g = c.gl, gw = g.offsetWidth, gh = g.offsetHeight, S = c.S, W = vw();
  var topY = S.y + S.jy - 112, below = topY < 70, cx = S.x;
  var gx = clamp(cx - gw / 2, 6, W - gw - 6);
  var gy = below ? S.y + S.jy + 8 : topY - gh + 6;
  g.style.transform = 'translate3d(' + gx.toFixed(1) + 'px,' + Math.max(4, gy).toFixed(1) + 'px,0)';
  g.classList.toggle('atas', !below);
  g.style.setProperty('--ekor', clamp(cx - gx - 6, 12, gw - 24) + 'px');
};
function fx(emoji, x, y, dx, dy, ms, size) {
  var n = D.createElement('div'); n.className = 'uj-fx'; n.textContent = emoji; n.style.fontSize = (size || 18) + 'px'; D.body.appendChild(n);
  var t0 = P.performance.now();
  (function f(now) {
    var p = Math.min(1, (now - t0) / ms);
    n.style.transform = 'translate3d(' + (x + dx * p) + 'px,' + (y + dy * p - Math.sin(p * Math.PI) * 14) + 'px,0) scale(' + (.6 + Math.sin(p * Math.PI) * .7) + ')';
    n.style.opacity = p < .7 ? 1 : (1 - p) / .3;
    if (p < 1) P.requestAnimationFrame(f); else n.remove();
  })(t0);
}
Cat.prototype.hati = function (n, e) {
  var c = this;
  for (var i = 0; i < (n || 3); i++) (function (i) { setTimeout(function () { fx(e || '❤️', c.S.x - 10 + rnd(0, 36), c.S.y + c.S.jy - 96, rnd(-14, 14), -rnd(36, 60), 1200, 16 + rnd(0, 6)); }, i * 180); })(i);
};

// ------------------------------------------------------------------ render per frame
function pegas(S, k, tgt, dt) {
  var v = S[k + 'v'] || 0; v += ((tgt - S[k]) * PEGAS.k - v * PEGAS.c) * dt; S[k] += v * dt; S[k + 'v'] = v;
}
Cat.prototype.step = function (dt, now) {
  var c = this, S = c.S, t = nowS;
  if (dt > 0) {
    c.vx = c.vx * .75 + ((S.x - c.lx) / dt) * .25; c.vy = c.vy * .75 + ((S.y - c.ly) / dt) * .25;
  }
  c.lx = S.x; c.ly = S.y;
  var spd = Math.sqrt(c.vx * c.vx + c.vy * c.vy);
  // --- pilih frame
  if (!c.xf && c.L[1 - c.front].style.opacity !== '0') { c.L[1 - c.front].style.opacity = 0; }      // cegah dua lapis gambar tumpuk
  if (!c.xf && c.L[c.front].style.opacity !== '1' && c.L[c.front].style.opacity !== '') c.L[c.front].style.opacity = 1;
  if (c.xf) {
    var p = Math.min(1, (now - c.xf.t0) / c.xf.ms), b = c.L[1 - c.front]; b.style.opacity = E.sine(p).toFixed(3);
    if (p >= 1) c.snapXf();
  } else if (c.fly) {
    var fp = clamp((now - c.fly.t0) / c.fly.ms, 0, 1); c.show(JUMP[Math.min(JUMP.length - 1, Math.floor(fp * JUMP.length))]);
  } else if (c.seq) {
    var s = c.seq, i = Math.floor((now - s.t0) / 1000 * s.fps);
    if (i >= s.f.length) { c.pose = s.tujuan; c.show(s.f[s.f.length - 1]); c.seq = null; if (s.res) s.res(); }
    else c.show(s.f[i]);
  } else if (c.cyc) {
    c.show(c.cyc.f[Math.floor((now - c.cyc.t0) / 1000 * c.cyc.fps) % c.cyc.f.length]);
  } else if (c.walkOn) {
    c.ph += (spd / c.stride) * dt; var a = Math.floor(((c.ph % 1) + 1) % 1 * RING.length); c.show(RING[a]);
  }
  // --- target 3D
  var arah = c.vx >= 0 ? 1 : -1, moving = c.walkOn && spd > 8, air = Math.abs(S.jy) > 3;
  var lean = (moving || air) ? clamp(c.vx / 140, -1, 1) : 0;
  S.rollT = (c.rollB || 0) + lean * 5;
  S.yawT = (c.yawB || 0) + (moving ? -arah * Math.min(1, spd / 80) * 13 : 0) + Math.sin(t * .7 + c.seed) * (moving ? 1.5 : 3.5);
  S.pitT = (c.pitB || 0) + (moving ? 1.5 : 0) + (air ? clamp(-c.vjy / 160, -1, 1) * -6 : 0);
  pegas(S, 'yaw', S.yawT, dt); pegas(S, 'roll', S.rollT, dt); pegas(S, 'pit', S.pitT, dt); pegas(S, 'sq', c.sqT || 0, dt);
  var vjy = (S.jy - (c.ljy || 0)) / Math.max(dt, 1e-3); c.vjy = (c.vjy || 0) * .7 + vjy * .3; c.ljy = S.jy;
  var stretch = air ? -clamp(Math.abs(c.vjy) / 1100, 0, .1) : 0;
  var ds = (.9 + clamp((S.y - 122) / Math.max(200, c.maxY() - 122), 0, 1) * .17) * S.sc;
  var br = (!moving && !c.seq && !c.cyc && !air) ? Math.sin(t * 2.1 + c.seed) * .011 : 0;
  var sq = S.sq + stretch, sx = (1 + sq * .5 - br * .5) * ds, sy = (1 - sq + br) * ds;
  var bob = moving ? -Math.abs(Math.sin(c.ph * Math.PI * 2)) * 2.6 * Math.min(1, spd / 90) : 0;
  c.el.style.opacity = S.op;
  c.el.style.transform = 'translate3d(' + (S.x - BW / 2).toFixed(2) + 'px,' + (S.y + S.jy - BH + bob).toFixed(2) + 'px,0)';
  c.el.style.zIndex = 90 + Math.min(9, Math.floor(S.y / 90));
  c.tilt.style.transform = 'rotateX(' + S.pit.toFixed(2) + 'deg) rotateY(' + S.yaw.toFixed(2) + 'deg) rotateZ(' + S.roll.toFixed(2) + 'deg) scale(' + sx.toFixed(4) + ',' + sy.toFixed(4) + ')';
  var hh = clamp(-S.jy / 100, 0, 1);
  c.bay.style.transform = 'translateX(-50%) scale(' + ((1 - hh * .5) * ds).toFixed(3) + ',' + (1 - hh * .4).toFixed(3) + ')';
  c.bay.style.opacity = (.9 - hh * .55).toFixed(3);
  if (c.gl.classList.contains('tampil')) c.posGl();
};
var lastDraw = 0;
function frame(now) {
  P.requestAnimationFrame(frame);                  // jadwalkan dulu: galat sekali tidak boleh mematikan animasi selamanya
  K.beat = Date.now();
  try {
    var dt = Math.min(.05, (now - (lastT || now)) / 1000); lastT = now; nowS = now / 1000;
    for (var i = T.length - 1; i >= 0; i--) {
      var tk = T[i], p = Math.min(1, (now - tk.t0) / tk.dur), e = tk.ease(p);
      for (var k in tk.to) tk.o[k] = tk.from[k] + (tk.to[k] - tk.from[k]) * e;
      if (p >= 1) { T.splice(i, 1); tk.res(); }
    }
    if (K.sembunyi || D.hidden) return;
    var diam = !T.length && K.cats.every(function (c) { return !c.walkOn && !c.seq && !c.cyc && !c.xf && !c.fly; });
    if (diam && now - lastDraw < 45) return;       // saat diam cukup ±22 fps (hemat baterai/CPU)
    lastDraw = now;
    K.cats.forEach(function (c) { if (c.aktif) { try { c.step(dt, now); } catch (er) { console.warn(er); } } });
  } catch (er2) { console.warn(er2); }
}

// ------------------------------------------------------------------ gerak dasar: balik badan, jalan, lompat
function gp(c, pose, fps, my) { return c.go(pose, fps).then(function () { chk(my); }); }
function isWalk(c) { return /^walk/.test(c.pose); }
async function hadap(c, dir, my) {                  // balik badan lewat pose menghadap depan (tidak gepeng)
  if (c.face === dir) return;
  c.yawB = -dir * 26;
  if (isWalk(c)) { await gp(c, 'walkF', 36, my); c.setFace(dir); await gp(c, 'walk3', 36, my); }
  else if (/^(sit[1-5]|lick|jump)/.test(c.pose)) { await gp(c, 'sit0', 36, my); c.setFace(dir); }
  else c.setFace(dir);
  c.yawB = 0;
}
function kunciWalk(c) {                              // pose kunci terdekat dari posisi siklus jalan
  var a = Math.floor(((c.ph % 1) + 1) % 1 * RING.length), k = Math.round(a / 5) % 5; return k;
}
async function jalanKe(c, x, y, my, spd) {
  spd = spd || 85; var S = c.S, t = c.clampPos(x, y);
  var dx = t.x - S.x, dist = Math.hypot(dx, t.y - S.y); if (dist < 5) return;
  if (Math.abs(dx) > 8) await hadap(c, dx > 0 ? 1 : -1, my);
  c.stride = spd > 150 ? 150 : 104;
  var dur = Math.max(450, dist / spd * 1000 * 1.22);
  var mulai = isWalk(c) ? Promise.resolve() : c.go('walk3', 38);
  var gerak = tw(S, { x: t.x, y: t.y }, dur, E.sine);
  await mulai; chk(my);
  c.pose = 'walk3'; c.ph = IDX.walk3 && RING.indexOf(IDX.walk3) / RING.length; c.walkOn = true;
  await gerak; chk(my);
  c.walkOn = false; var k = kunciWalk(c); c.pose = 'walk' + k; c.show(IDX['walk' + k]);
  await gp(c, 'sit0', 32, my);
}
async function lompatKe(c, x, y, tinggi, ms, my) {
  var S = c.S, t = c.clampPos(x, y); tinggi = tinggi || 50; ms = ms || 650;
  var dir = t.x > S.x + 4 ? 1 : (t.x < S.x - 4 ? -1 : c.face);
  if (dir !== c.face) await hadap(c, dir, my);
  c.sqT = .13; await gp(c, 'jump0', 46, my); await w(40, my);          // jongkok (antisipasi)
  c.sqT = 0; c.kick(-7);
  c.fly = { t0: P.performance.now(), ms: ms };
  var a = tw(S, { x: t.x, y: t.y }, ms, E.sine);
  var up = tw(S, { jy: -tinggi }, ms * .5, E.out).then(function () { return tw(S, { jy: 0 }, ms * .5, E.inn); });
  await Promise.all([a, up]); chk(my);
  c.fly = null; c.pose = 'jump5'; c.show(IDX.jump5); c.kick(9);        // mendarat: menekan lalu memantul (pegas)
  await w(70, my); await gp(c, 'sit1', 34, my);
}
async function pulang(c, my) {
  var h = c.home(), S = c.S; c.diam();
  var jauh = Math.hypot(S.x - h.x, S.y - h.y);
  if (jauh > 4) { if (jauh > 260 || S.y - h.y > 150) await lompatKe(c, h.x, h.y, 70, 800, my); else await jalanKe(c, h.x, h.y, my); }
  c.yawB = 0; c.rollB = 0; c.pitB = 0; c.sqT = 0;
  if (c.pose !== 'sit0') await gp(c, 'sit0', 30, my);
}

// ------------------------------------------------------------------ aktivitas tunggal (26)
var AK = {};
AK.duduk_santai = async function (c, my) { await gp(c, 'sit0', 28, my); c.yawB = 12; await w(1100, my); await gp(c, 'sit1', 22, my); await w(1500, my); c.yawB = -10; await gp(c, 'sit5', 22, my); await w(1500, my); c.yawB = 0; await gp(c, 'sit0', 22, my); };
AK.menguap = async function (c, my) { await gp(c, 'sit0', 28, my); c.say('Hoaaam… 🥱', 2800); await gp(c, 'laugh4', 18, my); c.pitB = -4; c.kick(-3); await w(1700, my); c.pitB = 0; await gp(c, 'sit0', 20, my); };
AK.jilat_kaki = async function (c, my) { await gp(c, 'sit1', 28, my); await gp(c, 'lick0', 24, my);
  for (var i = 0; i < 4; i++) { await gp(c, 'lick1', 8, my); await gp(c, 'lick0', 8, my); } await w(300, my); await gp(c, 'sit1', 24, my); };
AK.cuci_muka = async function (c, my) { await gp(c, 'sit1', 28, my); await gp(c, 'lick0', 24, my);
  for (var i = 0; i < 6; i++) { c.rollB = i % 2 ? 3 : -3; await gp(c, 'lick1', 12, my); await gp(c, 'lick0', 12, my); } c.rollB = 0; await gp(c, 'sit1', 24, my); await gp(c, 'laugh4', 20, my); await w(500, my); };
AK.garuk_telinga = async function (c, my) { await gp(c, 'sit1', 28, my); await gp(c, 'lick0', 26, my); c.yawB = -10;
  for (var i = 0; i < 8; i++) { c.rollB = i % 2 ? 5 : -5; await w(120, my); } c.rollB = 0; c.yawB = 0; await gp(c, 'sit1', 24, my); };
AK.melambai = async function (c, my) { c.say('Hai hai! 👋', 3400); await gp(c, 'wave0', 26, my);
  for (var i = 0; i < 5; i++) { await gp(c, 'wave1', 10, my); await gp(c, 'wave0', 10, my); } await gp(c, 'sit0', 26, my); };
AK.mengeong = async function (c, my) { await gp(c, 'wave0', 28, my);
  for (var i = 0; i < 2; i++) { c.say(i ? 'Meooong~' : 'Meong!', 1500); c.kick(-4); await pz(c.S, { jy: -8 }, 200, E.out, my); await pz(c.S, { jy: 0 }, 220, E.inn, my); await w(700, my); } await gp(c, 'sit0', 26, my); };
AK.minta_makan = async function (c, my) {
  if (K.kenyang >= 4 && Date.now() - K.kenyangT < 120000) { c.say('Aku kenyang banget… 🥱', 3000); await gp(c, 'sit2', 24, my); await w(2600, my); return; }
  await gp(c, 'sit1', 26, my); c.say('Aku lapar 🍗 kasih makan dong…', 12000, true);
  for (var i = 0; i < 6; i++) { await gp(c, 'wave0', 14, my); c.kick(-3); await gp(c, 'wave1', 10, my); await gp(c, 'sit1', 20, my); await w(900, my); }
  c.diam(); c.say('Hmm… ya sudah 🙁', 2600); await gp(c, 'sit2', 22, my); await w(1800, my); };
AK.tidur = async function (c, my) { await gp(c, 'sit2', 24, my); c.pitB = 7; var z = ['Zzz…', 'Zzz… zzz…', 'Zzzz~'];
  for (var i = 0; i < 3; i++) { c.say(z[i], 2400); await pz(c, { sqT: .05 }, 1300, E.sine, my); await pz(c, { sqT: -.01 }, 1300, E.sine, my); }
  c.diam(); c.sqT = 0; c.pitB = 0; await gp(c, 'sit0', 24, my); await gp(c, 'laugh4', 20, my); await w(600, my); };
AK.peregangan = async function (c, my) { await gp(c, 'jump4', 40, my); await par([tw(c, { sqT: -.1 }, 900, E.io), tw(c, { pitB: 9 }, 900, E.io)], my); await w(1400, my);
  await par([tw(c, { sqT: 0 }, 700, E.io), tw(c, { pitB: 0 }, 700, E.io)], my); await gp(c, 'sit1', 40, my); await gp(c, 'laugh4', 20, my); await w(500, my); };
AK.jalan_santai = async function (c, my) { var h = c.home(); await jalanKe(c, clamp(h.x - rnd(130, 260), 60, 9999), h.y + rnd(0, 60), my, 62);
  await gp(c, 'sit1', 24, my); c.yawB = -14; await w(800, my); await gp(c, 'sit5', 22, my); c.yawB = 12; await w(1000, my); c.yawB = 0; };
AK.lari_keliling = async function (c, my) { c.say('Wuuush! 💨', 2000); var h = c.home(); await jalanKe(c, 60, h.y + 40, my, 230); await w(150, my); await jalanKe(c, h.x, h.y, my, 230); };
AK.lompat_ditempat = async function (c, my) { var x0 = c.S.x, y0 = c.S.y; for (var i = 0; i < 3; i++) { await lompatKe(c, x0, y0, 36 + i * 10, 560, my); await w(100, my); } await gp(c, 'wave0', 26, my); await w(500, my); };
AK.lompat_jauh = async function (c, my) { var h = c.home(); await lompatKe(c, h.x - rnd(130, 240), h.y + rnd(80, 190), 90, 900, my); await w(900, my); await lompatKe(c, h.x, h.y, 100, 950, my); };
AK.kejar_ekor = async function (c, my) { await gp(c, 'sit5', 26, my);
  for (var i = 0; i < 6; i++) { var d = i % 2 ? 1 : -1; await par([tw(c, { yawB: 48 * d, rollB: 5 * d }, 340, E.sine), tw(c.S, { jy: -5 }, 170, E.out)], my); await tw(c.S, { jy: 0 }, 170, E.inn); chk(my); }
  await par([tw(c, { yawB: 0, rollB: 0 }, 300, E.io)], my); await gp(c, 'sit0', 24, my); await gp(c, 'laugh4', 20, my); await w(600, my); };
AK.berguling = async function (c, my) { await gp(c, 'sit0', 28, my); await gp(c, 'wave0', 28, my); await gp(c, 'laugh1', 20, my); await gp(c, 'laugh2', 16, my); await gp(c, 'laugh3', 16, my);
  c.rollB = 0; await par([tw(c, { rollB: 360 }, 1300, E.io), tw(c.S, { jy: -10 }, 650, E.sine)], my); await tw(c.S, { jy: 0 }, 300, E.inn); c.S.roll = 0; c.S.rollv = 0; c.rollB = 0;
  await w(600, my); await gp(c, 'laugh4', 18, my); await gp(c, 'sit0', 22, my); };
AK.menoleh = async function (c, my) { c.say('Ada apa ya? 👀', 2800); await gp(c, 'sit0', 28, my); c.yawB = -12; await w(500, my); await gp(c, 'sit1', 18, my); await w(600, my);
  await gp(c, 'sit5', 18, my); await w(500, my); await gp(c, 'sit4', 16, my); await w(900, my); await gp(c, 'sit5', 16, my); c.yawB = 10; await gp(c, 'sit1', 18, my); await w(400, my); c.yawB = 0; await gp(c, 'sit0', 22, my); };
AK.mengintip = async function (c, my) { var h = c.home(); await jalanKe(c, 80, h.y + 30, my, 90); await gp(c, 'sit1', 24, my);
  await pz(c.S, { x: 26 }, 900, E.io, my); c.yawB = -22; c.rollB = -4; await w(1700, my); await gp(c, 'laugh4', 20, my); await w(600, my); c.yawB = 0; c.rollB = 0; await pz(c.S, { x: 90 }, 700, E.io, my); };
AK.menari = async function (c, my) { c.say('♪ ♫', 4800); await gp(c, 'wave0', 26, my); var ps = ['laugh1', 'laugh2', 'laugh3', 'laugh2', 'laugh1', 'wave1'];
  for (var i = 0; i < ps.length; i++) { var s = i % 2 ? 1 : -1; c.rollB = 7 * s; c.yawB = 16 * s; var a = c.go(ps[i], 16); await par([a, tw(c.S, { jy: -9 }, 240, E.out)], my); await pz(c.S, { jy: 0 }, 200, E.inn, my); c.kick(5); await w(120, my); }
  c.rollB = 0; c.yawB = 0; await gp(c, 'sit0', 22, my); };
AK.kupu_kupu = async function (c, my) {
  var S = c.S; await gp(c, 'sit1', 26, my);
  var kp = D.createElement('div'); kp.className = 'uj-fx'; kp.textContent = '🦋'; kp.style.fontSize = '22px'; D.body.appendChild(kp);
  var t0 = P.performance.now(), dur = 3800, sx = S.x - 200, sy = S.y + 90, run = true;
  var kx = function (p) { return sx + (S.x - sx - 4) * p + Math.sin(p * 9) * 26; }, ky = function (p) { return sy + (S.y - 70 - sy) * p + Math.cos(p * 7) * 18; };
  (function f(now) { var p = Math.min(1, (now - t0) / dur); kp.style.transform = 'translate3d(' + kx(p) + 'px,' + ky(p) + 'px,0) rotate(' + Math.sin(p * 30) * 14 + 'deg)'; if (run && p < 1) P.requestAnimationFrame(f); else kp.remove(); })(t0);
  try {
    for (var i = 0; i < 6; i++) { var p2 = (i + 1) / 7; c.yawB = clamp((kx(p2) - S.x) * .12, -22, 22); c.pitB = clamp((S.y - 70 - ky(p2)) * -.04, -6, 6); await w(560, my); }
    c.say('Tangkap! 🦋', 1800); await lompatKe(c, S.x - 8, S.y, 56, 460, my); run = false; kp.remove(); await gp(c, 'laugh4', 20, my); await w(700, my);
  } finally { run = false; kp.remove(); c.yawB = 0; c.pitB = 0; } };
AK.mengendus = async function (c, my) { var h = c.home(); await jalanKe(c, h.x - 40, h.y + 30, my, 70); c.pitB = 9;
  for (var i = 0; i < 3; i++) { await jalanKe(c, c.S.x - 36, c.S.y, my, 34); await w(300, my); } c.pitB = 0; c.say('Wangi ayam goreng! 🍗', 2600); await w(1200, my); };
AK.kaget = async function (c, my) { await gp(c, 'sit0', 28, my); c.say('!?', 1800); c.kick(-12); await lompatKe(c, c.S.x + 22, c.S.y, 62, 520, my); await w(500, my); await gp(c, 'sit0', 22, my); c.say('Ternyata cuma angin 😅', 2600); await w(1500, my); };
AK.senyum_ceria = async function (c, my) { await gp(c, 'sit0', 28, my); await c.cross('laugh0', 220); chk(my); c.hati(5); c.kick(-4); await w(1700, my); await gp(c, 'laugh4', 20, my); await w(700, my); await gp(c, 'sit0', 22, my); };
AK.mengantuk = async function (c, my) { c.say('Hoaaam… 🥱', 2500); await gp(c, 'sit0', 28, my);
  for (var i = 0; i < 3; i++) { await par([tw(c, { pitB: 10, sqT: .05 }, 1100, E.io)], my); await par([tw(c, { pitB: 0, sqT: 0 }, 260, E.out)], my); await w(160, my); }
  await gp(c, 'laugh4', 18, my); await w(700, my); await gp(c, 'sit0', 22, my); };
AK.berdiri = async function (c, my) { await gp(c, 'wave0', 26, my); c.kick(-5); c.say('Ta-daaa! ✨', 2800);
  var ps = ['laugh1', 'wave1', 'wave0']; for (var i = 0; i < 3; i++) { c.rollB = i % 2 ? 4 : -4; await gp(c, ps[i], 14, my); await w(350, my); } c.rollB = 0; await gp(c, 'sit0', 24, my); };
AK.turun_naik = async function (c, my) { var h = c.home(); c.say('Jalan-jalan dulu ya~', 2500);
  await lompatKe(c, h.x - 70, h.y + 150, 70, 800, my); await lompatKe(c, h.x - 150, c.maxY() - 20, 70, 900, my);
  await jalanKe(c, h.x - 270, c.maxY(), my, 90); await w(500, my); await jalanKe(c, h.x - 120, c.maxY(), my, 80); await lompatKe(c, h.x, h.y, 110, 1100, my); };
var SOLO = Object.keys(AK); K.AK = AK;

// ------------------------------------------------------------------ interaksi dua kucing (14)
var DU = {};
function hadapan(A, B) { A.setFace(1); B.setFace(-1); }
async function temu(A, B, my, jarak, y) {
  var mx = clamp((A.S.x + B.S.x) / 2, 130, Math.max(140, vw() - 130)); y = y || 180; jarak = jarak || 96;
  await Promise.all([jalanKe(A, mx - jarak / 2, y, my, 105), jalanKe(B, mx + jarak / 2, y, my, 105)]); chk(my); hadapan(A, B);
}
function kirim(emoji, dari, ke, ms, tinggi) {
  var n = D.createElement('div'); n.className = 'uj-fx'; n.textContent = emoji; n.style.fontSize = '24px'; D.body.appendChild(n);
  var t0 = P.performance.now(), x0 = dari.S.x - 10, y0 = dari.S.y - 70, x1 = ke.S.x - 10, y1 = ke.S.y - 70;
  return new Promise(function (res) { (function f(now) { var p = Math.min(1, (now - t0) / ms);
    n.style.transform = 'translate3d(' + (x0 + (x1 - x0) * p) + 'px,' + (y0 + (y1 - y0) * p - Math.sin(p * Math.PI) * (tinggi || 40)) + 'px,0) rotate(' + (p * 540) + 'deg)';
    if (p < 1) P.requestAnimationFrame(f); else { n.remove(); res(); } })(t0); });
}
DU.saling_sapa = async function (A, B, my) { await temu(A, B, my); A.say('Hai Oyen! 👋', 2800); await gp(A, 'wave0', 26, my); await w(400, my);
  B.say('Hai Krish! 🧡', 2800); await Promise.all([gp(B, 'wave0', 26, my)]);
  for (var i = 0; i < 4; i++) { A.go(i % 2 ? 'wave0' : 'wave1', 10); B.go(i % 2 ? 'wave1' : 'wave0', 10); await w(420, my); }
  await Promise.all([gp(A, 'sit0', 26, my), gp(B, 'sit0', 26, my)]); };
DU.kejar_kejaran = async function (A, B, my) { var h = A.home(); B.say('Tangkap aku kalau bisa! 😜', 2400);
  for (var r = 0; r < 2; r++) {
    var lari = [jalanKe(B, 70, 190, my, 215)]; await w(420, my); lari.push(jalanKe(A, 70, 190, my, 225)); await Promise.all(lari); chk(my);
    lari = [jalanKe(B, h.x, 130, my, 215)]; await w(420, my); lari.push(jalanKe(A, h.x - 70, 130, my, 225)); await Promise.all(lari); chk(my);
  }
  A.say('Kena! 😸', 2000); await Promise.all([gp(A, 'laugh4', 20, my), gp(B, 'laugh4', 20, my)]); await w(900, my); };
DU.tos_lompat = async function (A, B, my) { await temu(A, B, my, 170); var mx = (A.S.x + B.S.x) / 2, y = A.S.y;
  A.say('Siap? 3-2-1…', 2000); await w(900, my);
  await Promise.all([lompatKe(A, mx - 26, y, 96, 760, my), lompatKe(B, mx + 26, y, 96, 760, my).then(function () { })]); chk(my);
  fx('✨', mx - 12, y - 120, 0, -10, 900, 30); A.say('Tos! 🙌', 1800); B.say('Yeay! 🧡', 1800); A.hati(2); B.hati(2); await w(1500, my);
  await Promise.all([gp(A, 'sit0', 26, my), gp(B, 'sit0', 26, my)]); hadapan(A, B); };
DU.berbagi_makan = async function (A, B, my) { await temu(A, B, my, 130); A.say('Ini buat kamu 🍗', 2400); await gp(A, 'wave0', 26, my); await kirim('🍗', A, B, 800, 46); chk(my);
  B.say('Nyam! Makasih Krish 😻', 3000); await Promise.all([gp(B, 'laugh4', 20, my)]);
  for (var i = 0; i < 4; i++) { await gp(B, 'sit0', 8, my); await gp(B, 'laugh4', 8, my); } B.hati(3); A.hati(2); await w(600, my); await Promise.all([gp(A, 'sit0', 26, my), gp(B, 'sit0', 26, my)]); };
DU.saling_merawat = async function (A, B, my) { await temu(A, B, my, 88); await Promise.all([gp(A, 'sit1', 26, my), gp(B, 'sit1', 26, my)]); hadapan(A, B);
  A.say('Sini kubersihkan 🧼', 2400); await gp(A, 'lick0', 24, my); for (var i = 0; i < 4; i++) { await gp(A, 'lick1', 8, my); await gp(A, 'lick0', 8, my); }
  B.say('Gantian ya! 😽', 2200); await gp(B, 'lick0', 24, my); for (var j = 0; j < 4; j++) { await gp(B, 'lick1', 8, my); await gp(B, 'lick0', 8, my); }
  A.hati(3); B.hati(3); await w(700, my); await Promise.all([gp(A, 'sit1', 24, my), gp(B, 'sit1', 24, my)]); };
DU.menari_bareng = async function (A, B, my) { await temu(A, B, my, 104); A.say('♪ Ayo menari! ♫', 4800); B.say('♫ Satu, dua, tiga! ♪', 4800);
  var ps = ['laugh1', 'laugh2', 'laugh3', 'laugh2', 'laugh1', 'wave1'];
  for (var i = 0; i < ps.length; i++) { var s = i % 2 ? 1 : -1; A.rollB = 7 * s; B.rollB = -7 * s; A.yawB = 16 * s; B.yawB = -16 * s;
    await par([A.go(ps[i], 16), B.go(ps[(i + 1) % ps.length], 16), tw(A.S, { jy: -9 }, 240, E.out), tw(B.S, { jy: -9 }, 240, E.out)], my);
    await par([tw(A.S, { jy: 0 }, 200, E.inn), tw(B.S, { jy: 0 }, 200, E.inn)], my); A.kick(5); B.kick(5); await w(100, my); }
  A.rollB = B.rollB = A.yawB = B.yawB = 0; await Promise.all([gp(A, 'sit0', 22, my), gp(B, 'sit0', 22, my)]); hadapan(A, B); };
DU.tidur_bareng = async function (A, B, my) { await temu(A, B, my, 82); await Promise.all([gp(A, 'sit2', 24, my), gp(B, 'sit2', 24, my)]); hadapan(A, B);
  A.pitB = B.pitB = 6; A.say('Zzz…', 2400); await w(1200, my); B.say('Zzz… zzz…', 2400);
  for (var i = 0; i < 3; i++) { await par([tw(A, { sqT: .05 }, 1200, E.sine), tw(B, { sqT: .05 }, 1300, E.sine)], my); await par([tw(A, { sqT: -.01 }, 1200, E.sine), tw(B, { sqT: -.01 }, 1300, E.sine)], my); }
  A.sqT = B.sqT = A.pitB = B.pitB = 0; A.say('Hoaaam, sudah pagi? 🥱', 2600); await Promise.all([gp(A, 'laugh4', 20, my), gp(B, 'laugh4', 20, my)]); await w(900, my);
  await Promise.all([gp(A, 'sit0', 22, my), gp(B, 'sit0', 22, my)]); };
DU.main_bola = async function (A, B, my) { await temu(A, B, my, 230, 190); A.say('Tangkap bolanya! 🧶', 2200); await gp(A, 'sit1', 26, my); hadapan(A, B);
  var p = [A, B, A, B];
  for (var i = 0; i < 3; i++) { var d = p[i], k = p[i + 1]; d.kick(-5); await kirim('🧶', d, k, 850, 70); chk(my);
    k.say(i % 2 ? 'Hap! 😸' : 'Hup! 😺', 1200); await lompatKe(k, k.S.x, k.S.y, 44, 480, my); hadapan(A, B); }
  A.hati(2); B.hati(2); await w(700, my); await Promise.all([gp(A, 'sit0', 22, my), gp(B, 'sit0', 22, my)]); };
DU.petak_umpet = async function (A, B, my) { var h = A.home(); A.say('Aku hitung ya… 1, 2, 3 🙈', 2600); await gp(A, 'sit1', 26, my); A.yawB = 20; await w(1200, my);
  await jalanKe(B, 60, 200, my, 150); await Promise.all([gp(B, 'sit1', 26, my)]); await pz(B.S, { x: 24 }, 500, E.io, my); A.yawB = 0;
  A.say('Oyen di mana ya…? 👀', 2800); await jalanKe(A, h.x - 120, 150, my, 70); await jalanKe(A, h.x - 40, 190, my, 70); await jalanKe(A, 150, 200, my, 80);
  B.yawB = -20; await w(300, my); A.say('Ketemu! 😸', 2000); await lompatKe(A, 96, 200, 50, 520, my); B.yawB = 0; B.say('Aaah ketahuan! 🙀', 2200);
  await Promise.all([gp(A, 'laugh4', 20, my), gp(B, 'laugh4', 20, my)]); await w(1100, my); };
DU.peluk_sayang = async function (A, B, my) { await temu(A, B, my, 66); await Promise.all([gp(A, 'sit1', 26, my), gp(B, 'sit1', 26, my)]); hadapan(A, B);
  A.rollB = 6; B.rollB = -6; A.yawB = 10; B.yawB = -10; A.say('Sayang Oyen 💕', 3000); await w(900, my); B.say('Sayang Krish 🧡', 3000);
  A.hati(4, '💕'); B.hati(4, '🧡'); await Promise.all([gp(A, 'laugh4', 18, my), gp(B, 'laugh4', 18, my)]); await w(1500, my);
  A.rollB = B.rollB = A.yawB = B.yawB = 0; await Promise.all([gp(A, 'sit0', 22, my), gp(B, 'sit0', 22, my)]); };
DU.ngobrol_tertawa = async function (A, B, my) { await temu(A, B, my, 100); await Promise.all([gp(A, 'sit1', 26, my), gp(B, 'sit1', 26, my)]); hadapan(A, B);
  var l = [['Kenapa ayam nyebrang jalan? 🐔', 'Kenapa hayo?'], ['Mau ke warung Ungkep Jowo! 🍗', 'Hahaha! 😹']];
  A.say(l[0][0], 2600); await w(1800, my); B.say(l[0][1], 2000); await w(1500, my); A.say(l[1][0], 2600); await w(1700, my);
  B.say(l[1][1], 2400); await Promise.all([gp(A, 'laugh4', 18, my), gp(B, 'laugh2', 14, my)]); await Promise.all([gp(B, 'laugh3', 14, my)]); await w(1200, my);
  await Promise.all([gp(A, 'sit0', 22, my), gp(B, 'sit0', 22, my)]); hadapan(A, B); };
DU.adu_lari = async function (A, B, my) { var h = A.home(); A.say('Lomba lari! Siap… mulai! 🏁', 2200); await w(900, my);
  var a = jalanKe(A, 70, 150, my, 200), b = jalanKe(B, 70, 210, my, 220); await Promise.all([a, b]); chk(my); B.say('Aku menang! 🏆', 2200); A.say('Curang~ ayo lagi!', 2200); await w(1100, my);
  var a2 = jalanKe(A, h.x, 130, my, 225), b2 = jalanKe(B, h.x - 100, 190, my, 205); await Promise.all([a2, b2]); chk(my); A.say('Aku yang menang! 🥇', 2200); await Promise.all([gp(A, 'laugh4', 20, my), gp(B, 'laugh4', 20, my)]); await w(900, my); };
DU.lomba_lompat = async function (A, B, my) { await temu(A, B, my, 180, 200); var t = [[A, 52, 'Segini!'], [B, 78, 'Aku lebih tinggi! 😼'], [A, 100, 'Lihat ini! 😸'], [B, 124, 'Juara! 🏆']];
  for (var i = 0; i < t.length; i++) { var c = t[i][0]; c.say(t[i][2], 1500); await lompatKe(c, c.S.x, c.S.y, t[i][1], 600 + i * 60, my); hadapan(A, B); await w(250, my); }
  await Promise.all([gp(A, 'laugh4', 20, my), gp(B, 'laugh4', 20, my)]); await w(800, my); };
DU.kaget_bareng = async function (A, B, my) { await temu(A, B, my, 90); await Promise.all([gp(A, 'sit1', 26, my), gp(B, 'sit1', 26, my)]); hadapan(A, B);
  fx('🐞', A.S.x + 40, A.S.y - 70, 8, -12, 1500, 22); A.say('Eh, ada kepik! 🐞', 2000); B.say('Wah!', 1600); A.kick(-12); B.kick(-12);
  await Promise.all([lompatKe(A, A.S.x - 20, A.S.y, 56, 480, my), lompatKe(B, B.S.x + 20, B.S.y, 56, 480, my)]); hadapan(A, B); await w(500, my);
  A.say('Ternyata lucu~ 😸', 2200); B.say('Hihihi 😹', 2200); await Promise.all([gp(A, 'laugh4', 20, my), gp(B, 'laugh4', 20, my)]); await w(900, my); };
var DUET = Object.keys(DU); K.DU = DU;

// ------------------------------------------------------------------ pengatur giliran (tiap ±5 detik)
function aktifCats() { return K.cats.filter(function (c) { return c.aktif; }); }
function pilihAksi() {
  if (K.paksa) { var pn = K.paksa, pc = K[K.paksaC || 'pom']; if (DU[pn]) return { n: pn, f: function (my) { return DU[pn](K.pom, K.oy, my); } }; return { n: pn, f: function (my) { return AK[pn](pc, my); } }; }
  var adm = K.mod === 'admin' && K.oy && K.oy.aktif, n, c;
  if (adm && Math.random() < .55) {
    var dl = DUET.filter(function (x) { return x !== K.lastAct; }); n = pick(dl);
    return { n: n, f: function (my) { return DU[n](K.pom, K.oy, my); } };
  }
  c = adm && Math.random() < .5 ? K.oy : K.pom;
  var sl = SOLO.filter(function (x) { return x !== K.lastAct; }); n = pick(sl);
  if (n === 'minta_makan' && Date.now() - K.fedLast < 60000) n = 'senyum_ceria';
  return { n: n, f: function (my) { return AK[n](c, my); } };
}
function giliran(delay) {
  clearTimeout(K.timer);
  K.tNext = Date.now() + (delay == null ? 5000 : delay);
  K.timer = setTimeout(function () { var a = pilihAksi(); K.jalankan(a.n, a.f); }, delay == null ? 5000 : delay);
}
K.jalankan = function (nama, fn) {
  if (K.sembunyi) { giliran(3000); return; }
  stopAll(); K.mulai = Date.now(); var my = GT; aktifCats().forEach(function (c) { c.diam(); }); K.lastAct = nama; K.sibuk = nama;
  (async function () {
    try { await fn(my); chk(my); await Promise.all(aktifCats().map(function (c) { return pulang(c, my); })); }
    catch (e) { if (e !== 'batal') console.warn(e); }
  })().then(function () { if (my === GT) { K.sibuk = ''; giliran(5000); } });
};
K.hide = function () { K.sembunyi = true; K.cats.forEach(function (c) { c.el.classList.add('sembunyi'); c.diam(); }); };
K.show = function () { K.sembunyi = false; K.cats.forEach(function (c) { c.el.classList.remove('sembunyi'); }); };
K.kabarBaru = function (t) { K.pom.say(t, 6000); K.pom.hati(2); };

// ------------------------------------------------------------------ sambutan: tersenyum, melompat dari kiri ke kanan, lalu melambai
K.sambut = function (cfg) {
  K.show(); var c = K.pom;
  K.jalankan('sambut', async function (my) {
    var h = c.home(), S = c.S; S.x = -64; S.y = h.y + 66; S.op = 0; S.jy = 0; c.setFace(1); c.set('sit1');
    await par([tw(S, { op: 1 }, 380, E.out), tw(S, { x: 40 }, 520, E.out)], my);
    c.say(cfg.sapa, 5200); c.hati(3); await gp(c, 'laugh4', 18, my); await w(500, my); await gp(c, 'sit1', 22, my);
    var n = Math.max(3, Math.round((h.x - S.x) / 76));
    for (var i = 1; i <= n; i++) {
      var tx = S.x + (h.x - S.x) / (n - i + 1);
      await lompatKe(c, tx, i === n ? h.y : h.y + 66 + (i % 2 ? 10 : -4), 40 + (i % 3) * 12, 640, my);
    }
    c.say('Halo ' + (cfg.nama || '') + '! Mau pesan apa hari ini? 🍛', 5600);
    await gp(c, 'wave0', 26, my);
    for (var k = 0; k < 6; k++) { await gp(c, 'wave1', 10, my); await gp(c, 'wave0', 10, my); }
    if (cfg.kabar) { c.say(cfg.kabar, 6000); await w(2500, my); }
    await w(500, my);
  });
};

// ------------------------------------------------------------------ halaman admin: Oyen datang menemani Krish
K.masukOyen = function () {
  K.show(); var A = K.pom, B = K.oy;
  K.jalankan('oyen_masuk', async function (my) {
    var h = B.home(), S = B.S; B.aktif = true; B.el.style.display = ''; B.set('sit1'); B.setFace(1); S.x = -64; S.y = h.y + 60; S.op = 1;
    A.say('Ada yang datang… 👀', 1800); A.yawB = -14; await w(500, my);
    await jalanKe(B, h.x, h.y, my, 130); A.yawB = 0; hadapan(B, A); B.setFace(1); A.setFace(1);
    A.say('Hai Oyen! Selamat datang di halaman admin 😸', 3200); await gp(A, 'wave0', 26, my); await w(600, my);
    B.say('Hai Krish! Ayo jaga warung bareng 🧡', 3200); await gp(B, 'wave0', 26, my);
    for (var i = 0; i < 4; i++) { A.go(i % 2 ? 'wave0' : 'wave1', 10); B.go(i % 2 ? 'wave1' : 'wave0', 10); await w(420, my); }
    await w(500, my);
  });
};
K.keluarOyen = function () {
  var B = K.oy; if (!B || !B.aktif || B.pergi) return; B.pergi = true;
  K.jalankan('oyen_pergi', async function (my) {
    B.say('Dadah~ aku istirahat dulu 👋', 2200); await gp(B, 'wave0', 26, my); await w(900, my); B.diam();
    await jalanKe(B, 56, B.S.y + 30, my, 150); await pz(B.S, { x: -80, op: 0 }, 800, E.io, my);
    B.aktif = false; B.pergi = false; B.el.style.display = 'none';
  });
};

// ------------------------------------------------------------------ memberi makan
var FOOD = { '🍗': ['Nyam nyam! Ayam goreng kriuk 😻', 'ayam'], '🍤': ['Udang goreng! Gurih banget~ 😋', 'udang'], '🐟': ['Ikan! Favoritkuuu 🐟💕', 'ikan'],
  '🥩': ['Dagingnya empuk! 😍', 'daging'], '🥛': ['Slurp… susunya enak~ 🥛', 'susu'], '🍚': ['Nasi hangat… ngenyangin 🍚', 'nasi'] };
K.beriMakan = function (c, e, btn) {
  var r = btn ? btn.getBoundingClientRect() : { left: c.S.x, top: c.S.y + 20 };
  var mx = c.S.x - 8, my2 = c.S.y - 52, sx = r.left, sy = r.top; fx(e, sx, sy, mx - sx, my2 - sy, 700, 24);
  K.kenyang = (Date.now() - K.kenyangT > 120000) ? 1 : K.kenyang + 1; K.kenyangT = Date.now(); K.fedLast = Date.now();
  var info = FOOD[e] || ['Enak!', 'makanan'], penuh = K.kenyang >= 4;
  K.jalankan('makan', async function (my) {
    await gp(c, 'sit0', 28, my); await w(560, my); c.say('…', 900);
    await gp(c, 'laugh4', 18, my);
    for (var i = 0; i < 5; i++) { c.rollB = i % 2 ? 3 : -3; await gp(c, 'sit0', 8, my); await gp(c, 'laugh4', 8, my); }
    c.rollB = 0; c.say(penuh ? 'Huaah… kenyang! Makasih ya 🥰' : info[0], 3400); c.hati(4); c.kick(-6); await w(2000, my);
  });
};

// ------------------------------------------------------------------ interaksi pengguna
function reaksi(c) {
  K.jalankan('sentuh', async function (my) {
    c.say(c === K.oy ? 'Nyaaa! Mau main? 🧡' : 'Meong! Mau tanya apa? 🐾', 2800); c.hati(3);
    await gp(c, 'sit0', 28, my); await lompatKe(c, c.S.x, c.S.y, 34, 460, my); await gp(c, 'laugh4', 18, my); await w(1100, my);
  });
}
function pasangKlik(c) { c.hit.addEventListener('click', function () { reaksi(c); }, true); }
D.addEventListener('pointerdown', function (e) {
  if (K.sembunyi || K.mod !== 'user' || K.sibuk === 'sambut') return;
  var t = e.target; if (!t || !t.closest) return;
  if (t.closest('.uj-cat,.uj-gelembung,button,a,input,select,textarea,label,table,[data-c],[role=dialog],[data-testid=stDialog],[data-baseweb],[data-testid=stExpander],iframe,svg')) return;
  var c = K.pom, tx = e.clientX, ty = e.clientY + 70;
  K.jalankan('panggil', async function (my) {
    c.say('Datang~ 🐾', 1600); var far = Math.hypot(tx - c.S.x, ty - c.S.y);
    if (far > 150) await lompatKe(c, tx, ty, Math.min(100, 44 + far * .1), Math.min(1100, 520 + far), my); else await jalanKe(c, tx, ty, my, 90);
    c.hati(2); await gp(c, 'laugh4', 18, my); await w(2000, my);
  });
}, true);
P.addEventListener('resize', function () { if (!K.sibuk) K.cats.forEach(function (c) { if (c.aktif) { var h = c.home(); c.S.x = h.x; } }); });
D.addEventListener('visibilitychange', function () {
  lastT = 0;
  if (D.hidden) { stopAll(); K.sibuk = ''; }                       // tab disembunyikan: hentikan, jangan menumpuk tugas
  else if (!K.sembunyi && K.siap) { K.cats.forEach(function (c) { if (c.aktif) c.diam(); }); giliran(900); }
});
setInterval(function () {                                           // penjaga: bila animasi macet lama, mulai ulang
  try {
    if (D.hidden || K.sembunyi || !K.siap) return;
    var n = Date.now();
    if (K.sibuk && n - (K.mulai || n) > 90000) { stopAll(); K.sibuk = ''; giliran(300); }
    else if (!K.sibuk && n - (K.tNext || n) > 15000) { giliran(300); }
    if (K.beat && n - K.beat > 4000) P.requestAnimationFrame(frame);
    var ada = D.querySelectorAll('.uj-cat'); if (ada.length > K.cats.length) [].forEach.call(ada, function (e) { if (!K.cats.some(function (c) { return c.el === e; })) e.remove(); });
    [].forEach.call(D.querySelectorAll('.uj-fx'), function (e) { if (!e.__t) e.__t = n; else if (n - e.__t > 5000) e.remove(); });
    K.cats.forEach(function (c) { if (c.aktif && !c.xf) { c.L[1 - c.front].style.opacity = 0; } });
  } catch (er) { }
}, 4000);

// ------------------------------------------------------------------ mulai
function aturKlik() { if (K.pom) K.pom.hit.setAttribute('data-c', K.mod === 'user' ? 'k|chat' : ''); if (K.pom && K.mod !== 'user') K.pom.hit.removeAttribute('data-c'); }
function muatAtlas(url) { return new Promise(function (res) { var im = new P.Image(); im.onload = im.onerror = function () { res(); }; im.src = url; }); }
K.mode = function (m, cfg) {
  cfg = cfg || {}; K.show();
  var admin = m === 'admin';
  if (cfg.b64 && cfg.b64.oyen && !URLS.oyen) URLS.oyen = blobUrl(cfg.b64.oyen);
  if (cfg.tema && cfg.tema !== K.temaUrl) { K.temaUrl = cfg.tema; K.muatTema(cfg.tema, cfg.musim); }
  if (admin) {
    if (!URLS.oyen) return;
    if (!K.oy) {
      K.oy = new Cat('oyen', URLS.oyen, 'Oyen'); K.oy.slot = 1; K.oy.aktif = false; K.oy.el.style.display = 'none'; K.cats.push(K.oy); pasangKlik(K.oy);
      K.oy.S.op = 1;
    }
    K.mod = 'admin'; aturKlik();
    if (!K.oy.aktif && !K.masuk) { K.masuk = 1; muatAtlas(URLS.oyen).then(function () { K.masuk = 0; if (K.mod === 'admin') K.masukOyen(); }); }
  } else {
    var dariAdmin = K.mod === 'admin'; K.mod = 'user'; aturKlik();
    if (cfg.sapa) K.sambut(cfg);
    else { if (dariAdmin) K.keluarOyen(); if (cfg.kabar) K.kabarBaru(cfg.kabar); }
  }
};
// ------------------------------------------------------------------ tema musim (diatur lewat tema.json di hosting statis, bisa diganti kapan saja)
K.tema = function (t) {
  var D2 = D, id = 'uj-tema-css', old = D2.getElementById(id); if (old) old.remove();
  [].forEach.call(D2.querySelectorAll('.uj-musim'), function (e) { e.remove(); });
  if (!t) return;
  if (t.css) { var st2 = D2.createElement('style'); st2.id = id; st2.textContent = t.css; D2.head.appendChild(st2); }
  var pt = t.partikel || {}; if (!t.tint && !(pt.emoji && pt.emoji.length)) return;
  var wrap = D2.createElement('div'); wrap.className = 'uj-musim'; if (t.tint) wrap.style.background = t.tint; var n = (pt.emoji && pt.emoji.length) ? Math.min(16, pt.jumlah || 10) : 0;
  for (var i = 0; i < n; i++) {
    var e = D2.createElement('span'); e.textContent = pt.emoji[i % pt.emoji.length];
    var dur = (pt.durasi || 12) * (.7 + Math.random() * .8);
    e.style.cssText = 'left:' + (Math.random() * 100).toFixed(1) + '%;font-size:' + (10 + Math.random() * 12).toFixed(0) + 'px;animation-duration:' + dur.toFixed(1) + 's;animation-delay:-' + (Math.random() * dur).toFixed(1) + 's;--dx:' + ((Math.random() - .5) * 90).toFixed(0) + 'px;';
    wrap.appendChild(e);
  }
  wrap.className += ' ' + (pt.arah === 'naik' ? 'naik' : 'turun'); D2.body.appendChild(wrap);
};
K.muatTema = function (url, paksa) {
  if (!url || !P.fetch) return;
  P.fetch(url + (url.indexOf('?') < 0 ? '?' : '&') + 't=' + Math.floor(Date.now() / 600000)).then(function (r) { return r.json(); }).then(function (j) {
    var nm = paksa || j.aktif, t = j.tema && j.tema[nm]; K.musim = nm; K.tema(t);
  }).catch(function () { });
};
D.addEventListener('visibilitychange', function () { [].forEach.call(D.querySelectorAll('.uj-musim'), function (e) { e.style.animationPlayState = D.hidden ? 'paused' : 'running'; }); });
P.__ujKucing = K;
K.pom = new Cat('krish', URLS.krish, 'Krish'); K.pom.slot = 0; K.cats.push(K.pom); pasangKlik(K.pom);
(function () {
  var h = K.pom.home(); K.pom.S.x = h.x; K.pom.S.y = h.y; K.pom.lx = h.x; K.pom.ly = h.y; K.pom.aktif = true;
  P.requestAnimationFrame(frame);
  if (CFG.tema) { K.temaUrl = CFG.tema; K.muatTema(CFG.tema, CFG.musim); }
  muatAtlas(URLS.krish).then(function () {
    K.pom.S.op = 1; K.siap = true;
    if (CFG.mode === 'admin') K.mode('admin', CFG);
    else if (CFG.sapa) { K.mod = 'user'; aturKlik(); K.sambut(CFG); }
    else { K.mod = 'user'; aturKlik(); giliran(2500); if (CFG.kabar) setTimeout(function () { K.kabarBaru(CFG.kabar); }, 1500); }
  });
})();

};})();
