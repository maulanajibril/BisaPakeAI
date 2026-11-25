#!/usr/bin/env node
// Sinkron katalog/produk.json ke Revo.id lalu tanam revo_product_id ke tiap aplikasi.
//   REVO_API_KEY=rv_test_... node tools/revo-sync.mjs           # jalankan
//   node tools/revo-sync.mjs --dry                              # lihat rencana saja
// Produk baru dibuat berstatus "draft". Aktifkan lisensi & batas perangkat di dashboard Revo.
import fs from 'node:fs';
import path from 'node:path';
import { createRevoClient } from './revo-client.mjs';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const FILE = path.join(ROOT, 'katalog/produk.json');
const dry = process.argv.includes('--dry');
const apiKey = process.env.REVO_API_KEY || process.env.sandbox;

const katalog = JSON.parse(fs.readFileSync(FILE, 'utf8'));
if (!dry && !apiKey) { console.error('Isi REVO_API_KEY (atau variabel sandbox) dulu, atau pakai --dry.'); process.exit(1); }
if (apiKey && apiKey.startsWith('rv_live_')) console.warn('PERINGATAN: memakai key LIVE, produk dibuat di toko sungguhan.');

const revo = dry ? null : createRevoClient({ apiKey });
const ada = dry ? [] : await revo.listProducts('all');
const byTitle = new Map((Array.isArray(ada) ? ada : []).map((p) => [p.title, p]));

for (const p of katalog.produk) {
  const data = { type: 'digital', title: p.judul, price: p.harga, description: p.deskripsi, access_url: `https://${p.subdomain}`, status: 'draft' };
  if (dry) { console.log(`[dry] ${p.revo_product_id ? 'update #' + p.revo_product_id : 'buat baru'}: ${p.judul} (Rp${p.harga})`); continue; }
  let hasil;
  if (p.revo_product_id) {
    const { status, ...ubah } = data; // jangan menurunkan produk aktif ke draft
    hasil = await revo.updateProduct(p.revo_product_id, ubah);
  } else if (byTitle.has(p.judul)) {
    hasil = byTitle.get(p.judul);
  } else {
    hasil = await revo.createProduct(data);
  }
  p.revo_product_id = hasil.id;
  console.log(`OK ${p.slug} -> produk Revo #${hasil.id}`);

  const app = path.join(ROOT, p.folder, 'index.html');
  if (fs.existsSync(app)) {
    const html = fs.readFileSync(app, 'utf8');
    const baru = html.replace(/revoProductId:\s*'[^']*'/, `revoProductId: '${hasil.id}'`);
    if (baru !== html) { fs.writeFileSync(app, baru); console.log(`   revoProductId ditanam ke ${p.folder}/index.html`); }
  }
}
if (!dry) fs.writeFileSync(FILE, JSON.stringify(katalog, null, 2) + '\n');
