#!/usr/bin/env python3
"""Membuat template Excel UMKM untuk excelcepat.com.

    python3 tools/excelcepat/buat-template.py

Hasil: situs/excelcepat.com/_berkas/*.xlsx dan situs/excelcepat.com/_berkas.js
(berisi file dalam base64, disisipkan ke index.html oleh tools/build.mjs).
Semua rumus memakai fungsi yang ada di Excel 2010+ dan Google Sheets (tanpa XLOOKUP).
"""
import base64, json, os, datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.utils import get_column_letter as kol

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'situs', 'excelcepat.com', '_berkas')
os.makedirs(OUT, exist_ok=True)

HIJAU = '1F6F50'; MUDA = 'E8F3EE'; KUNING = 'FFF4CC'; MERAH = 'FDE2DC'; ABU = 'F4F4F4'
RP = '"Rp"#,##0;[Red]-"Rp"#,##0'
TGL = 'dd/mm/yyyy'
tipis = Side(style='thin', color='D0D7D3')
KOTAK = Border(left=tipis, right=tipis, top=tipis, bottom=tipis)
HARI = dt.date(2026, 11, 2)


def judul(ws, teks, sub, lebar_kolom):
    ws['A1'] = teks; ws['A1'].font = Font(bold=True, size=16, color=HIJAU)
    ws['A2'] = sub; ws['A2'].font = Font(italic=True, size=10, color='666666')
    for i, w in enumerate(lebar_kolom, 1):
        ws.column_dimensions[kol(i)].width = w
    ws.sheet_view.showGridLines = False


def kepala(ws, baris, kolom):
    for i, t in enumerate(kolom, 1):
        c = ws.cell(row=baris, column=i, value=t)
        c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor=HIJAU)
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True); c.border = KOTAK
    ws.row_dimensions[baris].height = 30
    ws.freeze_panes = ws.cell(row=baris + 1, column=1)


def gaya(ws, r1, r2, c1, c2, fmt=None, isian=False, warna=None):
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            cell = ws.cell(row=r, column=c); cell.border = KOTAK
            if fmt: cell.number_format = fmt
            if warna: cell.fill = PatternFill('solid', fgColor=warna)
            elif isian: cell.fill = PatternFill('solid', fgColor='FFFFFF')
            else: cell.fill = PatternFill('solid', fgColor=ABU)


def petunjuk(wb, baris):
    ws = wb.create_sheet('Petunjuk', 0)
    ws.column_dimensions['A'].width = 100; ws.sheet_view.showGridLines = False
    ws['A1'] = 'Cara memakai template ini'; ws['A1'].font = Font(bold=True, size=16, color=HIJAU)
    for i, t in enumerate(baris + [
        '',
        'Kolom berlatar PUTIH diisi manual. Kolom berlatar ABU-ABU berisi rumus, jangan diketik ulang.',
        'Baris contoh boleh dihapus isinya (bukan barisnya), lalu ganti dengan data Anda.',
        'Template ini bisa dibuka di Microsoft Excel 2010 ke atas, Google Sheets, dan WPS Office.',
        '© excelcepat.com — untuk dipakai sendiri/usaha sendiri. Dilarang dijual ulang.'], 3):
        ws.cell(row=i, column=1, value=t).alignment = Alignment(wrap_text=True, vertical='top')
    return ws


def validasi_list(ws, rng, pilihan):
    dv = DataValidation(type='list', formula1='"' + ','.join(pilihan) + '"', allow_blank=True)
    ws.add_data_validation(dv); dv.add(rng)


