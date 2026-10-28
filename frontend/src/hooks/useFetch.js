import { useEffect, useState } from 'react';
import { request } from '../api/client.js';
import { useApp } from './useApp.js';

// GET a JSON endpoint; reloads when `url` or the refresh counter changes.
export function useFetch(url) {
  const { version } = useApp();
  const [state, setState] = useState({ data: null, error: null });
  useEffect(() => {
    let live = true;
    request(url)
      .then(data => live && setState({ data, error: null }))
      .catch(e => live && setState({ data: null, error: e.message }));
    return () => { live = false; };
  }, [url, version]);
  return state;
}
