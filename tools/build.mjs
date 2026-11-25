#!/usr/bin/env node
// Rakit situs statis: situs/<domain>/index.html -> dist/<domain>/index.html
// Baris `<!-- SISIP:_inti/nama-file.js -->` diganti isi file itu dalam <script>.
// Hasil di dist/<domain>/ tinggal diunggah ke folder addon domain di cPanel.
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const pilih = process.argv.slice(2);
const situs = fs.readdirSync(path.join(ROOT, 'situs')).filter((d) => !pilih.length || pilih.includes(d));
for (const d of situs) {
  const src = path.join(ROOT, 'situs', d);
  const out = path.join(ROOT, 'dist', d);
  fs.rmSync(out, { recursive: true, force: true });
  fs.cpSync(src, out, { recursive: true });
  const f = path.join(out, 'index.html');
  const html = fs.readFileSync(f, 'utf8').replace(/<!--\s*SISIP:([\w./-]+)\s*-->/g, (_, rel) => {
    const isi = fs.readFileSync(path.join(ROOT, rel), 'utf8');
    return `<script>\n${isi}\n</script>`;
  });
  fs.writeFileSync(f, html);
  console.log(`dist/${d}/index.html (${(html.length / 1024).toFixed(1)} KB)`);
}
