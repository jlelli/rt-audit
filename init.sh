#!/bin/bash

# SCHED_DEADLINE Testing Toolkit - Quick Initialization Script
# Provides fast dependency checking and setup guidance

set -e

echo "🚀 RT-Audit - Real-Time Taskset Auditor - Quick Setup"
echo "======================================================="

# Check if we're in the right directory
if [ ! -f "generate_taskset.py" ]; then
    echo "❌ Error: This script must be run from the toolkit directory"
    echo "   Please cd to the directory containing generate_taskset.py"
    exit 1
fi

# Check Python availability
if command -v python3 >/dev/null 2>&1; then
    echo "✅ Python3 found: $(python3 --version)"
else
    echo "❌ Python3 not found. Please install Python 3.6+"
    exit 1
fi

# Check if dependencies are satisfied
echo ""
echo "🔍 Checking dependencies..."
if python3 check_deps.py; then
    echo ""
    echo "🎉 All dependencies are satisfied!"
    echo ""
    echo "Quick start:"
    echo "  1. Generate a taskset: python3 generate_taskset.py --config example_config.json"
    echo "  2. Check schedulability: python3 schedulability_checker.py taskset.json"
    echo "  3. Run with rt-app: rt-app taskset.json"
    echo "  4. Analyze results: python3 analyze_logs.py"
    echo ""
    echo "For more options, run: make help"
else
    echo ""
    echo "❌ Some dependencies are missing."
    echo ""
    echo "Installation options:"
    echo "  1. Auto-install (requires sudo): make install-deps"
    echo "  2. Manual install: Follow the installation guide above"
    echo "  3. Check again: python3 check_deps.py"
    echo ""
    echo "For complete setup: make setup"
fi

echo ""
echo "📚 Documentation:"
echo "  - README.md (if available)"
echo "  - make help (for all available targets)"
echo "  - python3 check_deps.py (for detailed dependency info)"