# ---------------------------------------------------------------- 1. Buku kas
def buku_kas():
    wb = Workbook(); ws = wb.active; ws.title = 'Kas'
    judul(ws, 'Buku Kas Harian', 'Catat setiap uang masuk dan keluar. Saldo dihitung otomatis.', [13, 38, 18, 16, 16, 18])
    ws['E3'] = 'Saldo awal'; ws['E3'].font = Font(bold=True); ws['F3'] = 2000000; ws['F3'].number_format = RP
    gaya(ws, 3, 3, 6, 6, RP, isian=True)
    kepala(ws, 5, ['Tanggal', 'Keterangan', 'Kategori', 'Masuk', 'Keluar', 'Saldo'])
    kat = ['Penjualan', 'Modal', 'Bahan baku', 'Gaji', 'Sewa', 'Listrik & air', 'Transport', 'Promosi', 'Lain-lain']
    contoh = [(0, 'Penjualan tunai', 'Penjualan', 850000, None), (0, 'Beli tepung & gula', 'Bahan baku', None, 320000),
              (1, 'Transfer pelanggan', 'Penjualan', 1250000, None), (1, 'Bensin antar pesanan', 'Transport', None, 50000),
              (2, 'Iklan Instagram', 'Promosi', None, 150000), (3, 'Bayar listrik', 'Listrik & air', None, 275000)]
    N = 300
    for i in range(N):
        r = 6 + i
        if i < len(contoh):
            d, ket, k, m, kl = contoh[i]
            ws.cell(row=r, column=1, value=HARI + dt.timedelta(days=d)); ws.cell(row=r, column=2, value=ket)
            ws.cell(row=r, column=3, value=k); ws.cell(row=r, column=4, value=m); ws.cell(row=r, column=5, value=kl)
        ws.cell(row=r, column=6, value=f'=IF(AND(D{r}="",E{r}=""),"",$F$3+SUM($D$6:D{r})-SUM($E$6:E{r}))')
    gaya(ws, 6, 5 + N, 1, 5, isian=True); gaya(ws, 6, 5 + N, 6, 6, RP)
    for r in range(6, 6 + N):
        ws.cell(row=r, column=1).number_format = TGL
        for c in (4, 5): ws.cell(row=r, column=c).number_format = RP
    validasi_list(ws, f'C6:C{5+N}', kat)

    rk = wb.create_sheet('Rekap')
    judul(rk, 'Rekap per Kategori', 'Isi bulan & tahun, rekap terhitung otomatis dari sheet Kas.', [22, 18, 18])
    rk['A3'] = 'Bulan (1-12)'; rk['B3'] = 11; rk['A4'] = 'Tahun'; rk['B4'] = 2026
    gaya(rk, 3, 4, 2, 2, isian=True)
    kepala(rk, 6, ['Kategori', 'Masuk', 'Keluar'])
    awal = 'DATE($B$4,$B$3,1)'; akhir = 'EOMONTH(DATE($B$4,$B$3,1),0)'
    for i, k in enumerate(kat):
        r = 7 + i; rk.cell(row=r, column=1, value=k)
        for c, col in ((2, 'D'), (3, 'E')):
            rk.cell(row=r, column=c, value=f'=SUMIFS(Kas!${col}$6:${col}${5+N},Kas!$C$6:$C${5+N},$A{r},Kas!$A$6:$A${5+N},">="&{awal},Kas!$A$6:$A${5+N},"<="&{akhir})')
    rt = 7 + len(kat)
    rk.cell(row=rt, column=1, value='TOTAL').font = Font(bold=True)
    rk.cell(row=rt, column=2, value=f'=SUM(B7:B{rt-1})'); rk.cell(row=rt, column=3, value=f'=SUM(C7:C{rt-1})')
    rk.cell(row=rt + 1, column=1, value='Laba / (rugi) bulan ini').font = Font(bold=True)
    rk.cell(row=rt + 1, column=2, value=f'=B{rt}-C{rt}')
    gaya(rk, 7, rt + 1, 1, 1, isian=True); gaya(rk, 7, rt + 1, 2, 3, RP)
    petunjuk(wb, ['1. Isi saldo awal di sheet Kas (sel F3).',
                  '2. Setiap transaksi: isi tanggal, keterangan, pilih kategori, lalu isi kolom Masuk ATAU Keluar.',
                  '3. Saldo berjalan dihitung otomatis.',
                  '4. Sheet Rekap: ganti bulan & tahun untuk melihat total per kategori dan laba/rugi.'])
    return wb


