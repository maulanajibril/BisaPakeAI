# BisaPakeAI

Seri aplikasi HTML BisaPakeAI oleh **CV. Mewlanet Kreator Digital**.

| Seri | Subdomain | Folder |
|---|---|---|
| Mimin — Social Media Management & Corporate Content Creator | mimin.bisapakeai.com | [`mimin/`](mimin/) |
| Worksheet Anak — generator lembar kerja siap cetak | worksheetanak.net | [`situs/worksheetanak.net/`](situs/worksheetanak.net/) |
| Excel Cepat — 8 template Excel UMKM + perakit rumus | excelcepat.com | [`situs/excelcepat.com/`](situs/excelcepat.com/) |
| Hisab Rejeki — catatan keuangan keluarga + kalkulator zakat | hisabrejeki.com | [`situs/hisabrejeki.com/`](situs/hisabrejeki.com/) |

---

## Mimin

Satu file HTML statis (`mimin/index.html`), tanpa build dan tanpa server sendiri. Pengguna mengaktifkan lisensi dari bisapakeai.com, mengisi profil brand sekali, lalu memakai alat-alat di bawah. Setiap alat meracik prompt lengkap (profil brand + tugas + format jawaban + aturan) yang tinggal disalin atau dibuka langsung di Claude, ChatGPT, atau Gemini.

### Alat

| No | Alat | Isi |
|---|---|---|
| 01 | Kalender Konten | Rencana posting sebulan, pilih momen per bulan (hari besar & tanggal kembar) |
| 02 | Caption Siap Posting | Beberapa versi caption, pilihan formula (AIDA, PAS, BAB, dll.) |
| 03 | Naskah Reels / TikTok | Hook 3 detik, tabel adegan per detik, shot list |
| 04 | Carousel Edukasi | Isi dan arahan visual per slide |
| 05 | Bank Ide Konten | 20–50 ide per pilar |
| 06 | Balas Netizen | Balasan komplain, pertanyaan, komentar negatif, DM |
| 07 | Mode Krisis | Langkah 24 jam, pernyataan resmi, template balasan |
| 08 | Daur Ulang Konten | Satu materi jadi banyak konten lintas platform |
| 09 | Hashtag & Kata Kunci | Set hashtag + kata kunci pencarian |
| 10 | Iklan Berbayar | Copy Meta/TikTok/Google Ads + rencana uji A/B |
| 11 | Brief Desain & Prompt Gambar | Brief desainer + prompt AI gambar |
| 12 | Bedah Kompetitor | Analisis dari data yang ditempel admin |
| 13 | Laporan Bulanan | Laporan insight untuk atasan/klien |
| 14 | Kalkulator Engagement | Dihitung di browser (tanpa AI) |
| 15 | Cek Panjang Caption | Batas karakter & titik terpotong per platform |

Fitur pendukung: banyak profil brand (untuk admin yang pegang beberapa klien) dengan ekspor/impor JSON, riwayat 30 prompt terakhir, tema terang/gelap, tampilan HP. Semua data pengguna disimpan di `localStorage` browser masing-masing.

### Pasang di mimin.bisapakeai.com

1. Arahkan subdomain `mimin.bisapakeai.com` ke hosting statis (folder di cPanel, Cloudflare Pages, Netlify, Vercel, dll.).
2. Unggah `mimin/index.html` sebagai `index.html` di root subdomain.
3. Pastikan `IZINKAN_DEMO: false` di blok `LISENSI` (bawaan sudah `false`).

### Menyambungkan lisensi WordPress

Pengaturannya ada di bagian atas `<script>` dalam `mimin/index.html`:

```js
const LISENSI = {
  mode: 'custom',   // atau 'edd'
  endpoint: 'https://bisapakeai.com/wp-json/bisapakeai/v1/lisensi/cek',
  produk: 'mimin',
  ...
};
```

**Bawaan sekarang: mode `revo`** (lihat bagian *Lisensi lewat Revo.id* di bawah). Mode lama tetap tersedia:

**`custom`** — aplikasi mengirim `POST` JSON ke `endpoint`:

