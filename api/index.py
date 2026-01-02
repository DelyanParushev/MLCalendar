#!/usr/bin/env python
"""
Vercel serverless function entry point for FastAPI backend
"""
from backend.main import app

# Vercel will use this as the ASGI application
handler = app
