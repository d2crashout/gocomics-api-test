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

API endpoint: `GET /api/random-big-nate`

## Frontend (GitHub Pages)

Serve `frontend/` as a static site and set the backend URL in `frontend/script.js`.
