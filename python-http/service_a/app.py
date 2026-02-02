"""
Service A (Profile API) - CMPE 273 Week 1 Lab 1 (Python track)
GET /health -> {"status":"ok"}
GET /profile?user=<name> -> returns that user's profile (statusCode 200, profile)
GET /profiles -> returns all profiles (statusCode 200, profiles - 3 profiles)
Request logging: service name, endpoint, status, latency
"""

import time
from flask import Flask, request, jsonify

app = Flask(__name__)
SERVICE_NAME = "ServiceA-Profile"

PROFILES = [
    {
        "user": "John Doe",
        "preferences": ["quiet", "non-smoker", "clean"],
        "budget": 1200,
    },
    {
        "user": "Jane Smith",
        "preferences": ["pet-friendly", "flexible", "social"],
        "budget": 1400,
    },
    {
        "user": "Bob Wilson",
        "preferences": ["quiet", "early-bird", "minimal"],
        "budget": 1100,
    },
]


@app.before_request
def before_request():
    request.start_time = time.perf_counter()


@app.after_request
def after_request(response):
    latency_ms = (time.perf_counter() - request.start_time) * 1000
    endpoint = request.path or "/"
    print(f"service={SERVICE_NAME} endpoint={endpoint} status={response.status_code} latency_ms={latency_ms:.2f}")
    return response


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/profiles", methods=["GET"])
def profiles():
    return jsonify({"statusCode": 200, "profiles": PROFILES})


@app.route("/profile", methods=["GET"])
def profile():
    user_name = (request.args.get("user") or "").strip()
    profile_obj = next(
        (p for p in PROFILES if p["user"].lower() == user_name.lower()),
        None,
    )
    if profile_obj:
        return jsonify({"statusCode": 200, "profile": profile_obj})
    return (
        jsonify({
            "statusCode": 404,
            "error": "Not Found",
            "message": f"No profile found for user: {user_name}" if user_name else "Missing query parameter: user",
        }),
        404,
    )


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def not_found(path):
    return jsonify({"statusCode": 404, "error": "Not Found", "path": request.path}), 404


if __name__ == "__main__":
    print("Service A (Profile API) listening on http://127.0.0.1:8080")
    print("Endpoints: GET /health, GET /profile?user=<name>, GET /profiles")
    app.run(host="127.0.0.1", port=8080)
