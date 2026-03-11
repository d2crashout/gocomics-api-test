from __future__ import annotations

import os
from datetime import date
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def _iso(value: object) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def get_random_big_nate_from_comics() -> dict[str, str]:
    """Fetch a random Big Nate strip via the third-party `comics` package.

    The `comics` package API can vary by version, so we support a few shapes.
    """
    import comics  # required external dependency from https://pypi.org/project/comics/

    # Shape 1: package exposes direct helper(s)
    for fn_name in ("random", "get_random", "get_random_comic"):
        fn = getattr(comics, fn_name, None)
        if callable(fn):
            try:
                comic = fn("big nate")
                break
            except TypeError:
                try:
                    comic = fn("bignate")
                    break
                except Exception:
                    continue
    else:
        comic = None

    # Shape 2: package exposes GoComics client / Comic class
    if comic is None:
        for attr in ("GoComics", "Gocomics", "Comic", "Comics"):
            cls = getattr(comics, attr, None)
            if cls is None:
                continue
            try:
                client = cls("big nate")
            except Exception:
                try:
                    client = cls("bignate")
                except Exception:
                    continue

            for method_name in ("random", "get_random", "random_comic"):
                method = getattr(client, method_name, None)
                if callable(method):
                    comic = method()
                    break
            if comic is not None:
                break

    if comic is None:
        raise RuntimeError(
            "Unsupported `comics` package API. Please install/update from https://pypi.org/project/comics/."
        )

    title = getattr(comic, "title", None) or "Big Nate"
    image_url = (
        getattr(comic, "image_url", None)
        or getattr(comic, "img", None)
        or getattr(comic, "image", None)
    )
    page_url = getattr(comic, "url", None) or getattr(comic, "page_url", None) or ""
    published_date = _iso(getattr(comic, "date", None) or getattr(comic, "published_date", ""))

    if not image_url:
        raise RuntimeError("The `comics` package did not return an image URL.")

    return {
        "title": str(title),
        "image_url": str(image_url),
        "page_url": str(page_url),
        "published_date": str(published_date),
    }


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/random-big-nate")
def random_big_nate():
    try:
        return jsonify(get_random_big_nate_from_comics())
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": str(exc)}), 502


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
