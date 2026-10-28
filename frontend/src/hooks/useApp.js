import { createContext, useContext } from 'react';

// App-wide state: toast and refresh counter (bumped after Refresh so pages reload).
export const AppCtx = createContext(null);
export const useApp = () => useContext(AppCtx);
