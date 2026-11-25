#!/usr/bin/env node
// Sinkron katalog/produk.json ke Revo.id lalu tanam revo_product_id ke tiap aplikasi.
//   REVO_API_KEY=rv_test_... node tools/revo-sync.mjs           # jalankan
//   node tools/revo-sync.mjs --dry                              # lihat rencana saja
// Produk baru dibuat berstatus "draft" dengan lisensi aktif. Catatan dari uji sandbox 2026-11-25:
// - license_enabled & license_activations HANYA bisa diset saat produk dibuat (update mengabaikannya).
// - Produk draft tidak bisa di-checkout (422 checkout_status), juga di sandbox.
// - Produk tidak terpisah sandbox/live: key rv_test_ pun membuat produk di toko asli.
import fs from 'node:fs';
import path from 'node:path';
import { createRevoClient } from './revo-client.mjs';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const FILE = path.join(ROOT, 'katalog/produk.json');
const dry = process.argv.includes('--dry');
const pilih = process.argv.slice(2).filter((a) => !a.startsWith('--'));   // opsional: slug tertentu saja

// 1 toko Revo = 1 situs. Tiap entri katalog boleh punya key_env sendiri (API key toko itu).
function keyUntuk(p) {
  return (p.key_env && process.env[p.key_env]) || process.env.REVO_API_KEY || process.env.sandbox;
}
const klien = new Map();   // key -> { revo, byTitle }
async function tokoUntuk(apiKey) {
  if (!klien.has(apiKey)) {
    const revo = createRevoClient({ apiKey });
    const ada = await revo.listProducts('all');
    klien.set(apiKey, { revo, byTitle: new Map((Array.isArray(ada) ? ada : []).map((x) => [x.title, x])) });
    if (apiKey.startsWith('rv_live_')) console.warn('PERINGATAN: memakai key LIVE, produk dibuat di toko sungguhan.');
  }
  return klien.get(apiKey);
}

const katalog = JSON.parse(fs.readFileSync(FILE, 'utf8'));

for (const p of katalog.produk) {
  if (pilih.length && !pilih.includes(p.slug)) continue;
  const domain = p.domain || p.subdomain;
  const data = { type: 'digital', title: p.judul, price: p.harga, description: p.deskripsi, access_url: `https://${domain}`, status: 'draft' };
  const lisensi = { license_enabled: true, license_activations: p.batas_perangkat ?? 3 };
  if (dry) { console.log(`[dry] ${p.revo_product_id ? 'update #' + p.revo_product_id : 'buat baru'}: ${p.judul} (Rp${p.harga}) · key ${p.key_env || 'REVO_API_KEY'}${keyUntuk(p) ? '' : ' (BELUM ADA)'}`); continue; }
  const apiKey = keyUntuk(p);
  if (!apiKey) { console.error(`LEWATI ${p.slug}: isi ${p.key_env || 'REVO_API_KEY'} dulu.`); process.exitCode = 1; continue; }
  const { revo, byTitle } = await tokoUntuk(apiKey);
  let hasil;
  if (p.revo_product_id) {
    const { status, ...ubah } = data; // jangan menurunkan produk aktif ke draft
    hasil = await revo.updateProduct(p.revo_product_id, ubah);
  } else if (byTitle.has(p.judul)) {
    hasil = byTitle.get(p.judul);
  } else {
    hasil = await revo.createProduct({ ...data, ...lisensi });
  }
  if (hasil.license_enabled === false) {
    console.error(`GAGAL ${p.slug}: produk #${hasil.id} tanpa lisensi, dan ini tidak bisa diubah lewat API. Ganti judulnya / hapus di dashboard, kosongkan revo_product_id, lalu jalankan ulang.`);
    process.exitCode = 1;
    continue;
  }
  p.revo_product_id = hasil.id;
  console.log(`OK ${p.slug} -> produk Revo #${hasil.id}`);

  const app = path.join(ROOT, p.folder, 'index.html');
  if (fs.existsSync(app)) {
    const html = fs.readFileSync(app, 'utf8');
    let baru = html.replace(/revoProductId:\s*'[^']*'/, `revoProductId: '${hasil.id}'`);
    if (hasil.url) baru = baru.replace(/linkBeli:\s*'[^']*'/, `linkBeli: '${hasil.url}'`);
    if (baru !== html) { fs.writeFileSync(app, baru); console.log(`   revoProductId + linkBeli ditanam ke ${p.folder}/index.html`); }
  }
}
if (!dry) fs.writeFileSync(FILE, JSON.stringify(katalog, null, 2) + '\n');
