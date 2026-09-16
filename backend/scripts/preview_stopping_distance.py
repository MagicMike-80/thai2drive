r"""Run the real web shell/math locally without importing database/payment services.

From repository root:
  .venv\Scripts\python.exe backend/scripts/preview_stopping_distance.py
Open http://127.0.0.1:8088/api/web and continue as guest.
Auth/content endpoints are intentionally not included in this isolated preview.
"""
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

backend = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend))
from webapp import webapp_router
from traffic_math_routes import math_router

app = FastAPI()
app.include_router(webapp_router, prefix='/api')
app.include_router(math_router, prefix='/api')
app.mount('/api/assets', StaticFiles(directory=backend / 'public_assets'), name='assets')

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8088)
