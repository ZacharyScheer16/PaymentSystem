// Single source of truth for the API base URL.
//
// Defaults to the relative "/api" — in both `npm run dev` (Vite proxy) and the
// Docker image (nginx proxy), requests go to the same origin serving the page,
// so nothing host-specific is baked into the bundle at build time.
//
// VITE_API_BASE overrides it for the case where the API lives on a different
// origin (e.g. a separately deployed backend). Note it is read at BUILD time,
// not runtime — changing it requires rebuilding the frontend.
export const API_BASE = import.meta.env.VITE_API_BASE || '/api'
