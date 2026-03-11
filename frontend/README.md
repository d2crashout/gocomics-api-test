# Frontend (GitHub Pages)

This folder is static and can be deployed directly to **GitHub Pages**.

## Setup

1. Deploy backend from `/backend` to Render.
2. Open the frontend, paste your Render URL in **Backend URL**, then click **Save Backend URL**.
3. Click **Check Backend** first.
4. Press **Fetch Random Comic**.

If it fails, check Render logs and call `/api/debug/comics` on your backend to inspect which `comics` API attributes are available.
2. Edit `script.js` and replace `https://your-render-backend.onrender.com` with your real backend URL.
3. Publish this `frontend/` folder using GitHub Pages.
