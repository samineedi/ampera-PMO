export function Loading({ state }) {
  if (state.error) return (
    <div className="card"><h2>Something went wrong</h2><p>{state.error}</p>
      <p className="muted">If this is the first load, check your Trello settings in <code>.env</code>.</p></div>
  );
  return <div className="empty">Loading...</div>;
}
