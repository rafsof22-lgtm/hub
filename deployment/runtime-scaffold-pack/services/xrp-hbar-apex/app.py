import os
from flask import Flask, jsonify
import psycopg
import redis

app = Flask(__name__)

APP_NAME = os.getenv("APP_NAME", "xrp-hbar-apex")
APP_ENV = os.getenv("APP_ENV", "production")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "xrp_hbar_apex")
POSTGRES_USER = os.getenv("POSTGRES_USER", "xrp_hbar_apex_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "change_me")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": APP_NAME,
        "env": APP_ENV,
        "version": APP_VERSION
    }), 200

@app.route("/ready")
def ready():
    db_ok = False
    redis_ok = False
    db_error = None
    redis_error = None

    try:
        conn = psycopg.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            connect_timeout=3
        )
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        conn.close()
        db_ok = True
    except Exception as e:
        db_error = str(e)

    try:
        r = redis.from_url(REDIS_URL, socket_connect_timeout=3)
        redis_ok = r.ping()
    except Exception as e:
        redis_error = str(e)

    if db_ok and redis_ok:
        return jsonify({
            "status": "ready",
            "postgres": "ok",
            "redis": "ok"
        }), 200

    return jsonify({
        "status": "not_ready",
        "postgres": "ok" if db_ok else db_error,
        "redis": "ok" if redis_ok else redis_error
    }), 503

@app.route("/deployment/status")
def deployment_status():
    return jsonify({
        "status": "running",
        "service": APP_NAME,
        "env": APP_ENV,
        "version": APP_VERSION,
        "stack": ["app", "postgres", "redis", "caddy"]
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
