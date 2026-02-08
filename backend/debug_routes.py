
import sys
import os
from fastapi import FastAPI
from routers import ai_news

app = FastAPI()
app.include_router(ai_news.router)

print("Checking routes for ai_news...")
found = False
for route in app.routes:
    if "media-focus" in route.path:
        print(f"FOUND: {route.path}")
        found = True

if not found:
    print("NOT FOUND: media-focus endpoint is missing!")
else:
    print("Endpoint is correctly registered.")
