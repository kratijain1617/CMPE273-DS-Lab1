"""
Service B (Client) - CMPE 273 Week 1 Lab 1 (Python track)
GET /health -> {"statusCode":200,"status":"ok"}
GET /profile?user=<name> -> calls Service A /profile?user=, returns profile (with statusCode)
GET /profiles -> calls Service A /profiles, returns all profiles (with statusCode)
Timeout 2s when calling Service A; on failure returns 503 with reason and logs failure_reason
"""

import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
SERVICE_NAME = "ServiceB-Client"
SERVICE_A_BASE = "http://127.0.0.1:8080"
REQUEST_TIMEOUT_SEC = 2


@app.before_request
def before_request():
    request.start_time = time.perf_counter()


@app.after_request
def after_request(response):
    latency_ms = (time.perf_counter() - request.start_time) * 1000
    endpoint = request.path or "/"
    print(f"service={SERVICE_NAME} endpoint={endpoint} status={response.status_code} latency_ms={latency_ms:.2f}")
    return response


def get_failure_reason(exc):
    """Map exception to clear failure reason for logging and response."""
    if exc is None:
        return "Provider (Service A) is down or unreachable."
    msg = (getattr(exc, "message", "") or str(exc) or "").lower()
    if "econnrefused" in msg or "connection refused" in msg:
        return "Connection refused. Provider (Service A) is down or unreachable."
    if "timed out" in msg or "timeout" in msg:
        return "Request timed out. Provider (Service A) did not respond in time."
    return str(exc) or "Provider (Service A) is down or unreachable."


def log_failure(endpoint, reason):
    from datetime import datetime
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    print(f"[{ts}] service={SERVICE_NAME} endpoint={endpoint} failure_reason={reason}")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"statusCode": 200, "status": "ok"})


@app.route("/profile", methods=["GET"])
def profile():
    user = request.args.get("user", "")
    url = f"{SERVICE_A_BASE}/profile?user={requests.utils.quote(user)}"
    try:
        r = requests.get(url, timeout=REQUEST_TIMEOUT_SEC)
        data = r.json()
        return jsonify(data), r.status_code
    except requests.exceptions.Timeout:
        reason = "Request timed out. Provider (Service A) did not respond in time."
        log_failure("/profile", reason)
        return (
            jsonify({
                "statusCode": 503,
                "error": "Service A (Profile API) unavailable",
                "reason": reason,
                "hint": "Ensure Service A is running on http://127.0.0.1:8080",
            }),
            503,
        )
    except requests.exceptions.ConnectionError as e:
        reason = "Connection refused. Provider (Service A) is down or unreachable."
        log_failure("/profile", reason)
        return (
            jsonify({
                "statusCode": 503,
                "error": "Service A (Profile API) unavailable",
                "reason": reason,
                "hint": "Ensure Service A is running on http://127.0.0.1:8080",
            }),
            503,
        )
    except requests.exceptions.RequestException as e:
        reason = get_failure_reason(e)
        log_failure("/profile", reason)
        return (
            jsonify({
                "statusCode": 503,
                "error": "Service A (Profile API) unavailable",
                "reason": reason,
                "hint": "Ensure Service A is running on http://127.0.0.1:8080",
            }),
            503,
        )


@app.route("/profiles", methods=["GET"])
def profiles():
    url = f"{SERVICE_A_BASE}/profiles"
    try:
        r = requests.get(url, timeout=REQUEST_TIMEOUT_SEC)
        data = r.json()
        return jsonify(data), r.status_code
    except requests.exceptions.Timeout:
        reason = "Request timed out. Provider (Service A) did not respond in time."
        log_failure("/profiles", reason)
        return (
            jsonify({
                "statusCode": 503,
                "error": "Service A (Profile API) unavailable",
                "reason": reason,
                "hint": "Ensure Service A is running on http://127.0.0.1:8080",
            }),
            503,
        )
    except requests.exceptions.ConnectionError:
        reason = "Connection refused. Provider (Service A) is down or unreachable."
        log_failure("/profiles", reason)
        return (
            jsonify({
                "statusCode": 503,
                "error": "Service A (Profile API) unavailable",
                "reason": reason,
                "hint": "Ensure Service A is running on http://127.0.0.1:8080",
            }),
            503,
        )
    except requests.exceptions.RequestException as e:
        reason = get_failure_reason(e)
        log_failure("/profiles", reason)
        return (
            jsonify({
                "statusCode": 503,
                "error": "Service A (Profile API) unavailable",
                "reason": reason,
                "hint": "Ensure Service A is running on http://127.0.0.1:8080",
            }),
            503,
        )


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def not_found(path):
    return jsonify({"statusCode": 404, "error": "Not Found", "path": request.path}), 404


if __name__ == "__main__":
    print("Service B (Client) listening on http://127.0.0.1:8081")
    print("Endpoints: GET /health, GET /profile?user=<name>, GET /profiles")
    print(f"Calls Service A at {SERVICE_A_BASE} (timeout {REQUEST_TIMEOUT_SEC}s)")
    app.run(host="127.0.0.1", port=8081)
