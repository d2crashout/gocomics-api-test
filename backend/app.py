from __future__ import annotations

import logging
import os
from datetime import date

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("big-nate-backend")


@app.before_request
def _log_request_start() -> None:
    logger.info("Request started", extra={"method": request.method, "path": request.path})


@app.after_request
def _log_request_end(response):
    logger.info(
        "Request finished",
        extra={"method": request.method, "path": request.path, "status": response.status_code},
    )
    return response


def _iso(value: object) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _extract_comic_payload(comic: object) -> dict[str, str]:
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


def get_random_big_nate_from_comics() -> dict[str, str]:
    """Fetch a random Big Nate strip via the third-party `comics` package."""
    import comics  # required external dependency from https://pypi.org/project/comics/

    logger.info("Loaded comics package", extra={"module": getattr(comics, "__file__", "unknown")})

    comic = None

    for fn_name in ("random", "get_random", "get_random_comic"):
        fn = getattr(comics, fn_name, None)
        if not callable(fn):
            continue
        for comic_name in ("big nate", "bignate"):
            try:
                logger.info("Trying module function", extra={"function": fn_name, "comic_name": comic_name})
                comic = fn(comic_name)
                if comic is not None:
                    return _extract_comic_payload(comic)
            except Exception:
                logger.exception("Module function failed", extra={"function": fn_name, "comic_name": comic_name})

    for attr in ("GoComics", "Gocomics", "Comic", "Comics"):
        cls = getattr(comics, attr, None)
        if cls is None:
            continue

        for comic_name in ("big nate", "bignate"):
            try:
                logger.info("Trying client constructor", extra={"class": attr, "comic_name": comic_name})
                client = cls(comic_name)
            except Exception:
                logger.exception("Client construction failed", extra={"class": attr, "comic_name": comic_name})
                continue

            for method_name in ("random", "get_random", "random_comic"):
                method = getattr(client, method_name, None)
                if not callable(method):
                    continue
                try:
                    logger.info("Trying client method", extra={"class": attr, "method": method_name})
                    comic = method()
                    if comic is not None:
                        return _extract_comic_payload(comic)
                except Exception:
                    logger.exception("Client method failed", extra={"class": attr, "method": method_name})

    raise RuntimeError(
        "Unsupported or failing `comics` package API. Check backend logs for details and verify the installed package version."
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/random-big-nate")
def random_big_nate():
    try:
        payload = get_random_big_nate_from_comics()
        logger.info("Comic fetch succeeded", extra={"title": payload.get("title")})
        return jsonify(payload)
    except Exception as exc:  # pragma: no cover
        logger.exception("Comic fetch failed")
        return jsonify({"error": str(exc)}), 502


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    logger.info("Starting backend", extra={"port": port})
    app.run(host="0.0.0.0", port=port)