# ---------------------------------------------------------------- 2. Stok
def stok():
    wb = Workbook(); m = wb.active; m.title = 'Barang'
    judul(m, 'Daftar Barang & Stok', 'Stok akhir dihitung dari stok awal + barang masuk − barang keluar di sheet Mutasi.', [12, 30, 10, 12, 12, 12, 12, 16])
    kepala(m, 4, ['Kode', 'Nama barang', 'Satuan', 'Stok awal', 'Min. stok', 'Masuk', 'Keluar', 'Stok akhir'])
    brg = [('B001', 'Tepung terigu', 'kg', 25, 10), ('B002', 'Gula pasir', 'kg', 15, 8), ('B003', 'Mentega', 'kg', 6, 4),
           ('B004', 'Telur', 'butir', 120, 60), ('B005', 'Kemasan box', 'pcs', 200, 100)]
    N, NM = 150, 500
    for i in range(N):
        r = 5 + i
        if i < len(brg):
            for c, v in enumerate(brg[i], 1): m.cell(row=r, column=c, value=v)
        m.cell(row=r, column=6, value=f'=IF($A{r}="","",SUMIFS(Mutasi!$E$5:$E${4+NM},Mutasi!$B$5:$B${4+NM},$A{r},Mutasi!$D$5:$D${4+NM},"Masuk"))')
        m.cell(row=r, column=7, value=f'=IF($A{r}="","",SUMIFS(Mutasi!$E$5:$E${4+NM},Mutasi!$B$5:$B${4+NM},$A{r},Mutasi!$D$5:$D${4+NM},"Keluar"))')
        m.cell(row=r, column=8, value=f'=IF($A{r}="","",D{r}+F{r}-G{r})')
    gaya(m, 5, 4 + N, 1, 5, isian=True); gaya(m, 5, 4 + N, 6, 8)
    m.conditional_formatting.add(f'H5:H{4+N}', FormulaRule(formula=[f'AND($A5<>"",$H5<=$E5)'], fill=PatternFill('solid', fgColor=MERAH), font=Font(bold=True, color='8A2410')))
    mt = wb.create_sheet('Mutasi')
    judul(mt, 'Mutasi Barang', 'Isi setiap barang masuk (beli) dan keluar (terpakai/terjual). Nama terisi otomatis dari kode.', [13, 10, 30, 10, 10, 30])
    kepala(mt, 4, ['Tanggal', 'Kode', 'Nama barang', 'Jenis', 'Jumlah', 'Catatan'])
    mut = [(0, 'B001', 'Masuk', 20, 'Beli di toko A'), (0, 'B004', 'Keluar', 45, 'Produksi'), (1, 'B001', 'Keluar', 18, 'Produksi'), (2, 'B003', 'Keluar', 3, 'Produksi')]
    for i in range(NM):
        r = 5 + i
        if i < len(mut):
            d, k, j, q, c = mut[i]
            mt.cell(row=r, column=1, value=HARI + dt.timedelta(days=d)); mt.cell(row=r, column=2, value=k)
            mt.cell(row=r, column=4, value=j); mt.cell(row=r, column=5, value=q); mt.cell(row=r, column=6, value=c)
        mt.cell(row=r, column=3, value=f'=IF(B{r}="","",IFERROR(INDEX(Barang!$B$5:$B${4+N},MATCH(B{r},Barang!$A$5:$A${4+N},0)),"Kode tidak ada"))')
        mt.cell(row=r, column=1).number_format = TGL
    gaya(mt, 5, 4 + NM, 1, 2, isian=True); gaya(mt, 5, 4 + NM, 3, 3); gaya(mt, 5, 4 + NM, 4, 6, isian=True)
    for r in range(5, 5 + NM): mt.cell(row=r, column=1).number_format = TGL
    validasi_list(mt, f'D5:D{4+NM}', ['Masuk', 'Keluar'])
    petunjuk(wb, ['1. Sheet Barang: daftarkan semua barang dengan kode unik, stok awal, dan batas minimum.',
                  '2. Sheet Mutasi: setiap barang datang pilih "Masuk", setiap terpakai/terjual pilih "Keluar".',
                  '3. Stok akhir di sheet Barang dihitung otomatis. Baris berwarna merah artinya stok sudah di bawah batas minimum: saatnya belanja.'])
    return wb


