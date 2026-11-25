/* =====================================================================
   Lisensi Revo.id untuk aplikasi HTML statis (dipakai bersama semua situs).
   Disisipkan ke index.html oleh tools/build.mjs. Tanpa API key: kredensialnya
   kode lisensi itu sendiri. Endpoint lisensi Revo mengizinkan CORS dari origin mana pun.
   ===================================================================== */
function buatLisensiRevo(opsi){
  const o = Object.assign({ api:'https://revo.id/api/v1', productId:'', terimaLisensiUji:false,
    kunci:'revo.lisensi', cekUlangJam:24, masaTenggangHari:7 }, opsi);
  const PESAN = {
    license_not_found:'Kode lisensi tidak ditemukan.',
    instance_not_activated:'Lisensi belum diaktifkan di perangkat ini.',
    license_expired:'Lisensi sudah kedaluwarsa.',
    license_disabled:'Lisensi dinonaktifkan oleh penjual.',
    license_refunded:'Lisensi tidak berlaku karena pembelian sudah di-refund.',
    product_mismatch:'Kode lisensi ini untuk produk lain.',
    activation_limit:'Batas perangkat untuk lisensi ini sudah habis. Lepas lisensi di perangkat lama dulu.',
    rate_limited:'Terlalu banyak percobaan. Coba lagi 1 menit lagi.',
    test_license:'Ini kode lisensi uji (sandbox), tidak berlaku di versi ini.'
  };
  const baca = (k, d) => { try{ const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); }catch(e){ return d; } };
  const tulis = (k, v) => { try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} };
  const hapus = k => { try{ localStorage.removeItem(k); }catch(e){} };
  function perangkat(){
    let id = baca(o.kunci + '.perangkat', null);
    if(!id){ id = crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + Math.random().toString(16).slice(2); tulis(o.kunci + '.perangkat', id); }
    return id;
  }
  async function panggil(aksi, body){
    const c = new AbortController(); const t = setTimeout(() => c.abort(), 15000);
    try{
      const res = await fetch(o.api.replace(/\/$/, '') + '/licenses/' + aksi, { method:'POST', signal:c.signal,
        headers:{ 'Content-Type':'application/json', 'Accept':'application/json' }, body: JSON.stringify(body) });
      let j = {}; try{ j = await res.json() || {}; }catch(e){}
      return { res, j };
    } finally { clearTimeout(t); }
  }
  const dasar = kode => ({ license_key: kode, product_id: Number(o.productId), instance: perangkat() });
  function hasil(res, j, ok){
    const lic = j.license || (j.data && j.data.license) || {};
    if(ok && lic.livemode === false && !o.terimaLisensiUji) return { valid:false, kode:'test_license', pesan:PESAN.test_license };
    if(ok) return { valid:true, kedaluwarsa: lic.expires_at || null };
    const kode = j.reason || j.code || '';
    return { valid:false, kode, jaringan: res.status >= 500 || res.status === 429, pesan: PESAN[kode] || j.message || ('Server lisensi membalas ' + res.status + '.') };
  }
  async function cek(kode, aktifkan){
    if(!o.productId) return { valid:false, pesan:'ID produk Revo belum diisi.' };
    try{
      if(!aktifkan){
        const { res, j } = await panggil('validate', dasar(kode));
        if(res.ok && j.valid === true) return hasil(res, j, true);
        if(!(res.ok && j.reason === 'instance_not_activated')) return hasil(res, j, false);
      }
      const { res, j } = await panggil('activate', { ...dasar(kode), label: (location.hostname || 'lokal') + ' · ' + (navigator.platform || 'perangkat') });
      const r = hasil(res, j, res.ok && j.activated !== false);
      if(r.kode === 'test_license') panggil('deactivate', dasar(kode)).catch(() => {});
      return r;
    }catch(e){ return { valid:false, jaringan:true, pesan:'Server lisensi tidak terjangkau. Cek koneksi internetmu.' }; }
  }
  const berlaku = l => !l.kedaluwarsa || isNaN(Date.parse(l.kedaluwarsa)) || Date.parse(l.kedaluwarsa) > Date.now();
  return {
    /** Lisensi tersimpan yang masih sah, atau null. Cek ulang ke Revo bila sudah lewat cekUlangJam. */
    async status(){
      const l = baca(o.kunci, null);
      if(!l || !l.kode) return { aktif:false };
      const umurJam = (Date.now() - (l.dicek || 0)) / 36e5;
      if(umurJam < o.cekUlangJam && berlaku(l)) return { aktif:true, lisensi:l };
      const r = await cek(l.kode, false);
      if(r.valid){ Object.assign(l, { dicek: Date.now(), kedaluwarsa: r.kedaluwarsa }); tulis(o.kunci, l); return { aktif:true, lisensi:l }; }
      if(r.jaringan && umurJam < o.masaTenggangHari * 24 && berlaku(l)) return { aktif:true, lisensi:l, peringatan:'Lagi offline. Lisensi dicek ulang saat online.' };
      hapus(o.kunci);
      return { aktif:false, pesan:r.pesan };
    },
    async aktifkan(email, kode){
      kode = String(kode || '').trim();
      if(kode.length < 6) return { valid:false, pesan:'Kode lisensi belum lengkap.' };
      const r = await cek(kode, true);
      if(r.valid) tulis(o.kunci, { kode, email: String(email || '').trim(), kedaluwarsa: r.kedaluwarsa, dicek: Date.now() });
      return r;
    },
    async lepas(){
      const l = baca(o.kunci, null);
      hapus(o.kunci);
      if(l && l.kode && o.productId) await panggil('deactivate', dasar(l.kode)).catch(() => {});
    }
  };
}
