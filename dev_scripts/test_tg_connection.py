"""Test TigerGraph Savanna connection via HOST and SECRET (Token-based Auth).

This test validates connection for TigerGraph Cloud / Savanna accounts using
OAuth / Workgroup access (HOST + SECRET -> TOKEN only, no username/password).
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure stdout uses UTF-8 encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 1. Locate and load .env file
WORKSPACE_ROOT = Path(__file__).resolve().parent
ENV_PATH = WORKSPACE_ROOT / ".env"

if not ENV_PATH.exists():
    print(f"[ERROR] .env file not found at: {ENV_PATH}")
    sys.exit(1)

# Load environment variables
load_dotenv(dotenv_path=ENV_PATH)

tg_host = os.getenv("TG_HOST", "").strip().strip("\"'")
tg_secret = os.getenv("TG_SECRET", "").strip().strip("\"'")

# Validate presence without printing the values
if not tg_host:
    print("[ERROR] TG_HOST is missing or empty in .env.")
    sys.exit(1)

if not tg_secret:
    print("[ERROR] TG_SECRET is missing or empty in .env.")
    sys.exit(1)

print(f"[INFO] .env loaded from: {ENV_PATH}")
host_domain = tg_host.split("//")[-1].split("/")[0].split(":")[0]
print(f"[INFO] TG_HOST is set (domain: {host_domain})")
print(f"[INFO] TG_SECRET is present (length: {len(tg_secret)} characters, non-empty)")

# 2. Connect using pyTigerGraph
try:
    import pyTigerGraph as tg
except ImportError:
    print("[ERROR] pyTigerGraph is not installed. Please run: pip install pyTigerGraph")
    sys.exit(1)

def run_connection_test():
    print("\n--- Testing TigerGraph Savanna Connection ---")
    try:
        # Initialize connection with host
        conn = tg.TigerGraphConnection(host=tg_host)
        print("[1/3] Initialized TigerGraphConnection object.")

        # Note for Google OAuth / SSO workgroup accounts:
        # pyTigerGraph defaults to username/password="tigergraph", which sends
        # an invalid Basic auth header during token negotiation.
        # Clearing this header ensures clean SECRET -> Bearer Token generation.
        conn._cached_auth.pop("Authorization", None)
        conn.authHeader = {}

        # Request token using secret
        print("[2/3] Requesting token with TG_SECRET via conn.getToken(secret)...")
        token_res = conn.getToken(secret=tg_secret)
        if token_res:
            print("[2/3] Token successfully acquired.")
        else:
            print("[2/3] Warning: Token acquisition returned empty.")

        # Ping database with echo
        print("[3/3] Calling conn.echo()...")
        echo_res = conn.echo()
        print(f"[3/3] Echo response: {echo_res}")

        print("\n==========================================")
        print(" SUCCESS: TigerGraph Savanna connected OK!")
        print("==========================================")
        return True

    except Exception as e:
        error_msg = str(e)
        # Ensure secret value is never exposed in output
        if tg_secret and tg_secret in error_msg:
            error_msg = error_msg.replace(tg_secret, "***REDACTED_SECRET***")

        print("\n==========================================")
        print(" FAILURE: TigerGraph connection failed.")
        print(f" Reason: {error_msg}")
        print("==========================================")
        return False

if __name__ == "__main__":
    success = run_connection_test()
    sys.exit(0 if success else 1)
