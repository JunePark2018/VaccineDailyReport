from fastapi import FastAPI
from fastapi.testclient import TestClient
import sys
import os

# Add updated backend path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app

client = TestClient(app)


def test_endpoints_parameters():
    print("Verifying endpoint parameters...")

    # Just checking if the app loads and endpoints accept the new param structure.
    # We won't simulate a full DB interaction here as that needs setup, but we can inspect the openapi schema
    # or try a call that fails validation if param is missing.

    response = client.get("/openapi.json")
    if response.status_code == 200:
        schema = response.json()
        paths = schema.get("paths", {})

        # Check param names in paths
        endpoints_to_check = [
            ("/news/{news_id}/reaction", "post"),
            ("/news/{news_id}/reaction", "get"),
            ("/news/{news_id}/view", "post"),
        ]

        for path, method in endpoints_to_check:
            op = paths.get(path, {}).get(method, {})
            params = op.get("parameters", [])
            query_params = [p["name"] for p in params if p["in"] == "query"]

            if "login_id" in query_params and "user_id" not in query_params:
                print(f"SUCCESS: {method.upper()} {path} uses 'login_id'.")
            else:
                print(f"FAILURE: {method.upper()} {path} params: {query_params}")
    else:
        print("Failed to get OpenAPI schema")


if __name__ == "__main__":
    test_endpoints_parameters()