# ---------------------------------------------------------------- 3. Invoice
def invoice():
    wb = Workbook(); ws = wb.active; ws.title = 'Invoice'
    judul(ws, 'INVOICE', 'Ganti logo/nama usaha, isi item, total terhitung otomatis. Cetak atau simpan PDF.', [6, 40, 10, 18, 20])
    isi = [('A4', 'Nama usaha Anda'), ('A5', 'Alamat · No. WA · Email'), ('D4', 'No. invoice'), ('E4', 'INV-2026-001'),
           ('D5', 'Tanggal'), ('E5', HARI), ('D6', 'Jatuh tempo'), ('E6', '=E5+14'), ('A8', 'Kepada:'), ('B8', 'Nama pelanggan'), ('B9', 'Alamat pelanggan')]
    for a, v in isi: ws[a] = v
    ws['A4'].font = Font(bold=True, size=13); ws['E5'].number_format = TGL; ws['E6'].number_format = TGL; ws['A8'].font = Font(bold=True)
    gaya(ws, 4, 6, 5, 5, isian=True); ws['E6'].fill = PatternFill('solid', fgColor=ABU)
    kepala(ws, 11, ['No', 'Deskripsi', 'Qty', 'Harga satuan', 'Jumlah'])
    ws.freeze_panes = None
    item = [('Kue lapis legit 20x20', 2, 350000), ('Brownies panggang', 5, 85000), ('Ongkos kirim', 1, 30000)]
    for i in range(15):
        r = 12 + i
        ws.cell(row=r, column=1, value=f'=IF(B{r}="","",ROW()-11)')
        if i < len(item):
            for c, v in enumerate(item[i], 2): ws.cell(row=r, column=c, value=v)
        ws.cell(row=r, column=5, value=f'=IF(B{r}="","",C{r}*D{r})')
    gaya(ws, 12, 26, 1, 1); gaya(ws, 12, 26, 2, 4, isian=True); gaya(ws, 12, 26, 5, 5, RP)
    for r in range(12, 27): ws.cell(row=r, column=4).number_format = RP
    rows = [('Subtotal', '=SUM(E12:E26)'), ('Diskon (%)', 0), ('PPN (%) — isi 0 jika tidak PKP', 0),
            ('Diskon', '=E28*E29/100'), ('PPN', '=(E28-E31)*E30/100'), ('TOTAL', '=E28-E31+E32'), ('Sudah dibayar (DP)', 0), ('SISA TAGIHAN', '=E33-E34')]
    for i, (l, v) in enumerate(rows):
        r = 28 + i; ws.cell(row=r, column=4, value=l).alignment = Alignment(horizontal='right', wrap_text=True); ws.cell(row=r, column=5, value=v)
        ws.cell(row=r, column=5).number_format = '0' if '(%)' in l else RP; ws.cell(row=r, column=5).border = KOTAK
        ws.cell(row=r, column=5).fill = PatternFill('solid', fgColor='FFFFFF' if isinstance(v, int) else ABU)
    for r in (33, 35): ws.cell(row=r, column=4).font = Font(bold=True); ws.cell(row=r, column=5).font = Font(bold=True, size=12)
    ws['A38'] = 'Pembayaran ke: Bank ... a.n. ... No. rek ...'; ws['A39'] = 'Terima kasih atas kepercayaan Anda.'
    ws.print_area = 'A1:E39'; ws.page_setup.paperSize = ws.PAPERSIZE_A4; ws.page_setup.fitToWidth = 1
    petunjuk(wb, ['1. Ganti nama usaha, alamat, dan rekening.', '2. Isi deskripsi, qty, dan harga per item. Jumlah dan total terhitung otomatis.',
                  '3. Isi persen diskon / PPN bila ada. PPN hanya untuk usaha yang sudah PKP.',
                  '4. Untuk invoice berikutnya: klik kanan tab "Invoice" → Pindahkan atau Salin → centang Buat salinan.'])
    return wb


# ---------------------------------------------------------------- 4. Gaji
def gaji():
    wb = Workbook(); ws = wb.active; ws.title = 'Gaji'
    judul(ws, 'Daftar Gaji Karyawan', 'Isi komponen gaji per karyawan. Total dihitung otomatis. Slip ada di sheet berikutnya.', [24, 16, 16, 16, 10, 14, 16, 16, 18])
    kepala(ws, 4, ['Nama', 'Jabatan', 'Gaji pokok', 'Tunjangan', 'Jam lembur', 'Tarif lembur/jam', 'Bonus', 'Potongan', 'Gaji bersih'])
    org = [('Siti Aminah', 'Kasir', 2500000, 300000, 6, 15000, 0, 100000), ('Budi Santoso', 'Produksi', 2700000, 250000, 10, 17000, 150000, 0), ('Rina Wulandari', 'Admin online', 2600000, 300000, 0, 15000, 200000, 50000)]
    N = 50
    for i in range(N):
        r = 5 + i
        if i < len(org):
            for c, v in enumerate(org[i], 1): ws.cell(row=r, column=c, value=v)
        ws.cell(row=r, column=9, value=f'=IF(A{r}="","",C{r}+D{r}+E{r}*F{r}+G{r}-H{r})')
    gaya(ws, 5, 4 + N, 1, 8, isian=True); gaya(ws, 5, 4 + N, 9, 9, RP)
    for r in range(5, 5 + N):
        for c in (3, 4, 6, 7, 8): ws.cell(row=r, column=c).number_format = RP
    ws.cell(row=5 + N, column=8, value='TOTAL').font = Font(bold=True)
    ws.cell(row=5 + N, column=9, value=f'=SUM(I5:I{4+N})').number_format = RP
    sl = wb.create_sheet('Slip')
    judul(sl, 'SLIP GAJI', 'Pilih nama karyawan di sel B4, slip terisi otomatis. Cetak lalu berikan ke karyawan.', [26, 24])
    sl['A3'] = 'Periode'; sl['B3'] = 'November 2026'; sl['A4'] = 'Nama karyawan'; sl['B4'] = 'Siti Aminah'
    gaya(sl, 3, 4, 2, 2, isian=True)
    dv = DataValidation(type='list', formula1=f'=Gaji!$A$5:$A${4+N}'); sl.add_data_validation(dv); dv.add('B4')
    kolom = [('Jabatan', 2, None), ('Gaji pokok', 3, RP), ('Tunjangan', 4, RP), ('Jam lembur', 5, '0'), ('Uang lembur', None, RP), ('Bonus', 7, RP), ('Potongan', 8, RP), ('GAJI BERSIH', 9, RP)]
    for i, (l, c, f) in enumerate(kolom):
        r = 6 + i; sl.cell(row=r, column=1, value=l)
        rumus = f'=IFERROR(INDEX(Gaji!$E$5:$E${4+N},MATCH($B$4,Gaji!$A$5:$A${4+N},0))*INDEX(Gaji!$F$5:$F${4+N},MATCH($B$4,Gaji!$A$5:$A${4+N},0)),"")' if c is None else f'=IFERROR(INDEX(Gaji!${kol(c)}$5:${kol(c)}${4+N},MATCH($B$4,Gaji!$A$5:$A${4+N},0)),"")'
        sl.cell(row=r, column=2, value=rumus)
        if f: sl.cell(row=r, column=2).number_format = f
    gaya(sl, 6, 13, 1, 2); sl['A13'].font = Font(bold=True); sl['B13'].font = Font(bold=True, size=12)
    sl['A16'] = 'Diterima oleh,'; sl['B16'] = 'Disetujui oleh,'
    petunjuk(wb, ['1. Sheet Gaji: isi data setiap karyawan. Gaji bersih = pokok + tunjangan + (jam lembur × tarif) + bonus − potongan.',
                  '2. Sheet Slip: pilih nama di sel B4, lalu cetak.',
                  '3. Template ini tidak menghitung PPh 21 dan BPJS. Bila wajib, masukkan nilainya ke kolom Potongan.'])
    return wb


