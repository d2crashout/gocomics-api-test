# Big Nate Comic Generator

This project is split into:

- `backend/`: Python API (Render deploy target) that uses the [`comics` PyPI package](https://pypi.org/project/comics/) to fetch a random Big Nate comic.
- `frontend/`: Static site (GitHub Pages deploy target) with a button that requests and displays the comic.

## Backend (Render)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

API endpoints:
- `GET /health`
- `GET /api/random-big-nate`
- `GET /api/debug/comics` (lists discovered `comics` module attributes useful for debugging)

### Backend logging

The backend logs every request and each comics-fetch strategy attempt.
On Render, open the service logs and click **Fetch Random Comic** in the frontend.

```bash
LOG_LEVEL=DEBUG python app.py
```

## Frontend (GitHub Pages)

Serve `frontend/` as a static site.
In the UI:
1. Set/save your Render backend URL.
2. Use **Check Backend** to verify `/health`.
3. Press **Fetch Random Comic**.
