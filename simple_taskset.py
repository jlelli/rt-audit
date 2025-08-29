#!/usr/bin/env python3
"""
Simple Taskset Converter for RT-App

Converts human-friendly taskset specifications to rt-app JSON format.
Supports multiple input formats for easy manual specification.
"""

import json
import argparse
import yaml
import csv
import sys
import os

def csv_to_taskset(csv_file):
    """
    Convert CSV format to taskset specification.
    
    Expected CSV format:
    task_name,runtime_us,period_us,deadline_us
    audio_task,1000,10000,10000
    video_task,5000,20000,20000
    
    Args:
        csv_file (str): Path to CSV file
        
    Returns:
        dict: Taskset specification
    """
    taskset = {"cpus": 4, "duration": 30, "tasks": []}
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            task = {
                "name": row["task_name"],
                "runtime": int(row["runtime_us"]),
                "period": int(row["period_us"])
            }
            if "deadline_us" in row and row["deadline_us"]:
                task["deadline"] = int(row["deadline_us"])
            taskset["tasks"].append(task)
    
    return taskset

def yaml_to_taskset(yaml_file):
    """
    Convert YAML format to taskset specification.
    
    Args:
        yaml_file (str): Path to YAML file
        
    Returns:
        dict: Taskset specification
    """
    with open(yaml_file, 'r') as f:
        return yaml.safe_load(f)

def dict_to_taskset(taskset_dict):
    """
    Convert Python dictionary format to taskset specification.
    
    Args:
        taskset_dict (dict): Taskset dictionary
        
    Returns:
        dict: Taskset specification
    """
    return taskset_dict

def convert_to_rtapp(taskset):
    """
    Convert simple taskset specification to rt-app JSON format.
    
    Args:
        taskset (dict): Simple taskset specification
        
    Returns:
        dict: rt-app JSON format
    """
    # Default values
    cpus = taskset.get("cpus", 4)
    duration = taskset.get("duration", 30)
    lock_pages = taskset.get("lock_pages", True)
    ftrace = taskset.get("ftrace", "none")
    system_overhead = taskset.get("system_overhead", 0.02)
    event_type = taskset.get("event_type", "runtime")
    
    # Create rt-app format
    rtapp_config = {
        "global": {
            "duration": duration,
            "default_policy": "SCHED_DEADLINE",
            "log_basename": "taskset_log",
            "lock_pages": lock_pages,
            "ftrace": ftrace
        },
        "tasks": {}
    }
    
    # Convert each task
    for i, task in enumerate(taskset["tasks"]):
        task_name = task.get("name", f"task_{i}")
        runtime = task["runtime"]  # This is the actual required runtime
        period = task["period"]
        deadline = task.get("deadline", period)
        
        # Scale up dl-runtime to account for system overhead
        if system_overhead > 0:
            dl_runtime = int(runtime / (1.0 - system_overhead))
            # Ensure minimum dl-runtime
            dl_runtime = max(dl_runtime, runtime + 10)
        else:
            dl_runtime = runtime
        
        # Create rt-app task structure
        task_config = {
            "policy": "SCHED_DEADLINE",
            "dl-runtime": dl_runtime,      # Scaled up for overhead
            "dl-period": period,
            "dl-deadline": deadline,
            "cpus": list(range(cpus)),
            "phases": {
                f"phase_{i}": {
                    "loop": -1
                }
            }
        }

        # Add workload events based on the specified event type
        if event_type == "run":
            # Use "run" event: workload-based execution (varies with CPU frequency)
            # The run event executes for a fixed number of loops based on calibration
            task_config["phases"][f"phase_{i}"]["run"] = runtime
        elif event_type == "runtime":
            # Use "runtime" event: time-based execution (consistent regardless of CPU frequency)
            # This is the current default behavior
            task_config["phases"][f"phase_{i}"]["runtime"] = runtime
        else:
            # Default to runtime if invalid event_type specified
            task_config["phases"][f"phase_{i}"]["runtime"] = runtime

        # Add timer event AFTER workload events (rt-app requirement)
        task_config["phases"][f"phase_{i}"]["timer"] = {"ref": "unique", "period": period, "mode": "absolute"}

        rtapp_config["tasks"][task_name] = task_config
    
    return rtapp_config

