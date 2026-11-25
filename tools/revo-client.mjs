// Klien Revo.id API v1 (https://revo.id/developer/). Hanya dipakai di server.
import crypto from 'node:crypto';

const BASE = process.env.REVO_API_BASE || 'https://revo.id/api/v1';

export class RevoError extends Error {
  constructor(status, body) {
    super(body?.message || `Revo API error ${status}`);
    this.status = status;
    this.code = body?.code;
    this.body = body;
  }
}

export function createRevoClient({ apiKey = process.env.REVO_API_KEY, fetchImpl = globalThis.fetch } = {}) {
  async function call(method, path, body) {
    if (!apiKey) throw new Error('REVO_API_KEY belum diisi');
    const res = await fetchImpl(BASE + path, {
      method,
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    const text = await res.text();
    let json;
    try { json = text ? JSON.parse(text) : {}; } catch { json = { message: text }; }
    if (!res.ok) throw new RevoError(res.status, json);
    return json.data ?? json;
  }

  return {
    me: () => call('GET', '/me'),
    listProducts: (status = 'all') => call('GET', `/products?status=${status}&per_page=100`),
    createProduct: (p) => call('POST', '/products', p),
    updateProduct: (id, p) => call('POST', `/products/${id}`, p),
    /** Buat order + link bayar. Kembalikan { id, number, status, checkout_url, ... } */
    createCheckout: ({ productId, customer, externalId, metadata, returnUrl, coupon }) =>
      call('POST', '/checkouts', {
        product_id: Number(productId),
        customer,
        external_id: externalId,
        metadata,
        return_url: returnUrl,
        ...(coupon ? { coupon } : {}),
      }),
    getOrder: (idOrNumber) => call('GET', `/orders/${encodeURIComponent(idOrNumber)}`),
    checkAccess: (email, productId) =>
      call('GET', `/access?email=${encodeURIComponent(email)}&product_id=${productId}`),
    setWebhook: (url) => call('POST', '/webhook', { url }),
    testWebhook: () => call('POST', '/webhooks/test'),
  };
}

/**
 * Verifikasi header Revo-Signature: "t=<unix>,v1=<hex>".
 * v1 = HMAC-SHA256(secret, `${t}.${rawBody}`) dalam hex. Toleransi waktu 300 detik.
 */
export function verifyRevoSignature({ rawBody, header, secret, toleranceSec = 300, now = Date.now() }) {
  if (!header || !secret) return { ok: false, reason: 'missing_header_or_secret' };
  const parts = Object.fromEntries(
    header.split(',').map((kv) => kv.trim().split('=')).filter((a) => a.length === 2)
  );
  const t = Number(parts.t);
  const v1 = parts.v1;
  if (!t || !v1) return { ok: false, reason: 'malformed_header' };
  if (Math.abs(Math.floor(now / 1000) - t) > toleranceSec) return { ok: false, reason: 'timestamp_out_of_range' };
  const expected = crypto.createHmac('sha256', secret).update(`${t}.${rawBody}`).digest('hex');
  const a = Buffer.from(expected, 'utf8');
  const b = Buffer.from(v1, 'utf8');
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return { ok: false, reason: 'bad_signature' };
  return { ok: true };
}

/** Bantu tes: bikin header signature seperti Revo. */
export function signRevoPayload(rawBody, secret, t = Math.floor(Date.now() / 1000)) {
  const v1 = crypto.createHmac('sha256', secret).update(`${t}.${rawBody}`).digest('hex');
  return `t=${t},v1=${v1}`;
}
