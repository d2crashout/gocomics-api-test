from __future__ import annotations

import importlib
import inspect
import logging
import os
from datetime import date
from types import ModuleType
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("big-nate-backend")

TARGET_NAMES = ["big nate", "bignate", "big-nate"]
COMIC_METHOD_NAMES = ["random", "get_random", "random_comic", "comic", "latest"]


@app.before_request
def _log_request_start() -> None:
    logger.info("request.start method=%s path=%s", request.method, request.path)


@app.after_request
def _log_request_end(response):
    logger.info("request.end method=%s path=%s status=%s", request.method, request.path, response.status_code)
    return response


def _iso(value: object) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _normalize_result(result: Any) -> dict[str, str] | None:
    """Normalize common result shapes from the `comics` package."""
    if result is None:
        return None

    if isinstance(result, dict):
        title = result.get("title") or "Big Nate"
        image_url = result.get("image_url") or result.get("image") or result.get("img")
        page_url = result.get("page_url") or result.get("url") or ""
        published_date = _iso(result.get("published_date") or result.get("date") or "")
        if image_url:
            return {
                "title": str(title),
                "image_url": str(image_url),
                "page_url": str(page_url),
                "published_date": str(published_date),
            }

    if isinstance(result, str) and result.startswith("http"):
        return {
            "title": "Big Nate",
            "image_url": result,
            "page_url": "",
            "published_date": "",
        }

    title = getattr(result, "title", None) or "Big Nate"
    image_url = (
        getattr(result, "image_url", None)
        or getattr(result, "img", None)
        or getattr(result, "image", None)
        or getattr(result, "src", None)
    )
    page_url = getattr(result, "url", None) or getattr(result, "page_url", None) or ""
    published_date = _iso(getattr(result, "date", None) or getattr(result, "published_date", ""))

    if image_url:
        return {
            "title": str(title),
            "image_url": str(image_url),
            "page_url": str(page_url),
            "published_date": str(published_date),
        }

    return None


def _try_call(fn: Any, *args: Any) -> Any:
    try:
        return fn(*args)
    except TypeError:
        return fn()


def _try_module_functions(comics_module: ModuleType) -> dict[str, str] | None:
    for fn_name in COMIC_METHOD_NAMES:
        fn = getattr(comics_module, fn_name, None)
        if not callable(fn):
            continue
        for name in TARGET_NAMES:
            try:
                logger.info("comics.try module_function=%s arg=%s", fn_name, name)
                value = _try_call(fn, name)
                normalized = _normalize_result(value)
                if normalized:
                    return normalized
            except Exception:
                logger.exception("comics.fail module_function=%s arg=%s", fn_name, name)
    return None


def _try_named_attributes(comics_module: ModuleType) -> dict[str, str] | None:
    """Try attributes that look like Big Nate handlers/modules."""
    for attr_name in dir(comics_module):
        lower = attr_name.lower().replace("_", "").replace("-", "")
        if "nate" not in lower:
            continue

        target = getattr(comics_module, attr_name, None)
        if target is None:
            continue

        logger.info("comics.try named_attribute=%s", attr_name)

        if inspect.ismodule(target):
            for method_name in COMIC_METHOD_NAMES:
                method = getattr(target, method_name, None)
                if not callable(method):
                    continue
                try:
                    value = _try_call(method)
                    normalized = _normalize_result(value)
                    if normalized:
                        return normalized
                except Exception:
                    logger.exception("comics.fail module=%s method=%s", attr_name, method_name)

        if callable(target):
            for name in TARGET_NAMES + [None]:
                try:
                    value = target(name) if name is not None else target()
                    normalized = _normalize_result(value)
                    if normalized:
                        return normalized
                except Exception:
                    logger.exception("comics.fail callable=%s", attr_name)

    return None


def _try_client_classes(comics_module: ModuleType) -> dict[str, str] | None:
    for attr_name in ("GoComics", "Gocomics", "Comic", "Comics", "Client"):
        cls = getattr(comics_module, attr_name, None)
        if cls is None:
            continue

        for name in TARGET_NAMES:
            try:
                logger.info("comics.try class=%s name=%s", attr_name, name)
                client = cls(name)
            except Exception:
                logger.exception("comics.fail class_init=%s name=%s", attr_name, name)
                continue

            for method_name in COMIC_METHOD_NAMES:
                method = getattr(client, method_name, None)
                if not callable(method):
                    continue
                try:
                    value = _try_call(method)
                    normalized = _normalize_result(value)
                    if normalized:
                        return normalized
                except Exception:
                    logger.exception("comics.fail class=%s method=%s", attr_name, method_name)

    return None


def get_random_big_nate_from_comics() -> dict[str, str]:
    """Fetch a random Big Nate strip from the third-party `comics` package."""
    comics_module = importlib.import_module("comics")
    logger.info("comics.loaded module=%s", getattr(comics_module, "__file__", "unknown"))

    for strategy in (_try_module_functions, _try_named_attributes, _try_client_classes):
        payload = strategy(comics_module)
        if payload:
            logger.info("comics.success strategy=%s title=%s", strategy.__name__, payload.get("title"))
            return payload

    raise RuntimeError(
        "Could not fetch Big Nate from installed `comics` package. Check Render logs and verify package version/API."
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/debug/comics")
def debug_comics_shape():
    """Small debug endpoint so deployments can inspect available comics API shapes."""
    try:
        comics_module = importlib.import_module("comics")
        names = [
            name
            for name in dir(comics_module)
            if any(key in name.lower() for key in ("comic", "random", "nate", "go"))
        ]
        return jsonify({"module": getattr(comics_module, "__file__", "unknown"), "attributes": names})
    except Exception as exc:
        logger.exception("debug.comics.failed")
        return jsonify({"error": str(exc)}), 500


@app.get("/api/random-big-nate")
def random_big_nate():
    try:
        return jsonify(get_random_big_nate_from_comics())
    except Exception as exc:  # pragma: no cover
        logger.exception("comics.fetch.failed")
        return jsonify({"error": str(exc)}), 502


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    logger.info("server.start port=%s", port)
    app.run(host="0.0.0.0", port=port)
