#!/usr/bin/env python3
"""
RT-Audit: Real-Time Taskset Auditor
Schedulability Checker for SCHED_DEADLINE Tasksets

This script validates the theoretical schedulability of real-time tasksets
using the GFB (Goossens, Funk, and Baruah) test for global EDF scheduling.
"""

import json
import argparse
import os

def check_gfb_schedulability(taskset_file):
    """
    Checks if a given rt-app taskset is schedulable according to the GFB test.

    The GFB (Goossens, Funk, and Baruah) test is a utilization-based test for
    global EDF scheduling on multiprocessors. The condition is:
    U_total <= m - (m - 1) * U_max
    where:
    - U_total is the sum of the utilizations of all tasks.
    - m is the number of processors.
    - U_max is the maximum utilization among all tasks.

    Args:
        taskset_file (str): The path to the rt-app JSON taskset file.

    Returns:
        None. Prints the result of the schedulability test.
    """
    if not os.path.exists(taskset_file):
        print(f"Error: Taskset file not found at '{taskset_file}'")
        return

    try:
        with open(taskset_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{taskset_file}'")
        return

    tasks = data.get("tasks", {})
    if not tasks:
        print("No tasks found in the provided file.")
        return

    # --- 1. Extract Task Parameters and System Info ---
    
    # Determine the number of CPUs from the affinity of the first task.
    # We assume a global scheduling policy where all tasks can run on any CPU.
    first_task = next(iter(tasks.values()))
    num_cpus = len(first_task.get("cpus", []))
    if num_cpus == 0:
        print("Error: Could not determine the number of CPUs from the taskset.")
        return

    task_utilizations = []
    print("--- Taskset Analysis ---")
    print(f"System has {num_cpus} CPUs.\n")
    print("Individual Task Utilizations:")
    
    for name, params in tasks.items():
        # rt-app uses microseconds for these parameters
        runtime = params.get("dl-runtime")
        period = params.get("dl-period")

        if runtime is None or period is None:
            print(f"Warning: Skipping task '{name}' due to missing runtime or period.")
            continue
            
        if period == 0:
            print(f"Warning: Skipping task '{name}' due to zero period.")
            continue

        utilization = runtime / period
        task_utilizations.append(utilization)
        print(f"- {name}: U = {utilization:.4f}")

    if not task_utilizations:
        print("\nNo valid tasks were found to analyze.")
        return

    # --- 2. Calculate Metrics for GFB Test ---
    total_utilization = sum(task_utilizations)
    max_utilization = max(task_utilizations)

    print("\n--- Schedulability Test ---")
    print(f"Total Utilization (U_total): {total_utilization:.4f}")
    print(f"Maximum Task Utilization (U_max): {max_utilization:.4f}")

    # --- 3. Apply the GFB Schedulability Condition ---
    schedulability_bound = num_cpus - (num_cpus - 1) * max_utilization
    print(f"GFB Schedulability Bound (U_total <= m - (m - 1) * U_max): {schedulability_bound:.4f}")

    is_schedulable = total_utilization <= schedulability_bound

    print("\n--- Result ---")
    if is_schedulable:
        print("✅ The taskset IS SCHEDULABLE according to the GFB test.")
    else:
        print("❌ The taskset IS NOT SCHEDULABLE according to the GFB test.")

def main():
    """
    Main function to parse command-line arguments and run the checker.
    """
    parser = argparse.ArgumentParser(
        description="Check schedulability of an rt-app taskset using the GFB test.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("taskset_file", type=str, help="Path to the rt-app JSON taskset file.")
    
    args = parser.parse_args()
    check_gfb_schedulability(args.taskset_file)

if __name__ == "__main__":
    main()
