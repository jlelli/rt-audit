# RT-Audit: Real-Time Taskset Auditor

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Kernel 3.14+](https://img.shields.io/badge/kernel-3.14+-green.svg)](https://www.kernel.org/)

**RT-Audit** is a comprehensive toolkit for auditing and verifying the performance and schedulability of real-time tasksets using the Linux SCHED_DEADLINE scheduler. It provides tools for generating synthetic workloads, validating theoretical schedulability, executing real-time tests, and analyzing performance results.

## 🎯 Purpose

RT-Audit enables Linux kernel developers, real-time system engineers, and researchers to:

- **Generate** realistic SCHED_DEADLINE workloads for testing
- **Validate** theoretical schedulability using proven algorithms
- **Execute** real-time tests with rt-app framework
- **Analyze** performance metrics and deadline compliance
- **Audit** real-time system behavior under various load conditions

## 🏗️ Architecture

RT-Audit consists of four core components that work together to provide end-to-end real-time testing:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Generation    │───▶│   Validation     │───▶│   Execution     │───▶│    Analysis     │
│                 │    │                  │    │                 │    │                 │
│ generate_taskset│    │schedulability_   │    │     rt-app      │    │  analyze_logs   │
│                 │    │  checker         │    │                 │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Components

### 1. **generate_taskset.py** - Workload Generator
- **UUniFast Algorithm**: Generates realistic task utilizations
- **SCHED_DEADLINE Support**: Creates rt-app compatible JSON configurations
- **Event Type Support**: Supports `run` and `runtime` workload events
- **Configurable Parameters**: CPU count, task count, periods, utilizations
- **System Overhead**: Accounts for real-world scheduling overhead
- **Flexible Input**: Command-line arguments and configuration files

### 1.5. **simple_taskset.py** - Human-Friendly Converter
- **Multiple Formats**: Supports CSV, YAML, and Python input formats
- **Easy Specification**: Simple, intuitive task definition syntax
- **Event Type Support**: Configurable workload events (`run`, `runtime`)
- **Auto-Conversion**: Automatically generates full rt-app JSON format
- **Manual Design**: Perfect for manually designing specific tasksets

### 2. **schedulability_checker.py** - Theoretical Validator
- **GFB Test**: Goossens, Funk, and Baruah schedulability test
- **BCL Test**: Bertogna, Cirinei, and Lipari schedulability test
- **Global EDF**: Validates multiprocessor real-time scheduling
- **Utilization Analysis**: Per-task and aggregate utilization metrics
- **Constraint Validation**: Ensures mathematical feasibility
- **Combined Analysis**: Uses both tests for broader coverage

### 3. **analyze_logs.py** - Performance Analyzer
- **Log Parsing**: Processes rt-app execution logs
- **Deadline Miss Detection**: Identifies timing violations
- **Performance Metrics**: Slack time, wakeup latency analysis
- **Statistical Analysis**: Distribution analysis with percentiles

### 4. **check_deps.py** - Dependency Manager
- **Environment Validation**: Python, kernel, and tool availability
- **Installation Guidance**: Platform-specific package installation
- **Kernel Version Check**: Ensures SCHED_DEADLINE support (≥3.14)
- **Real-time Setup**: System configuration guidance

## 🚀 Quick Start

### Prerequisites
- **Linux Kernel**: ≥3.14 (SCHED_DEADLINE support)
- **Python**: ≥3.6 with pandas
- **rt-app**: Real-time application framework
- **Root Access**: For real-time testing (recommended)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd taskgen

# Check dependencies
./init.sh

# Install system dependencies (if needed)
make install-deps

# Install rt-app (if not available)
make install-rtapp

# Test the complete workflow
make test
```

### Basic Usage
```bash
# 1. Generate a taskset
python3 generate_taskset.py --config example_config.json

# 1.5. OR manually specify a simple taskset
python3 simple_taskset.py design.yaml -o taskset.json

# 2. Validate schedulability (GFB + BCL tests)
python3 schedulability_checker.py taskset.json

# 3. Execute real-time test
rt-app taskset.json

# 4. Analyze results
python3 analyze_logs.py
```

## 📋 Configuration

### Example Configuration
```json
{
    "cpus": 4,
    "tasks": 8,
    "min_period": 20,
    "max_period": 200,
    "max_util": 0.6,
    "system_overhead": 0.03,
    "output": "taskset.json"
}
```

### Command-Line Options
```bash
# Generate with specific parameters
python3 generate_taskset.py -c 4 -n 6 --max-util 0.8 --system-overhead 0.05

# Generate with specific event type
python3 generate_taskset.py -c 4 -n 6 --event-type run --max-util 0.8

# Verbose mode for debugging
python3 generate_taskset.py --config config.json -v

# Convert simple taskset specification
python3 simple_taskset.py design.yaml -o taskset.json

# Create example input files
python3 simple_taskset.py --create-examples

# Check dependencies
python3 check_deps.py

# Get help
make help
```

## 🔧 Advanced Features

### System Overhead Configuration
- **Default**: 2% system overhead
- **Purpose**: Accounts for context switching and scheduling overhead
- **Impact**: Makes runtime smaller than deadline runtime for realism

### Workload Event Types
- **`run`**: Workload-based execution that varies with CPU frequency
- **`runtime`**: Time-based execution with consistent timing regardless of CPU frequency
- **Default**: `runtime` for consistent timing behavior

### Timer Configuration
- **Absolute Mode**: Consistent timing regardless of execution delays
- **Unique References**: Prevents timer conflicts in multi-task scenarios
- **Real-time Behavior**: Mimics actual SCHED_DEADLINE scheduler behavior

### UUniFast Algorithm
- **Realistic Distribution**: Generates utilizations that sum to target total
- **Constraint Satisfaction**: Ensures individual task constraints are met
- **Mathematical Validation**: Prevents impossible constraint combinations

## 📊 Output Analysis

### Schedulability Results
```
✅ The taskset IS SCHEDULABLE according to BOTH tests.
Total Utilization: 2.800
Maximum Task Utilization: 0.600
GFB Schedulability Bound: 3.200

BCL Test Results:
Task: task_0 - BCL schedulable: ✅
Task: task_1 - BCL schedulable: ✅
```

### Performance Metrics
```
📊 Task: task_0
  - Deadline Misses: 0
  - Slack Time (µs): Min: 15.23, Avg: 45.67, Max: 89.12
  - Wakeup Latency (µs): Min: 2.45, Avg: 8.91, Max: 15.67
```

## 🎛️ Makefile Targets

```bash
make help          # Show all available targets
make check-deps    # Check dependencies
make install-deps  # Install system dependencies
make test          # Run complete test workflow
make install       # Install to system PATH
make clean         # Remove generated files
```

## 🔍 Troubleshooting

### Common Issues
1. **Permission Denied**: Run as root for real-time testing
2. **rt-app Not Found**: Install using `make install-rtapp`
3. **Kernel Too Old**: Upgrade to kernel ≥3.14
4. **Python Dependencies**: Install with `pip3 install pandas`

### Debug Mode
```bash
# Enable verbose output
python3 generate_taskset.py --config config.json -v

# Check detailed dependency info
python3 check_deps.py

# View system information
make info
```

## 📚 Technical Details

### SCHED_DEADLINE Parameters
- **dl-runtime**: Maximum execution time within deadline
- **dl-period**: Task period (implicit deadline = period)
- **dl-deadline**: Absolute deadline (defaults to period)
- **Policy**: SCHED_DEADLINE scheduling class

### RT-App Workload Events

#### Run Events (`run`)
- **Behavior**: Executes for a fixed number of loops based on CPU calibration
- **Timing**: Duration varies with CPU frequency and compute capacity
- **Use Case**: CPU-intensive workloads where actual work performed matters more than time
- **Example**: `"run": 1000` executes ~1000 loops regardless of how long it takes

#### Runtime Events (`runtime`)
- **Behavior**: Executes for a fixed amount of time
- **Timing**: Duration is consistent regardless of CPU frequency or compute capacity
- **Use Case**: Real-time applications requiring precise timing guarantees
- **Example**: `"runtime": 1000` executes for exactly 1000 microseconds



### UUniFast Algorithm
- **Purpose**: Generate task utilizations with realistic distribution
- **Constraint**: Σ(utilization_i) = total_utilization
- **Method**: Recursive random sampling with scaling
- **Validation**: Ensures max_task_util constraint satisfaction

### Schedulability Tests

#### GFB (Goossens, Funk, and Baruah) Test
- **Condition**: U_total ≤ m - (m-1) × U_max
- **Where**: m = number of CPUs, U_max = maximum task utilization
- **Applicability**: Global EDF scheduling on multiprocessors
- **Sufficient**: Pass implies schedulability (not necessary)
- **Complexity**: O(n) where n is the number of tasks

#### BCL (Bertogna, Cirinei, and Lipari) Test
- **Condition**: For each task τk, either:
  1. ∑ i ≠ k min(βi, 1 − λk) < m(1 − λk), OR
  2. ∑ i ≠ k min(βi, 1 − λk) = m(1 − λk) AND ∃i ≠ k : 0 < βi ≤ 1 − λk
- **Where**: λk = Ck/Dk, βi = (NiCi + min(Ci, (Dk − NiTi)0)) / Dk
- **Applicability**: Global EDF scheduling, effective for heavy tasks
- **Sufficient**: Pass implies schedulability (not necessary)
- **Complexity**: O(n²) where n is the number of tasks
- **Advantage**: Better detection for high-utilization task sets

#### Combined Approach
- **Strategy**: Apply GFB first (faster), then BCL if needed
- **Coverage**: Broader schedulability detection than either test alone
- **Performance**: O(n²) worst-case, but often much better in practice

## 🤝 Contributing

RT-Audit is designed for the Linux kernel community and real-time systems research. Contributions are welcome:

1. **Bug Reports**: Use GitHub issues
2. **Feature Requests**: Propose enhancements
3. **Code Contributions**: Submit pull requests
4. **Documentation**: Improve README and inline docs

## 📄 License

This project is licensed under the GNU General Public License v2 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Linux Kernel Community**: SCHED_DEADLINE scheduler implementation
- **rt-app Developers**: Real-time application framework
- **Real-time Research**: UUniFast and GFB algorithms
- **SCHED_DEADLINE Maintainers**: Ongoing scheduler development

## 👥 Authors

**RT-Audit** was developed by:

- **Juri Lelli** <juri.lelli@redhat.com> - Main developer and SCHED_DEADLINE maintainer
- **Google Gemini** - AI assistance for code generation and optimization
- **Cursor** - AI-powered code editor for development assistance

## 📞 Support

For questions, issues, or contributions:
- **Repository**: [GitHub Issues](https://github.com/username/taskgen/issues)
- **Documentation**: This README and inline code comments
- **Community**: Linux kernel and real-time systems forums

---

**RT-Audit**: Making real-time system validation accessible and reliable.
