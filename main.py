import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_log = logging.getLogger("backend_api.main")
_log.setLevel(logging.INFO)
if not _log.handlers:
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))
    _log.addHandler(_h)

from firebase_admin import get_app, initialize_app
from firebase_functions import https_fn, options
from firebase_functions.https_fn import Request, Response
from mangum import Mangum

try:
    get_app()
except ValueError:
    initialize_app()

from backend_api.app import app
from backend_api.triggers.payment_approval import on_payment_status_changed  # noqa: F401

try:
    import firebase_functions.private.serving as _serving
    _serving.kill = lambda *args, **kwargs: None
except Exception:
    pass

_handler = Mangum(app, lifespan="off")


def _request_to_lambda_event(req: Request) -> dict:
    query = req.args.to_dict() if req.args else {}
    body = req.get_data(as_text=True) if req.get_data() else None
    headers = {k.lower(): v for k, v in (req.headers.items() or [])}
    path = req.path.rstrip("/") if req.path != "/" else req.path
    return {
        "resource": path,
        "path": path,
        "httpMethod": req.method,
        "headers": headers,
        "queryStringParameters": query if query else None,
        "body": body,
        "isBase64Encoded": False,
        "requestContext": {
            "identity": {"sourceIp": "127.0.0.1"},
            "http": {
                "method": req.method,
                "path": path,
            }
        },
    }


@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins="*",
        cors_methods=["get", "post", "put", "patch", "delete", "options", "head"],
    ),
    timeout_sec=300,
)
def api(req: Request) -> Response:
    query = req.args.to_dict() if req.args else {}
    _log.info("%s %s %s", req.method, req.path, query)
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    event = _request_to_lambda_event(req)
    context = type("Context", (), {"aws_request_id": "", "get_remaining_time_in_millis": lambda: 60000})()
    result = _handler(event, context)
    status = result.get("statusCode", 500)
    headers = result.get("headers", {})
    if isinstance(headers, dict):
        headers = list(headers.items())
    body = result.get("body", "") or ""
    if isinstance(body, bytes):
        body = body.decode("utf-8")
    _log.info("%s %s -> %d", req.method, req.path, status)
    res = Response(body, status=status)
    for k, v in (headers or []):
        if isinstance(k, bytes):
            k = k.decode("latin-1")
        if isinstance(v, bytes):
            v = v.decode("latin-1")
        if k.lower() not in ("content-length", "transfer-encoding"):
            res.headers[k] = v
    return res