# ---------------------------------------------------------------- 5. Anggaran
def anggaran():
    wb = Workbook(); ws = wb.active; ws.title = 'Anggaran'
    judul(ws, 'Anggaran Bulanan', 'Isi rencana di awal bulan, isi realisasi sepanjang bulan. Selisih & persen terhitung otomatis.', [28, 18, 18, 18, 12])
    ws['A3'] = 'Pemasukan bulan ini'; ws['B3'] = 8500000; ws['B3'].number_format = RP; gaya(ws, 3, 3, 2, 2, isian=True)
    kepala(ws, 5, ['Pos', 'Rencana', 'Realisasi', 'Sisa', '% terpakai'])
    pos = [('Kebutuhan dapur', 2500000, 2310000), ('Listrik, air, internet', 750000, 790000), ('Transportasi', 600000, 420000), ('Pendidikan anak', 1000000, 1000000),
           ('Cicilan', 1500000, 1500000), ('Kesehatan', 300000, 0), ('Zakat/infak/sedekah', 250000, 250000), ('Hiburan', 300000, 410000), ('Tabungan', 1000000, 1000000), ('Dana darurat', 300000, 300000)]
    N = 25
    for i in range(N):
        r = 6 + i
        if i < len(pos):
            for c, v in enumerate(pos[i], 1): ws.cell(row=r, column=c, value=v)
        ws.cell(row=r, column=4, value=f'=IF(A{r}="","",B{r}-C{r})'); ws.cell(row=r, column=5, value=f'=IF(OR(A{r}="",N(B{r})=0),"",C{r}/B{r})')
    gaya(ws, 6, 5 + N, 1, 3, isian=True); gaya(ws, 6, 5 + N, 4, 5)
    for r in range(6, 6 + N):
        for c in (2, 3, 4): ws.cell(row=r, column=c).number_format = RP
        ws.cell(row=r, column=5).number_format = '0%'
    ws.conditional_formatting.add(f'E6:E{5+N}', CellIsRule(operator='greaterThan', formula=['1'], fill=PatternFill('solid', fgColor=MERAH), font=Font(bold=True, color='8A2410')))
    rt = 6 + N
    ws.cell(row=rt, column=1, value='TOTAL').font = Font(bold=True)
    for c in (2, 3, 4): ws.cell(row=rt, column=c, value=f'=SUM({kol(c)}6:{kol(c)}{rt-1})').number_format = RP
    ws.cell(row=rt + 1, column=1, value='Pemasukan − rencana').font = Font(bold=True); ws.cell(row=rt + 1, column=2, value=f'=B3-B{rt}').number_format = RP
    ws.cell(row=rt + 2, column=1, value='Pemasukan − realisasi').font = Font(bold=True); ws.cell(row=rt + 2, column=2, value=f'=B3-C{rt}').number_format = RP
    petunjuk(wb, ['1. Isi pemasukan bulan ini di sel B3.', '2. Isi rencana per pos. Total rencana sebaiknya tidak melebihi pemasukan.',
                  '3. Tambahkan realisasi setiap ada pengeluaran. Pos yang melewati 100% akan berwarna merah.',
                  '4. Untuk bulan baru: salin sheet Anggaran, kosongkan kolom Realisasi.'])
    return wb


