# Simple Taskset Converter for RT-App

A human-friendly way to specify real-time tasksets that automatically converts to rt-app JSON format.

## 🎯 **Why This Tool?**

The standard rt-app JSON format is quite verbose and complex:
```json
{
    "global": {
        "duration": 30,
        "default_policy": "SCHED_DEADLINE",
        "log_basename": "taskset_log"
    },
    "tasks": {
        "task_0": {
            "policy": "SCHED_DEADLINE",
            "dl-runtime": 1000,
            "dl-period": 10000,
            "dl-deadline": 10000,
            "cpus": [0, 1, 2, 3],
            "phases": {
                "phase_0": {
                    "loop": -1,
                    "runtime": 1000,
                    "timer": {
                        "ref": "unique",
                        "period": 10000,
                        "mode": "absolute"
                    }
                }
            }
        }
    }
}
```

**With the simple converter, you can write:**
```yaml
cpus: 4
duration: 30
tasks:
  - name: "audio_task"
    runtime: 1000
    period: 10000
```

## 🚀 **Quick Start**

### 1. Create Example Files
```bash
python3 simple_taskset.py --create-examples
```

### 2. Convert Your Taskset
```bash
# From CSV
python3 simple_taskset.py tasks.csv -o rtapp_taskset.json

# From YAML  
python3 simple_taskset.py tasks.yaml -o rtapp_taskset.json

# From Python
python3 simple_taskset.py tasks.py -o rtapp_taskset.json
```

### 3. Validate Schedulability
```bash
python3 schedulability_checker.py rtapp_taskset.json
```

## 📝 **Input Formats**

### 1. **CSV Format** (Ultra-Simple)
```csv
task_name,runtime_us,period_us,deadline_us
audio_task,1000,10000,10000
video_task,5000,20000,20000
control_task,500,5000,4000
network_task,2000,15000,15000
```

**Advantages:**
- ✅ Easiest to write manually
- ✅ Can be created in Excel/Google Sheets
- ✅ Simple copy-paste from documentation
- ✅ Version control friendly

**Usage:**
```bash
python3 simple_taskset.py tasks.csv -o output.json
```

### 2. **YAML Format** (Human-Readable)
```yaml
cpus: 4
duration: 30
tasks:
  - name: "audio_task"
    runtime: 1000      # microseconds
    period: 10000      # microseconds
    deadline: 10000    # microseconds (optional)
    
  - name: "video_task"
    runtime: 5000
    period: 20000      # deadline defaults to period
    
  - name: "control_task"
    runtime: 500
    period: 5000
    deadline: 4000     # constrained deadline
```

**Advantages:**
- ✅ Very readable
- ✅ Supports comments
- ✅ Flexible structure
- ✅ Good for complex configurations

**Usage:**
```bash
python3 simple_taskset.py tasks.yaml -o output.json
```

### 3. **Python Format** (Programmatic)
```python
#!/usr/bin/env python3
from simple_taskset import convert_and_save

taskset = {
    "cpus": 4,
    "duration": 30,
    "tasks": [
        {"name": "audio_task", "runtime": 1000, "period": 10000, "deadline": 10000},
        {"name": "video_task", "runtime": 5000, "period": 20000},
        {"name": "control_task", "runtime": 500, "period": 5000, "deadline": 4000},
        {"name": "network_task", "runtime": 2000, "period": 15000}
    ]
}

# Convert and save
convert_and_save(taskset, "generated_taskset.json")
print("Taskset converted and saved!")
```

**Advantages:**
- ✅ Full Python power
- ✅ Can generate tasks programmatically
- ✅ Easy to modify and iterate
- ✅ Good for research and automation

**Usage:**
```bash
python3 tasks.py  # Runs the script directly
# OR
python3 simple_taskset.py tasks.py -o output.json
```

## 🔧 **Parameters**

### **Global Parameters**
- **`cpus`**: Number of CPUs (default: 4)
- **`duration`**: Test duration in seconds (default: 30)
- **`lock_pages`**: Lock memory pages in RAM (default: true)
- **`ftrace`**: Ftrace logging categories (default: "none")
- **`system_overhead`**: System overhead as fraction 0.0-1.0 (default: 0.02)

### **System Configuration Options**

#### **lock_pages**
- **Purpose**: Prevents memory pages from being swapped to disk
- **Values**: `true` (default) or `false`
- **Impact**: Critical for real-time performance, prevents page faults during execution

