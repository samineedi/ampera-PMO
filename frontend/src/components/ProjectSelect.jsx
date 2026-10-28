import { useFetch } from '../hooks/useFetch.js';

// Dropdown of the board's projects (from "Project: ..." labels). Empty value = all projects.
export function ProjectSelect({ value, onChange }) {
  const { data } = useFetch('/api/projects');
  return (
    <label className="f">Project
      <select value={value} onChange={e => onChange(e.target.value)}>
        <option value="">All projects</option>
        {(data?.projects || []).map(p => <option key={p} value={p}>{p}</option>)}
      </select>
    </label>
  );
}
