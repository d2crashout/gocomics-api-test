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

### Backend logging

The backend now logs each request and detailed `comics` package fetch failures.
On Render, open your service logs while clicking **Fetch Random Comic** in the frontend.

You can tune verbosity with:

```bash
LOG_LEVEL=DEBUG python app.py
```

## Frontend (GitHub Pages)

Serve `frontend/` as a static site.
In the UI, set and save your Render backend URL before pressing **Fetch Random Comic**.