# ---------------------------------------------------------------- 6. Penjualan
def penjualan():
    wb = Workbook(); ws = wb.active; ws.title = 'Transaksi'
    judul(ws, 'Catatan Penjualan', 'Satu baris = satu transaksi. Rekap per produk & per channel otomatis.', [13, 26, 16, 8, 16, 18, 18])
    kepala(ws, 4, ['Tanggal', 'Produk', 'Channel', 'Qty', 'Harga', 'Total', 'Pelanggan'])
    ch = ['Offline', 'WhatsApp', 'Shopee', 'Tokopedia', 'TikTok Shop', 'GoFood', 'GrabFood']
    trx = [(0, 'Kopi susu gula aren', 'Offline', 3, 18000, 'Umum'), (0, 'Roti bakar', 'GoFood', 2, 22000, 'Andi'), (1, 'Kopi susu gula aren', 'GrabFood', 4, 18000, 'Dewi'),
           (1, 'Es teh jumbo', 'Offline', 6, 6000, 'Umum'), (2, 'Roti bakar', 'WhatsApp', 5, 22000, 'Kantor Maju'), (3, 'Kopi susu gula aren', 'Offline', 7, 18000, 'Umum')]
    N = 1000
    for i in range(N):
        r = 5 + i
        if i < len(trx):
            d, p, c, q, h, pl = trx[i]
            for col, v in ((1, HARI + dt.timedelta(days=d)), (2, p), (3, c), (4, q), (5, h), (7, pl)): ws.cell(row=r, column=col, value=v)
        ws.cell(row=r, column=6, value=f'=IF(B{r}="","",D{r}*E{r})')
    gaya(ws, 5, 4 + N, 1, 5, isian=True); gaya(ws, 5, 4 + N, 6, 6, RP); gaya(ws, 5, 4 + N, 7, 7, isian=True)
    for r in range(5, 5 + N): ws.cell(row=r, column=1).number_format = TGL; ws.cell(row=r, column=5).number_format = RP
    validasi_list(ws, f'C5:C{4+N}', ch)
    rk = wb.create_sheet('Rekap')
    judul(rk, 'Rekap Penjualan', 'Isi bulan & tahun. Daftar produk diketik sekali di kolom A.', [28, 10, 18, 4, 18, 18])
    rk['A3'] = 'Bulan (1-12)'; rk['B3'] = 11; rk['A4'] = 'Tahun'; rk['B4'] = 2026; gaya(rk, 3, 4, 2, 2, isian=True)
    syarat = f',Transaksi!$A$5:$A${4+N},">="&DATE($B$4,$B$3,1),Transaksi!$A$5:$A${4+N},"<="&EOMONTH(DATE($B$4,$B$3,1),0)'
    kepala(rk, 6, ['Produk', 'Qty', 'Omzet', '', 'Channel', 'Omzet'])
    rk.freeze_panes = None
    for i, p in enumerate(['Kopi susu gula aren', 'Roti bakar', 'Es teh jumbo'] + [None] * 12):
        r = 7 + i; rk.cell(row=r, column=1, value=p)
        rk.cell(row=r, column=2, value=f'=IF(A{r}="","",SUMIFS(Transaksi!$D$5:$D${4+N},Transaksi!$B$5:$B${4+N},A{r}{syarat}))')
        rk.cell(row=r, column=3, value=f'=IF(A{r}="","",SUMIFS(Transaksi!$F$5:$F${4+N},Transaksi!$B$5:$B${4+N},A{r}{syarat}))').number_format = RP
    gaya(rk, 7, 21, 1, 1, isian=True); gaya(rk, 7, 21, 2, 3, RP); [setattr(rk.cell(row=r, column=2), 'number_format', '0') for r in range(7, 22)]
    for i, c in enumerate(ch):
        r = 7 + i; rk.cell(row=r, column=5, value=c)
        rk.cell(row=r, column=6, value=f'=SUMIFS(Transaksi!$F$5:$F${4+N},Transaksi!$C$5:$C${4+N},E{r}{syarat})')
    gaya(rk, 7, 6 + len(ch), 5, 6, RP)
    rk.cell(row=23, column=1, value='TOTAL OMZET BULAN INI').font = Font(bold=True)
    rk.cell(row=23, column=3, value=f'=SUMIFS(Transaksi!$F$5:$F${4+N}{syarat})').number_format = RP
    petunjuk(wb, ['1. Sheet Transaksi: setiap penjualan isi tanggal, produk, channel, qty, harga.',
                  '2. Sheet Rekap: ketik nama produk di kolom A (harus sama persis dengan di Transaksi), lalu pilih bulan & tahun.',
                  '3. Omzet per produk dan per channel terhitung otomatis.'])
    return wb


