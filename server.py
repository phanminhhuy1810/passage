"""Local comparison demo. All model inference stays on this computer."""

import argparse
import asyncio
from contextlib import asynccontextmanager
import json
from pathlib import Path
import threading
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator

from dataset import load_dataset
from engine import METHODS, SearchEngine

ROOT = Path(__file__).resolve().parent


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    top_k: int = Field(default=3, ge=1, le=5)

    @field_validator("query")
    @classmethod
    def usable_query(cls, value):
        value = value.strip()
        if not any(c.isalnum() for c in value):
            raise ValueError("Hãy nhập một câu hỏi hoặc từ khóa có chữ hoặc số.")
        return value


def create_app(*, provided_engine=None, provided_data=None):
    lock = threading.Lock()

    @asynccontextmanager
    async def lifespan(app):
        app.state.data = provided_data if provided_data is not None else load_dataset()
        app.state.engine = (provided_engine if provided_engine is not None else
                            await asyncio.to_thread(SearchEngine, app.state.data["documents"]))
        yield

    app = FastAPI(title="Vietnamese Retrieval Lab", lifespan=lifespan,
                  docs_url=None, redoc_url=None)

    @app.exception_handler(RequestValidationError)
    async def invalid_input(request: Request, exc):
        return JSONResponse(status_code=422, content={
            "error": "Nhập câu hỏi từ 1–500 ký tự có chữ hoặc số; chọn từ 1 đến 5 kết quả."
        })

    @app.get("/api/status")
    def status():
        data, engine = app.state.data, app.state.engine
        docs = {d["id"]: d for d in data["documents"]}
        examples, seen_titles = [], set()
        for question in data["queries"]:
            title = docs[question["gold_id"]]["title"]
            if question["split"] == "dev" and title not in seen_titles:
                examples.append({"text": question["text"], "title": title})
                seen_titles.add(title)
            if len(examples) == 6:
                break
        benchmark = None
        for split in ("test", "dev"):
            path = ROOT / "results" / f"{split}-metrics.json"
            if path.exists():
                report = json.loads(path.read_text(encoding="utf-8"))
                benchmark = {"split": split,
                             "query_count": report.get("query_count", report["results"][0]["query_count"]),
                             "results": report["results"]}
                break
        meta = engine.metadata
        return {
            "app": "vietnamese-retrieval-lab", "ready": True,
            "document_count": len(data["documents"]), "methods": METHODS,
            "model": {"name": meta.get("model_name"), "revision": meta.get("model_revision"),
                      "device": meta.get("device")},
            "examples": examples, "benchmark": benchmark,
        }

    @app.post("/api/search")
    def search(body: SearchRequest):
        results = []
        # One inference at a time: CPU timing remains interpretable under clicks.
        with lock:
            for method in METHODS:
                start = time.perf_counter()
                hits = app.state.engine.search(body.query, method, body.top_k)
                results.append({"method": method,
                                "elapsed_ms": round(1000 * (time.perf_counter() - start), 2),
                                "hits": hits})
        return {"query": body.query, "results": results}

    @app.get("/")
    def index():
        return FileResponse(ROOT / "web" / "index.html")

    @app.get("/app.css")
    def css():
        return FileResponse(ROOT / "web" / "app.css", media_type="text/css")

    @app.get("/app.js")
    def javascript():
        return FileResponse(ROOT / "web" / "app.js", media_type="application/javascript")

    return app


app = create_app()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", choices=["127.0.0.1", "localhost"])
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    import uvicorn
    uvicorn.run(app, host=args.host, port=args.port)
