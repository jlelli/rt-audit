#!/usr/bin/env python3

import os
import glob
import re
import pandas as pd

def print_detailed_stats(title, series):
    """Helper function to print a formatted block of statistics for a pandas Series."""
    stats = series.describe(percentiles=[.95, .99])
    print(f"    {title} (µs):")
    print(f"      - Min:    {stats.get('min', 0):>10.2f}")
    print(f"      - Avg:    {stats.get('mean', 0):>10.2f}")
    print(f"      - Max:    {stats.get('max', 0):>10.2f}")
    print(f"      - Std Dev:{stats.get('std', 0):>10.2f}")
    print(f"      - 95th Pct:{stats.get('95%', 0):>10.2f}")
    print(f"      - 99th Pct:{stats.get('99%', 0):>10.2f}")


def analyze_logs():
    """
    Analyzes rt-app log files in the current directory to provide per-task
    and aggregate statistics on performance, including deadline misses.
    """
    log_files = glob.glob("taskset_log-task_*-*.log")

    if not log_files:
        print("No rt-app log files found in the current directory.")
        print("Please run this script in the same directory as your log files.")
        return

    all_task_stats = {}
    all_dfs = []

    # --- 1. Process Each Log File Individually ---
    for log_file in log_files:
        # Extract the task name from the filename using a regular expression
        match = re.search(r'taskset_log-(task_\d+)-\d+\.log', log_file)
        if not match:
            continue
        task_name = match.group(1)

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

            # Store detailed statistics for slack and wakeup latency
            task_stats = {
                'deadline_misses': num_misses,
                'max_slack_violation_us': max_slack_violation,
                'slack_series': df['slack'],
                'wu_lat_series': df['wu_lat']
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
        
        print_detailed_stats("Slack Time", stats['slack_series'])
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
    
    print_detailed_stats("Overall Slack Time", combined_df['slack'])
    print_detailed_stats("Overall Wakeup Latency", combined_df['wu_lat'])
    print("="*45)


def main():
    """
    Main function to run the log analyzer.
    """
    analyze_logs()

if __name__ == "__main__":
    main()
