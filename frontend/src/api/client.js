export async function request(url, body) {
  const opts = body === undefined ? {} : {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  };
  const r = await fetch(url, opts);
  let j = {};
  try { j = await r.json(); } catch (e) { /* non-JSON error body */ }
  if (r.status === 401 && !url.startsWith('/api/login') && !url.startsWith('/api/session')) {
    window.dispatchEvent(new Event('auth-required'));      // session expired: App shows the login page
  }
  if (!r.ok) throw new Error(j.error || `Request failed (${r.status})`);
  return j;
}
export const post = (url, body) => request(url, body || {});