def create_example_files():
    """Create example input files for demonstration."""
    
    # CSV example
    csv_content = """task_name,runtime_us,period_us,deadline_us
audio_task,1000,10000,10000
video_task,5000,20000,20000
control_task,500,5000,4000
network_task,2000,15000,15000"""
    
    with open("example_taskset.csv", "w") as f:
        f.write(csv_content)
    
    # YAML example with runtime events (time-based, consistent timing)
    runtime_yaml_content = """cpus: 4
duration: 30
lock_pages: true
ftrace: "none"
system_overhead: 0.02
event_type: "runtime"
tasks:
  - name: "audio_task"
    runtime: 1000
    period: 10000
    deadline: 10000
    
  - name: "video_task"
    runtime: 5000
    period: 20000
    
  - name: "control_task"
    runtime: 500
    period: 5000
    deadline: 4000
    
  - name: "network_task"
    runtime: 2000
    period: 15000"""
    
    with open("example_runtime.yaml", "w") as f:
        f.write(runtime_yaml_content)

    # YAML example with run events (workload-based, varies with CPU frequency)
    run_yaml_content = """cpus: 4
duration: 30
lock_pages: true
ftrace: "run,loop,stats"
system_overhead: 0.02
event_type: "run"
tasks:
  - name: "cpu_intensive_task"
    runtime: 2000
    period: 8000
    
  - name: "io_bound_task"
    runtime: 500
    period: 12000"""
    
    with open("example_run.yaml", "w") as f:
        f.write(run_yaml_content)


    
    # Python dict example with system configuration and event types
    python_content = """#!/usr/bin/env python3
# Example Python taskset specification with different event types
from simple_taskset import convert_and_save

# Example 1: Runtime events (time-based execution)
runtime_taskset = {
    "cpus": 4,
    "duration": 30,
    "lock_pages": True,
    "ftrace": "none",
    "system_overhead": 0.02,
    "event_type": "runtime",
    "tasks": [
        {"name": "audio_task", "runtime": 1000, "period": 10000, "deadline": 10000},
        {"name": "video_task", "runtime": 5000, "period": 20000},
        {"name": "control_task", "runtime": 500, "period": 5000, "deadline": 4000},
        {"name": "network_task", "runtime": 2000, "period": 15000}
    ]
}

# Example 2: Run events (workload-based execution)
run_taskset = {
    "cpus": 4,
    "duration": 30,
    "lock_pages": True,
    "ftrace": "run,loop,stats",
    "system_overhead": 0.02,
    "event_type": "run",
    "tasks": [
        {"name": "cpu_intensive", "runtime": 2000, "period": 8000},
        {"name": "io_bound", "runtime": 500, "period": 12000}
    ]
}

# Convert and save examples
convert_and_save(runtime_taskset, "runtime_taskset.json")
convert_and_save(run_taskset, "run_taskset.json")

print("Example tasksets converted and saved!")
print("- runtime_taskset.json: Time-based execution (consistent timing)")
print("- run_taskset.json: Workload-based execution (varies with CPU frequency)")"""
    
    with open("example_taskset.py", "w") as f:
        f.write(python_content)
    
    print("Created example files:")
    print("  - example_taskset.csv")
    print("  - example_runtime.yaml (runtime events)")
    print("  - example_run.yaml (run events)")
    print("  - example_taskset.py")

def convert_and_save(taskset, output_file):
    """
    Convert taskset and save to file.
    
    Args:
        taskset (dict): Taskset specification
        output_file (str): Output file path
    """
    rtapp_config = convert_to_rtapp(taskset)
    
    with open(output_file, 'w') as f:
        json.dump(rtapp_config, f, indent=4)
    
    print(f"Converted taskset saved to: {output_file}")
    
    # Print configuration summary
    print(f"\nConfiguration Summary:")
    print(f"  CPUs: {taskset.get('cpus', 4)}")
    print(f"  Duration: {rtapp_config['global']['duration']}s")
    print(f"  Lock Pages: {rtapp_config['global']['lock_pages']}")
    print(f"  Ftrace: {rtapp_config['global']['ftrace']}")
    print(f"  System Overhead: {taskset.get('system_overhead', 0.02):.1%}")
    print(f"  Tasks: {len(rtapp_config['tasks'])}")
    
    # Show system overhead effect
    if taskset.get('system_overhead', 0.02) > 0:
        print(f"  Note: dl-runtime values increased by {taskset.get('system_overhead', 0.02):.1%} to account for system overhead")

def main():
    """Main function to handle command-line usage."""
    parser = argparse.ArgumentParser(
        description="Convert human-friendly taskset specifications to rt-app JSON format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument("input_file", nargs="?", help="Input file (CSV, YAML, or Python)")
    parser.add_argument("-o", "--output", default="taskset.json", help="Output JSON file")
    parser.add_argument("--create-examples", action="store_true", help="Create example input files")
    parser.add_argument("--format", choices=["auto", "csv", "yaml", "python"], default="auto", 
                       help="Input format (auto-detect if not specified)")
    
    args = parser.parse_args()
    
    if args.create_examples:
        create_example_files()
        return
    
    if not args.input_file:
        parser.print_help()
        print("\nExamples:")
        print("  # Convert CSV file")
        print("  python3 simple_taskset.py tasks.csv -o output.json")
        print("\n  # Convert YAML file") 
        print("  python3 simple_taskset.py tasks.yaml -o output.json")
        print("\n  # Convert Python file")
        print("  python3 simple_taskset.py tasks.py -o output.json")
        print("\n  # Create example files")
        print("  python3 simple_taskset.py --create-examples")
        print("\nSystem Configuration Options:")
        print("  lock_pages: true/false (default: true)")
        print("  ftrace: 'none', 'main', 'task', 'run', 'loop', 'stats' or comma-separated list")
        print("  system_overhead: 0.0-1.0 (default: 0.02)")
        return
    
    # Determine input format
    if args.format == "auto":
        if args.input_file.endswith(".csv"):
            args.format = "csv"
        elif args.input_file.endswith((".yml", ".yaml")):
            args.format = "yaml"
        elif args.input_file.endswith(".py"):
            args.format = "python"
        else:
            print(f"Error: Cannot auto-detect format for {args.input_file}")
            print("Please specify format with --format")
            return
    
    # Convert based on format
    try:
        if args.format == "csv":
            taskset = csv_to_taskset(args.input_file)
        elif args.format == "yaml":
            taskset = yaml_to_taskset(args.input_file)
        elif args.format == "python":
            # For Python files, we expect them to define a 'taskset' variable
            with open(args.input_file, 'r') as f:
                exec(f.read())
            if 'taskset' not in locals():
                print("Error: Python file must define a 'taskset' variable")
                return
            taskset = locals()['taskset']
        
        # Convert and save
        convert_and_save(taskset, args.output)
        
    except Exception as e:
        print(f"Error converting {args.input_file}: {e}")
        return

if __name__ == "__main__":
    main()