```json
{ "license_key": "XXXX-XXXX", "email": "nama@email.com", "product": "mimin", "domain": "mimin.bisapakeai.com", "device": "uuid-perangkat" }
```

Respons yang dikenali (salah satu bentuk ini cukup):

```json
{ "valid": true, "expires_at": "2027-10-17", "name": "Nama Pembeli" }
{ "valid": false, "message": "Kode lisensi tidak ditemukan." }
{ "success": true, "data": { "status": "active", "expires_at": "2027-10-17" } }
```

**`edd`** — Easy Digital Downloads Software Licensing. Isi `eddSitus` dan `eddItemId`; aplikasi memanggil `GET {eddSitus}/?edd_action=check_license&license=...&item_id=...&url=...` dan membaca field `license` (`valid`, `expired`, `site_inactive`, dst.). Ganti `eddAksi` ke `activate_license` kalau setiap perangkat harus diaktifkan.

Kalau format respons seri Guru berbeda, cukup ubah fungsi `bacaRespons()`.

**CORS:** karena aplikasi berjalan di subdomain `mimin.`, endpoint di `bisapakeai.com` harus mengizinkan origin `https://mimin.bisapakeai.com` (header `Access-Control-Allow-Origin`, dan untuk mode `custom` juga menjawab preflight `OPTIONS` dengan `Access-Control-Allow-Headers: Content-Type`).

**Perilaku cek lisensi**

- Setelah aktif, lisensi disimpan di browser dan dicek ulang ke server setiap `cekUlangJam` (bawaan 24 jam).
- Kalau server tidak terjangkau, aplikasi tetap bisa dipakai selama `masaTenggangHari` (bawaan 7 hari) sejak cek terakhir yang berhasil.
- Kalau server menyatakan lisensi tidak valid atau kedaluwarsa, pengguna dikembalikan ke layar aktivasi.
- Pengguna bisa melepas lisensi dari perangkat lewat tautan "Lepas lisensi" di footer.

Catatan: pengecekan di aplikasi HTML statis berjalan di browser, jadi orang yang paham teknis tetap bisa mengakalinya. Yang benar-benar melindungi adalah server: batasi jumlah aktivasi/perangkat per lisensi di WordPress.

### Uji lokal

Set `IZINKAN_DEMO: true`, jalankan server lokal (misal `python3 -m http.server` di folder `mimin/`), lalu buka `http://localhost:8000/?demo` untuk melewati lisensi. Kembalikan ke `false` sebelum diunggah.

---

## Lisensi lewat Revo.id

Alur jual tiap seri: pembeli bayar di checkout Revo (QRIS / VA), lalu Revo menerbitkan kode lisensi dan mengirimnya ke email pembeli. Di aplikasi, kode itu diaktifkan langsung ke Revo. Di browser tidak ada API key, karena kredensialnya adalah kode lisensi itu sendiri (lihat [docs/revo-api.md](docs/revo-api.md)).

| Kejadian | Panggilan ke `https://revo.id/api/v1` |
|---|---|
| Pengguna menekan **Aktifkan** | `POST /licenses/activate` `{license_key, product_id, instance, label}` |
| Cek ulang tiap `cekUlangJam` | `POST /licenses/validate`. Kalau `reason = instance_not_activated`, aplikasi otomatis mencoba aktivasi sekali |
| **Lepas lisensi** | `POST /licenses/deactivate`, supaya slot perangkat kembali kosong |

`instance` = ID acak per perangkat, sehingga batas perangkat (`max_activations`) yang diatur di Revo berlaku. Masa tenggang offline tetap mengikuti `masaTenggangHari`.

### Langkah pasang

1. Di dashboard Revo, buat produk **digital** untuk seri ini, nyalakan lisensinya, lalu atur batas perangkat (misal 3). Cara lainnya: jalankan skrip sinkron di bawah, lalu nyalakan lisensinya di dashboard.
2. Isi `revoProductId` di blok `LISENSI` (`mimin/index.html`) dengan ID produk tersebut, dan isi `linkBeli` dengan link checkout produknya.
3. Unggah seperti biasa.