#### **ftrace**
- **Purpose**: Enables Linux kernel tracing for debugging and analysis
- **Values**: 
  - `"none"` (default) - No tracing
  - `"main"` - Main thread tracing
  - `"task"` - Task-level tracing
  - `"run"` - Runtime tracing
  - `"loop"` - Loop iteration tracing
  - `"stats"` - Statistics collection
  - Comma-separated list: `"main,task,run"`

#### **system_overhead**
- **Purpose**: Accounts for scheduler and system overhead
- **Values**: 0.0 to 1.0 (default: 0.02 = 2%)
- **Impact**: Automatically scales up dl-runtime to ensure deadlines are met
- **Example**: With 5% overhead, a 1000µs runtime becomes 1053µs dl-runtime

### **Task Parameters**
- **`name`**: Task identifier (default: auto-generated)
- **`runtime`**: **Actual required execution time** in microseconds (required)
- **`period`**: Task period in microseconds (required)
- **`deadline`**: Absolute deadline in microseconds (optional, defaults to period)

**Note**: The `runtime` field specifies the **actual execution time needed**. The system automatically calculates the appropriate `dl-runtime` by scaling up to account for system overhead, ensuring deadlines are met.

## 📊 **Real-World Examples**

### **Audio/Video Processing System**
```yaml
cpus: 8
duration: 60
tasks:
  - name: "audio_input"
    runtime: 500
    period: 5000      # 200Hz audio processing
    
  - name: "audio_output"
    runtime: 300
    period: 5000
    
  - name: "video_decode"
    runtime: 8000
    period: 33333     # 30fps video
    
  - name: "video_encode"
    runtime: 12000
    period: 33333
    
  - name: "network_tx"
    runtime: 2000
    period: 10000     # 100Hz network
    
  - name: "network_rx"
    runtime: 1500
    period: 10000
```

### **Control System**
```yaml
cpus: 4
duration: 120
tasks:
  - name: "sensor_read"
    runtime: 100
    period: 1000      # 1kHz sensor reading
    
  - name: "control_loop"
    runtime: 500
    period: 2000      # 500Hz control loop
    
  - name: "actuator_drive"
    runtime: 200
    period: 2000
    
  - name: "safety_monitor"
    runtime: 300
    period: 10000     # 100Hz safety check
```

### **Embedded System**
```csv
task_name,runtime_us,period_us,deadline_us
led_blink,50,1000000,1000000
adc_read,100,10000,10000
uart_tx,200,50000,50000
uart_rx,150,50000,50000
spi_comm,500,20000,20000
```

### **System Configuration Example**
```yaml
# High-performance real-time system
cpus: 8
duration: 120
lock_pages: true                    # Prevent page faults
ftrace: "main,task,run,stats"       # Comprehensive tracing
system_overhead: 0.05               # 5% overhead for scheduler

tasks:
  - name: "critical_sensor"
    runtime: 100                    # Actually needs 100µs
    period: 1000                     # 1kHz critical path
    
  - name: "control_loop"
    runtime: 500                    # Actually needs 500µs
    period: 2000                     # 500Hz control
    
  - name: "data_logger"
    runtime: 1000                   # Actually needs 1000µs
    period: 10000                    # 100Hz logging
```

**System Overhead Scaling**:
- `critical_sensor`: runtime 100µs → dl-runtime 105µs (5% increase)
- `control_loop`: runtime 500µs → dl-runtime 526µs (5.2% increase)  
- `data_logger`: runtime 1000µs → dl-runtime 1053µs (5.3% increase)

The system automatically ensures that each task gets enough `dl-runtime` to complete its actual `runtime` work within the deadline, accounting for scheduler overhead.

## 🎛️ **Command-Line Options**

```bash
python3 simple_taskset.py [OPTIONS] INPUT_FILE

Options:
  INPUT_FILE              Input file (CSV, YAML, or Python)
  -o, --output FILE      Output JSON file (default: taskset.json)
  --create-examples      Create example input files
  --format FORMAT        Input format: auto, csv, yaml, python (default: auto)
  -h, --help            Show help message

Examples:
  # Auto-detect format
  python3 simple_taskset.py tasks.csv -o output.json
  
  # Force format
  python3 simple_taskset.py tasks.txt --format yaml -o output.json
  
  # Create examples
  python3 simple_taskset.py --create-examples
```

## 🔄 **Complete Workflow**

### **1. Design Your Taskset**
```yaml
# design.yaml
cpus: 4
duration: 30
tasks:
  - name: "task_a"
    runtime: 1000
    period: 10000
    
  - name: "task_b" 
    runtime: 2000
    period: 15000
```

