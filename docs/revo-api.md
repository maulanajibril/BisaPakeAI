# Revo.id API, ringkasan untuk integrasi

Sumber: https://revo.id/developer/ (dibaca 2026-11-25). Cek ulang ke halaman aslinya sebelum go-live.

## Dasar
- Base URL: `https://revo.id/api/v1`
- Auth: `Authorization: Bearer rv_live_…` atau `rv_test_…` (sandbox, datanya terpisah). Header cadangan: `X-Revo-Key`.
- Key dibuat di Dashboard → Developer (`https://revo.id/app/?iv=developer`). Hanya ditampilkan sekali. Maksimal 10 key aktif per toko. **Key hanya boleh dipakai di server**, jangan sampai masuk ke JS browser.
- Nominal dalam rupiah bulat (`49000`), waktu ISO 8601 UTC. Format list: `{data:[…], meta:{page, per_page, total, total_pages}}` dengan `per_page` maks 100.
- Rate limit 300 request/menit per key. Kalau lewat, dapat 429 `rate_limited`.

## Endpoint yang kita pakai
| Method | Path | Kegunaan |
|---|---|---|
| GET | `/me` | info toko |
| GET/POST | `/products`, `/products/{id}` | list, buat, ubah produk (`type`: link, digital, membership, support, service; field `title`, `price`, `access_url`, `description`, `status` active/draft) |
| POST | `/checkouts` | buat order + link bayar |
| GET | `/orders`, `/orders/{id atau number}` | status order (`unpaid`, `paid`, `cancelled`, `refunded`); filter `external_id`, `email`, `product_id` |
| GET | `/access?email=&product_id=` | cek apakah email punya akses |
| POST | `/webhook` | atur URL webhook, respons berisi secret `whsec_…` |
| POST | `/webhooks/test` | kirim `ping` |

## Checkout
`POST /checkouts` dengan body:
```json
{ "product_id": 123, "customer": {"name":"", "email":"", "phone":""},
  "external_id": "quiz-session-abc", "metadata": {"site":"aura"},
  "return_url": "https://situs-kita/terima-kasih" }
```
Field opsional lain: `coupon`, `amount` (khusus pay-what-you-want), `bump`, `affiliate`, `cf[0..n]`.
Respons 201 berisi `data.id`, `number` (RV-yymmdd-000123), `status: "unpaid"`, `checkout_url`. Arahkan pembeli ke `checkout_url`.
- Setelah bayar, pembeli kembali ke `return_url?revo_order=RV-…&status=paid`. **Ini bukan bukti bayar.** Konfirmasi lewat webhook atau `GET /orders/{number}`.
- Order yang belum dibayar kedaluwarsa otomatis (durasinya tidak disebut). Buat checkout baru untuk setiap klik beli.

## Webhook
- Event: `order.paid`, `order.refunded`, `subscription.created|renewed|cancelled|expired`, `license.updated`, `ping`.
- Header: `Revo-Event`, `Revo-Delivery` (`evt_…`), `Revo-Signature: t=<unix>,v1=<hex>`, dan `Revo-Mode: test` di sandbox.
- Body: `{id, type, created_at, store, data}`.
- Verifikasi: hitung HMAC-SHA256 hex atas `"{t}.{raw body}"` dengan secret `whsec_…`, bandingkan dengan `v1` pakai timing-safe compare. Tolak kalau tidak cocok atau `|now - t| > 300` detik. Pakai raw body sebelum di-parse.
- Endpoint harus membalas 2xx dalam 10 detik. Kalau gagal, Revo mencoba ulang setelah 1m, 5m, 30m, 2j, 6j, 24j. Bisa datang dobel, jadi dedupe berdasarkan `id` event. Urutannya juga tidak dijamin. Redirect tidak diikuti. Port yang diterima 80, 443, atau 8080.
- Di production, abaikan event yang `livemode: false`.

## Sandbox
Pakai key `rv_test_…`. Halaman checkout menampilkan tombol simulasi bayar/gagal. Ada juga endpoint `POST /sandbox/orders/{id}/pay|fail|refund` dan `POST /sandbox/reset`.

## MCP (untuk Claude mengelola toko, bukan untuk website live)
`https://revo.id/api/v1/mcp`, transport Streamable HTTP, header `Authorization: Bearer rv_test_…`.
Tool: `get_store`, `list_products`, `create_product`, `update_product`, `create_payment_link`, `get_order`, `list_orders`, `check_access`, `set_webhook`, `get_integration_code`, `simulate_payment`.

## Yang tidak didokumentasikan
Skema respons lengkap, durasi kedaluwarsa checkout, API refund live, idempotency key, aturan validasi `return_url`, rotasi secret, dan batas jumlah produk/domain per toko. **Tanyakan ke Revo soal pemakaian satu toko untuk banyak domain.**