### Skrip sinkron katalog → Revo

`katalog/produk.json` berisi daftar semua seri (satu entri = satu produk Revo). Skrip ini membuat produk yang belum ada (berstatus **draft**), memperbarui produk yang sudah ada, lalu menanam `revoProductId` ke `index.html` setiap seri:

```bash
node tools/revo-sync.mjs --dry                     # lihat rencana
REVO_API_KEY=rv_test_xxx node tools/revo-sync.mjs  # sandbox dulu
```

Butuh Node 20+ dan tidak memerlukan dependensi tambahan. Key hanya dipakai di komputer/server kamu, jangan pernah dimasukkan ke HTML.

### Belum terverifikasi

- **CORS**: dokumentasi Revo tidak menyebut apakah `/licenses/*` boleh dipanggil dari domain lain. Kalau browser menolak, sediakan proxy kecil (misal Cloudflare Worker) di subdomain sendiri, lalu arahkan `revoApi` ke proxy itu.
- Field untuk menyalakan lisensi saat `POST /products` tidak didokumentasikan, jadi lisensi dinyalakan manual di dashboard.
- Uji ke sandbox Revo yang sebenarnya belum dilakukan. Alurnya baru diuji dengan server tiruan.

---

## Situs per domain (`situs/<domain>/`)

Setiap domain punya satu situs statis: landing page dan aplikasinya ada di **satu** `index.html`. Pembelian lewat checkout Revo, lalu aplikasi dibuka dengan kode lisensi Revo. **1 situs = 1 toko (halaman kreator) Revo.**

```
_inti/lisensi-revo.js      modul lisensi Revo bersama (activate/validate/deactivate)
situs/<domain>/index.html  sumber situs, berisi <!-- SISIP:_inti/lisensi-revo.js -->
dist/<domain>/index.html   hasil rakit, file inilah yang diunggah
tools/build.mjs            node tools/build.mjs [domain...]
```

### Menambah toko Revo untuk satu situs
1. Di dashboard Revo, buat halaman kreator/toko baru untuk domain itu.
2. Di toko itu buka **Developer**, buat API key, lalu simpan sebagai variabel dengan nama yang ada di kolom `key_env` katalog (misal `REVO_KEY_WORKSHEETANAK`). Simpan di secret atau `.env`, **jangan di-commit**.
3. Jalankan `node tools/revo-sync.mjs worksheetanak`. Skrip ini membuat produk (draft, lisensi aktif) di toko itu, lalu menanam `revoProductId` dan `linkBeli` ke `situs/<domain>/index.html`.
4. Isi `linkToko` di blok `SITUS` dengan URL halaman toko Revo-nya.
5. `node tools/build.mjs`, lalu aktifkan produknya di dashboard Revo saat siap dijual.

### Pasang di cPanel
1. **Domains → Create a New Domain** (addon domain), misal `worksheetanak.net`, dengan document root `public_html/worksheetanak.net`.
2. Unggah `dist/worksheetanak.net/index.html` ke folder tersebut lewat File Manager.
3. Aktifkan SSL (AutoSSL / Let's Encrypt) untuk domain itu.

Tidak butuh PHP, database, atau proxy, karena endpoint lisensi Revo mengizinkan CORS dari domain mana pun (sudah diuji di sandbox).

### Excel Cepat: membuat ulang template
Template `.xlsx` dibuat oleh `python3 tools/excelcepat/buat-template.py` (butuh `openpyxl`). Skrip ini menulis file ke `situs/excelcepat.com/_berkas/` dan `_berkas.js` (base64), yang disisipkan ke halaman saat `node tools/build.mjs`. Tombol unduh hanya muncul setelah lisensi aktif.

Catatan: file ditanam di HTML. Orang yang paham teknis bisa mengambilnya lewat view-source, sama seperti semua pengecekan lisensi di browser. Untuk produk murah ini masih wajar. Kalau ingin lebih ketat, lampirkan file langsung di produk Revo, sehingga Revo yang mengirimkannya ke pembeli.
