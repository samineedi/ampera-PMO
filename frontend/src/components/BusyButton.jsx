import { useState } from 'react';
import { useApp } from '../hooks/useApp.js';

// Button that disables itself and shows a label while an async action runs; errors become toasts.
export function BusyButton({ label, busyLabel, onClick, className, disabled }) {
  const { toast } = useApp();
  const [busy, setBusy] = useState(false);
  const run = async () => {
    setBusy(true);
    try { await onClick(); } catch (e) { toast(e.message, true); } finally { setBusy(false); }
  };
  return <button className={className} disabled={busy || disabled} onClick={run}>{busy ? busyLabel : label}</button>;
}
