#!/usr/bin/env python3
"""
RT-Audit: Real-Time Taskset Auditor
Performance Log Analyzer for SCHED_DEADLINE Testing

This script analyzes rt-app execution logs to provide performance metrics,
deadline miss detection, and statistical analysis of real-time behavior.
"""

import os
import glob
import re
import pandas as pd

def print_detailed_stats(title, series, period=None, runtime=None, show_percentage=False):
    """Helper function to print a formatted block of statistics for a pandas Series."""
    # Choose percentiles based on the metric type
    if "Slack" in title:
        # For slack time, we want 5th and 10th percentiles (worst-case scenarios)
        stats = series.describe(percentiles=[.05, .10])
        p1_label = "5th Pct"
        p2_label = "10th Pct"
        p1_key = "5%"
        p2_key = "10%"
    else:
        # For other metrics (like wakeup latency), we want 95th and 99th percentiles (worst-case scenarios)
        stats = series.describe(percentiles=[.95, .99])
        p1_label = "95th Pct"
        p2_label = "99th Pct"
        p1_key = "95%"
        p2_key = "99%"
    
    print(f"    {title} (µs):")
    
    # Calculate percentage if period and runtime are provided
    if show_percentage and period is not None and runtime is not None:
        available_time = period - runtime
        if available_time > 0:
            min_pct = (stats.get('min', 0) / available_time) * 100
            avg_pct = (stats.get('mean', 0) / available_time) * 100
            max_pct = (stats.get('max', 0) / available_time) * 100
            p1_pct = (stats.get(p1_key, 0) / available_time) * 100
            p2_pct = (stats.get(p2_key, 0) / available_time) * 100
            
            print(f"      - Min:    {stats.get('min', 0):>10.2f} ({min_pct:>6.1f}%)")
            print(f"      - Avg:    {stats.get('mean', 0):>10.2f} ({avg_pct:>6.1f}%)")
            print(f"      - Max:    {stats.get('max', 0):>10.2f} ({max_pct:>6.1f}%)")
            print(f"      - Std Dev:{stats.get('std', 0):>10.2f}")
            print(f"      - {p1_label}: {stats.get(p1_key, 0):>10.2f} ({p1_pct:>6.1f}%)")
            print(f"      - {p2_label}: {stats.get(p2_key, 0):>10.2f} ({p2_pct:>6.1f}%)")
        else:
            # Fallback to absolute values if calculation not possible
            print(f"      - Min:    {stats.get('min', 0):>10.2f}")
            print(f"      - Avg:    {stats.get('mean', 0):>10.2f}")
            print(f"      - Max:    {stats.get('max', 0):>10.2f}")
            print(f"      - Std Dev:{stats.get('std', 0):>10.2f}")
            print(f"      - {p1_label}: {stats.get(p1_key, 0):>10.2f}")
            print(f"      - {p2_label}: {stats.get(p2_key, 0):>10.2f}")
    else:
        print(f"      - Min:    {stats.get('min', 0):>10.2f}")
        print(f"      - Avg:    {stats.get('mean', 0):>10.2f}")
        print(f"      - Max:    {stats.get('max', 0):>10.2f}")
        print(f"      - Std Dev:{stats.get('std', 0):>10.2f}")
        print(f"      - {p1_label}: {stats.get(p1_key, 0):>10.2f}")
        print(f"      - {p2_label}: {stats.get(p2_key, 0):>10.2f}")


def analyze_logs():
    """
    Analyzes rt-app log files in the current directory to provide per-task
    and aggregate statistics on performance, including deadline misses.
    """
    log_files = glob.glob("*.log")

    if not log_files:
        print("No rt-app log files found in the current directory.")
        print("Please run this script in the same directory as your log files.")
        return

    all_task_stats = {}
    all_dfs = []

    # --- 1. Process Each Log File Individually ---
    for log_file in log_files:
        # Extract the task name from the filename using a regular expression
        match = re.search(r'(\w+)_log-(\w+)-\d+\.log', log_file)
        if not match:
            continue
        task_name = match.group(2)

        try:
            # Use pandas to read the log file.
            # We use sep='\s+' for whitespace delimiters and explicitly handle the
            # commented header by reading it and then renaming the first column.
            df = pd.read_csv(log_file, sep=r'\s+')
            
            # The first column is read as '#idx', so we rename it.
            df.rename(columns={'#idx': 'idx'}, inplace=True)

            all_dfs.append(df)
            
            # --- 2. Calculate Per-Task Statistics ---
            
            # Deadline misses occur when slack is negative
            deadline_misses = df[df['slack'] < 0]
            num_misses = len(deadline_misses)
            
            # Find the worst deadline miss (most negative slack)
            max_slack_violation = deadline_misses['slack'].min() if num_misses > 0 else 0

            # Extract period and configured runtime information for percentage calculations
            # Use the first row values as they should be consistent for the task
            if len(df) > 0:
                period = df.iloc[0].get('c_period', None)
                configured_runtime = df.iloc[0].get('c_duration', None)
            else:
                period = None
                configured_runtime = None

            # Store detailed statistics for slack and wakeup latency
            task_stats = {
                'deadline_misses': num_misses,
                'max_slack_violation_us': max_slack_violation,
                'slack_series': df['slack'],
                'wu_lat_series': df['wu_lat'],
                'period': period,
                'configured_runtime': configured_runtime
            }
            
            all_task_stats[task_name] = task_stats

        except Exception as e:
            print(f"Could not process file {log_file}: {e}")

    if not all_task_stats:
        print("No valid task data could be extracted from the log files.")
        return

    # --- 3. Print Per-Task Summaries ---
    print("--- Per-Task Execution Summary ---")
    # Sort tasks by name for consistent output
    for task_name in sorted(all_task_stats.keys()):
        stats = all_task_stats[task_name]
        print(f"\n📊 Task: {task_name}")
        print(f"  - Deadline Misses: {stats['deadline_misses']}")
        if stats['deadline_misses'] > 0:
            print(f"  - Max Slack Violation: {stats['max_slack_violation_us']:.2f} µs")
        
        # Show task configuration if available
        if stats['period'] is not None and stats['configured_runtime'] is not None:
            available_time = stats['period'] - stats['configured_runtime']
            print(f"  - Configuration: period={stats['period']} µs, runtime={stats['configured_runtime']} µs, slack={available_time} µs")
        
        print_detailed_stats("Slack Time", stats['slack_series'], 
                           stats['period'], stats['configured_runtime'], show_percentage=True)
        print_detailed_stats("Wakeup Latency", stats['wu_lat_series'])


    # --- 4. Aggregate and Print Overall Summary ---
    if not all_dfs:
        return
        
    combined_df = pd.concat(all_dfs, ignore_index=True)
    total_misses = (combined_df['slack'] < 0).sum()
    
    print("\n" + "="*45)
    print("--- Overall Taskset Summary ---")
    print(f"Total Deadline Misses: {total_misses}")
    if total_misses > 0:
        worst_violation = combined_df[combined_df['slack'] < 0]['slack'].min()
        print(f"Worst Slack Violation: {worst_violation:.2f} µs")
    
    print_detailed_stats("Overall Wakeup Latency", combined_df['wu_lat'])
    print("="*45)


def main():
    """
    Main function to run the log analyzer.
    """
    analyze_logs()

if __name__ == "__main__":
    main()
