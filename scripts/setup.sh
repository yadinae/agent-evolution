#!/bin/bash
# Agent Evolution - Setup Script
# This script helps you set up the development environment

set -e

echo "🧬 Agent Evolution - Setup Script"
echo "=================================="
echo ""

# Check Python version
echo "📌 Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "   Python version: $python_version"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "❌ Error: Python 3.11+ is required"
    exit 1
fi
echo "   ✅ Python version OK"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
else
    echo "   ℹ️  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "   ✅ Dependencies installed"
echo ""

# Install development tools
echo "🛠️  Installing development tools..."
pip install pytest pytest-cov black flake8 mypy
echo "   ✅ Development tools installed"
echo ""

# Run tests
echo "🧪 Running tests..."
pytest tests/ -v --tb=short
echo "   ✅ Tests passed"
echo ""

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data
echo "   ✅ Data directory created"
echo ""

# Create logs directory
echo "📝 Creating logs directory..."
mkdir -p logs
echo "   ✅ Logs directory created"
echo ""

# Create backups directory
echo "💾 Creating backups directory..."
mkdir -p backups
echo "   ✅ Backups directory created"
echo ""

# Copy example config
echo "⚙️  Setting up configuration..."
if [ ! -f "config/.env" ]; then
    cp config/.env.example config/.env
    echo "   ℹ️  Created config/.env from template"
    echo "   ⚠️  Please edit config/.env with your settings"
else
    echo "   ℹ️  Configuration already exists"
fi
echo ""

# Initialize Git (if not already initialized)
echo "🔧 Initializing Git repository..."
if [ ! -d ".git" ]; then
    git init
    echo "   ✅ Git repository initialized"
else
    echo "   ℹ️  Git repository already exists"
fi
echo ""

# Show next steps
echo "=================================="
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit config/.env with your settings"
echo "   2. Copy database files to data/ directory (optional)"
echo "   3. Run examples:"
echo "      python examples/basic_usage.py"
echo "   4. Run the evolution engine:"
echo "      python src/evolve_analysis.py --health-check"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Project overview"
echo "   - CONTRIBUTING.md - Contribution guide"
echo "   - docs/ - Technical documentation"
echo ""
echo "🎉 Happy coding!"
echo ""