# ---------------------------------------------------------------- 7. Hutang piutang
def hutang():
    wb = Workbook(); ws = wb.active; ws.title = 'Hutang Piutang'
    judul(ws, 'Hutang & Piutang', 'Catat siapa berutang ke usaha (piutang) dan usaha berutang ke siapa (hutang).', [22, 11, 13, 13, 16, 16, 16, 14])
    ws['A3'] = 'Hari ini'; ws['B3'] = '=TODAY()'; ws['B3'].number_format = TGL
    kepala(ws, 5, ['Nama', 'Jenis', 'Tanggal', 'Jatuh tempo', 'Jumlah', 'Sudah dibayar', 'Sisa', 'Status'])
    data = [('Toko Berkah', 'Piutang', -20, -5, 1500000, 500000), ('Supplier Tepung Jaya', 'Hutang', -10, 10, 2200000, 0), ('Bu Rahma (katering)', 'Piutang', -3, 7, 900000, 900000)]
    N = 200
    for i in range(N):
        r = 6 + i
        if i < len(data):
            n, j, t, jt, jm, b = data[i]
            for c, v in ((1, n), (2, j), (3, HARI + dt.timedelta(days=t)), (4, HARI + dt.timedelta(days=jt + 25)), (5, jm), (6, b)): ws.cell(row=r, column=c, value=v)
        ws.cell(row=r, column=7, value=f'=IF(A{r}="","",E{r}-F{r})')
        ws.cell(row=r, column=8, value=f'=IF(A{r}="","",IF(G{r}<=0,"LUNAS",IF(AND(D{r}<>"",$B$3>D{r}),"TERLAMBAT","BELUM")))')
    gaya(ws, 6, 5 + N, 1, 6, isian=True); gaya(ws, 6, 5 + N, 7, 8)
    for r in range(6, 6 + N):
        for c in (3, 4): ws.cell(row=r, column=c).number_format = TGL
        for c in (5, 6, 7): ws.cell(row=r, column=c).number_format = RP
    validasi_list(ws, f'B6:B{5+N}', ['Piutang', 'Hutang'])
    ws.conditional_formatting.add(f'H6:H{5+N}', CellIsRule(operator='equal', formula=['"TERLAMBAT"'], fill=PatternFill('solid', fgColor=MERAH), font=Font(bold=True, color='8A2410')))
    ws.conditional_formatting.add(f'H6:H{5+N}', CellIsRule(operator='equal', formula=['"LUNAS"'], fill=PatternFill('solid', fgColor=MUDA), font=Font(color=HIJAU)))
    ws['J5'] = 'Ringkasan'; ws['J5'].font = Font(bold=True); ws.column_dimensions['J'].width = 26; ws.column_dimensions['K'].width = 18
    for i, (l, f) in enumerate([('Total piutang belum dibayar', f'=SUMIFS(G6:G{5+N},B6:B{5+N},"Piutang")'), ('Total hutang belum dibayar', f'=SUMIFS(G6:G{5+N},B6:B{5+N},"Hutang")'), ('Jumlah tagihan terlambat', f'=COUNTIF(H6:H{5+N},"TERLAMBAT")')]):
        ws.cell(row=6 + i, column=10, value=l); c = ws.cell(row=6 + i, column=11, value=f); c.number_format = RP if i < 2 else '0'; c.border = KOTAK
    petunjuk(wb, ['1. Isi nama, jenis (Piutang = orang berutang ke kita, Hutang = kita berutang), tanggal, jatuh tempo, dan jumlah.',
                  '2. Setiap ada pembayaran, tambahkan nilainya ke kolom "Sudah dibayar".',
                  '3. Status otomatis: LUNAS (hijau), TERLAMBAT (merah, lewat jatuh tempo), atau BELUM.'])
    return wb


