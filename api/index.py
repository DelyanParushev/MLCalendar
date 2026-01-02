#!/usr/bin/env python
"""
Vercel serverless function entry point for FastAPI backend
"""
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import the FastAPI app
from backend.main import app

# Export for Vercel (FastAPI works directly with Vercel's Python runtime)
# No need for Mangum - Vercel handles ASGI natively
