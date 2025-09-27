#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🔧 Starting build process..."

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔍 Checking Python installation..."
python --version
which python

echo "📁 Current directory contents:"
ls -la

echo "🗄️ Setting up database..."
# Skip migration for now to avoid issues, we'll run it after deployment
echo "⚠️  Skipping migration during build - will run on first startup"

echo "✅ Build completed successfully!"