# ---------------------------------------------------------------- 8. Absensi
def absensi():
    wb = Workbook(); ws = wb.active; ws.title = 'Absensi'
    judul(ws, 'Absensi Bulanan', 'Kode: H = hadir, S = sakit, I = izin, A = alpa, C = cuti, L = libur. Rekap otomatis di kanan.', [22] + [4] * 31 + [6] * 6)
    ws['A3'] = 'Bulan'; ws['B3'] = 'November 2026'
    kepala(ws, 5, ['Nama'] + [str(d) for d in range(1, 32)] + ['H', 'S', 'I', 'A', 'C', 'L'])
    ws.freeze_panes = 'B6'
    nama = ['Siti Aminah', 'Budi Santoso', 'Rina Wulandari']
    N = 40
    for i in range(N):
        r = 6 + i
        if i < len(nama):
            ws.cell(row=r, column=1, value=nama[i])
            for d in range(1, 11): ws.cell(row=r, column=1 + d, value='L' if d in (1, 8) else ('S' if (i == 1 and d == 4) else 'H'))
        for j, k in enumerate('HSIACL'):
            ws.cell(row=r, column=33 + j, value=f'=IF($A{r}="","",COUNTIF($B{r}:$AF{r},"{k}"))')
    gaya(ws, 6, 5 + N, 1, 32, isian=True); gaya(ws, 6, 5 + N, 33, 38)
    for c in range(2, 33):
        for r in range(6, 6 + N): ws.cell(row=r, column=c).alignment = Alignment(horizontal='center')
    validasi_list(ws, f'B6:AF{5+N}', list('HSIACL'))
    ws.conditional_formatting.add(f'B6:AF{5+N}', CellIsRule(operator='equal', formula=['"A"'], fill=PatternFill('solid', fgColor=MERAH)))
    ws.conditional_formatting.add(f'B6:AF{5+N}', CellIsRule(operator='equal', formula=['"L"'], fill=PatternFill('solid', fgColor=ABU)))
    petunjuk(wb, ['1. Tulis nama karyawan di kolom A.', '2. Setiap hari isi kode kehadiran (pilih dari daftar).',
                  '3. Jumlah H/S/I/A/C/L per orang terhitung otomatis di sebelah kanan. Untuk bulan baru, salin sheet dan kosongkan kode harian.'])
    return wb


TEMPLATE = [
    ('kas', 'Buku Kas Harian', 'Saldo berjalan otomatis + rekap laba/rugi per kategori per bulan.', '💰', buku_kas),
    ('stok', 'Stok Barang', 'Stok akhir otomatis dari mutasi masuk/keluar, tanda merah saat stok menipis.', '📦', stok),
    ('invoice', 'Invoice', 'Subtotal, diskon, PPN, DP, dan sisa tagihan otomatis. Siap cetak A4.', '🧾', invoice),
    ('gaji', 'Gaji & Slip Karyawan', 'Gaji bersih dengan lembur, bonus, potongan. Slip terisi otomatis per nama.', '👥', gaji),
    ('anggaran', 'Anggaran Bulanan', 'Rencana vs realisasi, sisa, dan % terpakai dengan peringatan merah.', '📊', anggaran),
    ('penjualan', 'Catatan Penjualan', 'Omzet per produk dan per channel (offline, marketplace, ojol) per bulan.', '🛒', penjualan),
    ('hutang', 'Hutang & Piutang', 'Sisa tagihan dan status LUNAS / BELUM / TERLAMBAT otomatis.', '🤝', hutang),
    ('absensi', 'Absensi Bulanan', 'Kode H/S/I/A/C/L per hari dengan rekap otomatis per karyawan.', '🗓️', absensi),
]

if __name__ == '__main__':
    berkas = []
    for slug, nama, desk, ikon, fn in TEMPLATE:
        wb = fn(); f = os.path.join(OUT, f'excelcepat-{slug}.xlsx'); wb.save(f)
        data = base64.b64encode(open(f, 'rb').read()).decode()
        berkas.append({'slug': slug, 'nama': nama, 'desk': desk, 'ikon': ikon, 'file': f'excelcepat-{slug}.xlsx', 'b64': data})
        print(f'{f}  {os.path.getsize(f)/1024:.1f} KB')
    js = '/* Dibuat oleh tools/excelcepat/buat-template.py — jangan disunting manual. */\nconst BERKAS = ' + json.dumps(berkas, ensure_ascii=False) + ';\n'
    open(os.path.join(ROOT, 'situs', 'excelcepat.com', '_berkas.js'), 'w').write(js)
