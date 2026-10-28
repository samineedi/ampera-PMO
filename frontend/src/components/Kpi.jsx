export function Kpi({ label, value, cls = '' }) {
  return <div className={`kpi ${cls}`}><span>{label}</span><b>{value}</b></div>;
}