### **2. Convert to RT-App Format**
```bash
python3 simple_taskset.py design.yaml -o rtapp_taskset.json
```

### **3. Validate Schedulability**
```bash
python3 schedulability_checker.py rtapp_taskset.json
```

### **4. Run RT-App Test**
```bash
rt-app rtapp_taskset.json
```

### **5. Analyze Results**
```bash
python3 analyze_logs.py
```

## 🎯 **Best Practices**

### **Naming Conventions**
- Use descriptive names: `audio_input`, `video_decode`, `control_loop`
- Avoid generic names: `task1`, `thread_a`, `process_1`

### **Timing Units**
- Always specify units in comments
- Use microseconds for precision
- Common periods: 1000µs (1kHz), 10000µs (100Hz), 1000000µs (1Hz)

### **Task Organization**
- Group related tasks together
- Order by frequency (highest to lowest)
- Use consistent naming patterns

### **Documentation**
- Add comments explaining task purpose
- Document timing requirements
- Include system constraints

## 🚨 **Common Pitfalls**

### **1. Unit Confusion**
```yaml
# ❌ Wrong - mixing units
tasks:
  - name: "task1"
    runtime: 1        # Is this 1µs, 1ms, or 1s?
    period: 10000     # microseconds
    
# ✅ Correct - consistent units
tasks:
  - name: "task1"
    runtime: 1000     # microseconds
    period: 10000     # microseconds
```

### **2. Missing Required Fields**
```yaml
# ❌ Wrong - missing runtime
tasks:
  - name: "task1"
    period: 10000
    
# ✅ Correct - all required fields
tasks:
  - name: "task1"
    runtime: 1000
    period: 10000
```

### **3. Invalid Timing**
```yaml
# ❌ Wrong - runtime > period
tasks:
  - name: "task1"
    runtime: 15000    # 15ms
    period: 10000     # 10ms - impossible!
    
# ✅ Correct - runtime < period
tasks:
  - name: "task1"
    runtime: 5000     # 5ms
    period: 10000     # 10ms
```

## 🔍 **Troubleshooting**

### **Conversion Errors**
```bash
# Check file format
file tasks.csv

# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('tasks.yaml'))"

# Check Python syntax
python3 -m py_compile tasks.py
```

### **Validation Issues**
```bash
# Test with simple taskset first
python3 simple_taskset.py --create-examples
python3 simple_taskset.py example_taskset.csv -o test.json
python3 schedulability_checker.py test.json
```

### **RT-App Errors**
```bash
# Check JSON syntax
python3 -m json.tool rtapp_taskset.json

# Validate against rt-app requirements
rt-app --validate rtapp_taskset.json
```

## 📚 **Advanced Usage**

### **Programmatic Generation**
```python
import random
from simple_taskset import convert_and_save

def generate_random_taskset(num_tasks, total_util):
    tasks = []
    for i in range(num_tasks):
        runtime = random.randint(100, 5000)
        period = random.randint(5000, 50000)
        tasks.append({
            "name": f"random_task_{i}",
            "runtime": runtime,
            "period": period
        })
    
    return {
        "cpus": 4,
        "duration": 30,
        "tasks": tasks
    }

# Generate and convert
taskset = generate_random_taskset(10, 0.8)
convert_and_save(taskset, "random_taskset.json")
```

### **Batch Processing**
```bash
# Convert multiple files
for file in *.yaml; do
    python3 simple_taskset.py "$file" -o "${file%.yaml}.json"
done

# Validate all converted files
for file in *.json; do
    echo "Checking $file..."
    python3 schedulability_checker.py "$file"
done
```

## 🤝 **Integration with Existing Tools**

### **Makefile Integration**
```makefile
# Add to your Makefile
convert-taskset:
	python3 simple_taskset.py $(INPUT) -o $(OUTPUT)

validate-taskset:
	python3 schedulability_checker.py $(TASKSET)

test-taskset: convert-taskset validate-taskset
	rt-app $(OUTPUT)
```

### **CI/CD Integration**
```yaml
# GitHub Actions example
- name: Convert and Validate Taskset
  run: |
    python3 simple_taskset.py design.yaml -o rtapp_taskset.json
    python3 schedulability_checker.py rtapp_taskset.json
```

## 📖 **References**

- **RT-App Documentation**: [https://github.com/scheduler-tools/rt-app](https://github.com/scheduler-tools/rt-app)
- **SCHED_DEADLINE**: Linux kernel real-time scheduler
- **Real-Time Scheduling**: Theory and practice of real-time systems

---

**Simple Taskset Converter**: Making real-time system design accessible and human-friendly.
