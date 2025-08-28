# RT-Audit - Real-Time Taskset Auditor Makefile
# Provides easy targets for dependency management and testing

.PHONY: help check-deps install-deps test clean install

# Default target
help:
	@echo "RT-Audit - Real-Time Taskset Auditor - Available Targets:"
	@echo ""
	@echo "Dependencies:"
	@echo "  check-deps     - Check if all dependencies are satisfied"
	@echo "  install-deps   - Install system dependencies (requires sudo)"
	@echo ""
	@echo "Testing:"
	@echo "  test          - Run a complete test workflow"
	@echo "  test-generate - Test taskset generation"
	@echo "  test-check    - Test schedulability checking"
	@echo "  test-analyze  - Test log analysis (if logs exist)"
	@echo ""
	@echo "Installation:"
	@echo "  install       - Install the toolkit to system PATH"
	@echo "  uninstall     - Remove toolkit from system PATH"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean         - Remove generated files"
	@echo "  distclean     - Remove all generated and temporary files"
	@echo ""

# Check dependencies
check-deps:
	@echo "🔍 Checking dependencies..."
	@python3 check_deps.py

# Install system dependencies
install-deps:
	@echo "📦 Installing system dependencies..."
	@if command -v apt-get >/dev/null 2>&1; then \
		echo "Detected Debian/Ubuntu system"; \
		sudo apt-get update; \
		sudo apt-get install -y python3 python3-pip git build-essential; \
		sudo apt-get install -y linux-tools-common linux-tools-generic; \
	elif command -v yum >/dev/null 2>&1; then \
		echo "Detected RHEL/CentOS/Fedora system"; \
		sudo yum install -y python3 python3-pip git gcc make; \
		sudo yum install -y kernel-tools kernel-devel; \
	else \
		echo "Unsupported package manager. Please install dependencies manually."; \
		exit 1; \
	fi
	@echo "🐍 Installing Python dependencies..."
	@pip3 install pandas
	@echo "✅ Dependencies installed successfully!"

# Install rt-app (if not already installed)
install-rtapp:
	@echo "🛠️  Installing rt-app..."
	@if command -v rt-app >/dev/null 2>&1; then \
		echo "rt-app is already installed"; \
	else \
		echo "Cloning and building rt-app..."; \
		git clone https://github.com/scheduler-tools/rt-app.git; \
		cd rt-app && make && sudo make install; \
		cd .. && rm -rf rt-app; \
	fi

# Test taskset generation
test-generate:
	@echo "🧪 Testing taskset generation..."
	@python3 generate_taskset.py --config example_config.json -v
	@echo "✅ Generation test completed!"

# Test schedulability checking
test-check:
	@echo "🧪 Testing schedulability checking..."
	@if [ -f "taskset.json" ]; then \
		python3 schedulability_checker.py taskset.json; \
	else \
		echo "No taskset.json found. Running generation first..."; \
		$(MAKE) test-generate; \
		python3 schedulability_checker.py taskset.json; \
	fi
	@echo "✅ Schedulability check test completed!"

# Test log analysis (if logs exist)
test-analyze:
	@echo "🧪 Testing log analysis..."
	@if ls taskset_log-task_*-*.log 1> /dev/null 2>&1; then \
		python3 analyze_logs.py; \
		echo "✅ Log analysis test completed!"; \
	else \
		echo "⚠️  No log files found. Run rt-app first to generate logs."; \
		echo "   Example: rt-app taskset.json"; \
	fi

# Run complete test workflow
test: test-generate test-check
	@echo "🧪 Complete test workflow completed!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run: rt-app taskset.json"
	@echo "  2. Analyze: python3 analyze_logs.py"

# Install toolkit to system PATH
install:
	@echo "📦 Installing toolkit to system PATH..."
	@sudo cp generate_taskset.py /usr/local/bin/generate_taskset
	@sudo cp schedulability_checker.py /usr/local/bin/schedulability_checker
	@sudo cp analyze_logs.py /usr/local/bin/analyze_logs
	@sudo cp check_deps.py /usr/local/bin/check_deps
	@sudo chmod +x /usr/local/bin/generate_taskset
	@sudo chmod +x /usr/local/bin/schedulability_checker
	@sudo chmod +x /usr/local/bin/analyze_logs
	@sudo chmod +x /usr/local/bin/check_deps
	@echo "✅ RT-Audit installed successfully!"
	@echo "   Commands available: generate_taskset, schedulability_checker, analyze_logs, check_deps"

# Uninstall toolkit from system PATH
uninstall:
	@echo "🗑️  Uninstalling RT-Audit from system PATH..."
	@sudo rm -f /usr/local/bin/generate_taskset
	@sudo rm -f /usr/local/bin/schedulability_checker
	@sudo rm -f /usr/local/bin/analyze_logs
	@sudo rm -f /usr/local/bin/check_deps
	@echo "✅ RT-Audit uninstalled successfully!"

# Clean generated files
clean:
	@echo "🧹 Cleaning generated files..."
	@rm -f taskset.json example_taskset.json
	@rm -f taskset_log-*
	@echo "✅ Cleanup completed!"

# Deep clean (remove all generated and temporary files)
distclean: clean
	@echo "🧹 Deep cleaning..."
	@rm -f *.pyc __pycache__/* .*.swp
	@rm -rf __pycache__
	@echo "✅ Deep cleanup completed!"

# Show system information
info:
	@echo "ℹ️  System Information:"
	@echo "OS: $(shell uname -s)"
	@echo "Architecture: $(shell uname -m)"
	@echo "Kernel: $(shell uname -r)"
	@echo "Python: $(shell python3 --version)"
	@echo "Git: $(shell git --version 2>/dev/null || echo "Not installed")"
	@echo "rt-app: $(shell rt-app --help 2>/dev/null | head -1 || echo "Not installed")"

# Quick setup (check deps and install if needed)
setup: check-deps
	@echo ""
	@echo "🚀 RT-Audit setup completed!"
	@echo "Run 'make test' to verify everything works correctly."
