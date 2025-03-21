#!/bin/bash
# update-dependencies.sh

set -e

echo "📦 Analysing current dependencies..."
uv pip show --system --directory ./backend -f > current_deps.txt

echo "⬆️ Upgrading all dependencies..."
uv pip compile --system --upgrade --directory ./backend -o new_uv.lock

echo "🔍 Installing new dependencies for testing..."
UV_LOCK=new_uv.lock uv pip sync --directory ./backend

echo "🧪 Running tests with new dependencies..."
cd .. && pytest backend/tests -v

if [ $? -eq 0 ]; then
    echo "✅ Tests passed with new dependencies!"
    echo "📋 Generating report of upgraded dependencies..."
    uv pip show --system --directory backend -f > new_deps.txt
    diff current_deps.txt new_deps.txt || true

    echo "📝 Updating lock file..."
    cd backend
    mv new_uv.lock uv.lock

    echo "🚀 Dependencies upgraded successfully!"
else
    echo "❌ Tests failed with new dependencies!"
    echo "🔄 Reverting to original dependencies..."
    UV_LOCK=uv.lock uv pip sync
fi
