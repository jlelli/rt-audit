#!/usr/bin/env python3
"""
RT-Audit: Real-Time Taskset Auditor
Schedulability Checker for SCHED_DEADLINE Tasksets

This script validates the theoretical schedulability of real-time tasksets
using both GFB (Goossens, Funk, and Baruah) and BCL (Bertogna, Cirinei, and Lipari) 
tests for global EDF scheduling.
"""

import json
import argparse
import os
import math

def check_bcl_schedulability(tasks, num_cpus):
    """
    Checks if a given taskset is schedulable according to the BCL test.
    
    The BCL test is a sufficient, polynomial-time test for global EDF scheduling
    that is particularly effective for task sets containing "heavy" (high utilization) tasks.
    
    For each task τk, the test checks if:
    1. ∑ i ≠ k min(βi, 1 − λk) < m(1 − λk), OR
    2. ∑ i ≠ k min(βi, 1 − λk) = m(1 − λk) AND ∃i ≠ k : 0 < βi ≤ 1 − λk
    
    Where:
    - λk = Ck / Dk (utilization of task τk)
    - βi = (NiCi + min(Ci, (Dk − NiTi)0)) / Dk
    - Ni = ⌊ Dk / Ti ⌋
    - (x)0 = max(0, x)
    
    Args:
        tasks (dict): Dictionary of tasks with their parameters
        num_cpus (int): Number of available CPUs
        
    Returns:
        tuple: (is_schedulable, details) where details contains per-task results
    """
    task_results = {}
    all_schedulable = True
    
    for task_name, task_params in tasks.items():
        runtime = task_params.get("dl-runtime")
        period = task_params.get("dl-period")
        deadline = task_params.get("dl-deadline", period)  # Default to period if deadline not specified
        
        if runtime is None or period is None or deadline is None:
            continue
            
        if period == 0 or deadline == 0:
            continue
            
        # Calculate λk for the current task
        lambda_k = runtime / deadline
        
        # Calculate βi for all other tasks
        beta_sum = 0
        beta_details = {}
        
        for other_name, other_params in tasks.items():
            if other_name == task_name:
                continue
                
            other_runtime = other_params.get("dl-runtime")
            other_period = other_params.get("dl-period")
            other_deadline = other_params.get("dl-deadline", other_period)
            
            if other_runtime is None or other_period is None or other_deadline is None:
                continue
                
            if other_period == 0 or other_deadline == 0:
                continue
            
            # Calculate Ni = ⌊ Dk / Ti ⌋
            Ni = math.floor(deadline / other_period)
            
            # Calculate (Dk − NiTi)0 = max(0, Dk − NiTi)
            remaining_time = max(0, deadline - Ni * other_period)
            
            # Calculate βi = (NiCi + min(Ci, (Dk − NiTi)0)) / Dk
            beta_i = (Ni * other_runtime + min(other_runtime, remaining_time)) / deadline
            
            beta_details[other_name] = beta_i
            beta_sum += min(beta_i, 1 - lambda_k)
        
        # Check BCL conditions
        bound = num_cpus * (1 - lambda_k)
        condition1 = beta_sum < bound
        condition2 = beta_sum == bound and any(0 < beta <= 1 - lambda_k for beta in beta_details.values())
        
        is_task_schedulable = condition1 or condition2
        
        task_results[task_name] = {
            'lambda_k': lambda_k,
            'beta_sum': beta_sum,
            'bound': bound,
            'condition1': condition1,
            'condition2': condition2,
            'is_schedulable': is_task_schedulable,
            'beta_details': beta_details
        }
        
        if not is_task_schedulable:
            all_schedulable = False
    
    return all_schedulable, task_results

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

    print("\n--- GFB Schedulability Test ---")
    print(f"Total Utilization (U_total): {total_utilization:.4f}")
    print(f"Maximum Task Utilization (U_max): {max_utilization:.4f}")

    # --- 3. Apply the GFB Schedulability Condition ---
    schedulability_bound = num_cpus - (num_cpus - 1) * max_utilization
    print(f"GFB Schedulability Bound (U_total <= m - (m - 1) * U_max): {schedulability_bound:.4f}")

    is_gfb_schedulable = total_utilization <= schedulability_bound

    print("\n--- GFB Result ---")
    if is_gfb_schedulable:
        print("✅ The taskset IS SCHEDULABLE according to the GFB test.")
    else:
        print("❌ The taskset IS NOT SCHEDULABLE according to the GFB test.")

    # --- 4. Apply BCL Test ---
    print("\n--- BCL Schedulability Test ---")
    print("BCL (Bertogna, Cirinei, and Lipari) test analysis:")
    
    is_bcl_schedulable, bcl_results = check_bcl_schedulability(tasks, num_cpus)
    
    for task_name, result in bcl_results.items():
        print(f"\nTask: {task_name}")
        print(f"  λk (utilization): {result['lambda_k']:.4f}")
        print(f"  β sum: {result['beta_sum']:.4f}")
        print(f"  Bound: {result['bound']:.4f}")
        print(f"  Condition 1 (β_sum < bound): {result['condition1']}")
        print(f"  Condition 2 (β_sum = bound AND ∃βi > 0): {result['condition2']}")
        print(f"  BCL schedulable: {'✅' if result['is_schedulable'] else '❌'}")
    
    print(f"\n--- BCL Result ---")
    if is_bcl_schedulable:
        print("✅ The taskset IS SCHEDULABLE according to the BCL test.")
    else:
        print("❌ The taskset IS NOT SCHEDULABLE according to the BCL test.")

    # --- 5. Combined Result ---
    print("\n--- Combined Analysis ---")
    if is_gfb_schedulable and is_bcl_schedulable:
        print("✅ The taskset IS SCHEDULABLE according to BOTH tests.")
    elif is_gfb_schedulable:
        print("✅ The taskset IS SCHEDULABLE according to GFB test only.")
    elif is_bcl_schedulable:
        print("✅ The taskset IS SCHEDULABLE according to BCL test only.")
    else:
        print("❌ The taskset IS NOT SCHEDULABLE according to either test.")
        print("Note: This does not guarantee unschedulability - consider Response Time Analysis (RTA) for definitive results.")

def main():
    """
    Main function to parse command-line arguments and run the checker.
    """
    parser = argparse.ArgumentParser(
        description="Check schedulability of an rt-app taskset using GFB and BCL tests.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("taskset_file", type=str, help="Path to the rt-app JSON taskset file.")
    
    args = parser.parse_args()
    check_gfb_schedulability(args.taskset_file)

if __name__ == "__main__":
    main()
