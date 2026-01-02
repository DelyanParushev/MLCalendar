#!/usr/bin/env python
"""
Vercel serverless function entry point for FastAPI backend
"""
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.main import app
from mangum import Mangum

# Vercel will use this as the ASGI application via Mangum
app.title = "AI Calendar API (Vercel)"

# Mangum adapter for AWS Lambda/Vercel
handler = Mangum(app, lifespan="off")
