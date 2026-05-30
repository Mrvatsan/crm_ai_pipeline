/**
 * Centralized API configuration.
 *
 * - In production (Vite build with import.meta.env.PROD === true):
 *     Uses the deployed Render backend URL.
 * - In development (vite dev server):
 *     Falls back to http://localhost:8000
 *
 * You can override the production URL by setting VITE_API_URL in a .env file.
 */
export const API_BASE_URL: string =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD
    ? "https://ai-compiler-backend-wz1n.onrender.com"
    : "http://localhost:8000");
