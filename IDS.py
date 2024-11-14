# CSCI262 Assignment 3 Grp T02-12
import numpy as np
import sys
from typing import List, Tuple

def read_file(filename: str) -> List[List[str]]:
    try:
        with open(filename, 'r') as f:
            return [line.strip().split(":") for line in f]
    except FileNotFoundError:
        print(f"File not found: {filename}")
        sys.exit(0)

def validate_events(events: List[List[str]], stats: List[List[str]]) -> None:
    if len(events) != len(stats) or events[0][0] != stats[0][0]:
        print("Inconsistent number or order of events.")
        sys.exit(0)
    for i, (event, stat) in enumerate(zip(events[1:], stats[1:]), start=1):
        if event[0] != stat[0]:
            print(f"Inconsistent order of events at line {i + 1}.")
            sys.exit(0)

def generate_baseline_events(events: List[List[str]], stats: List[List[str]], days: int) -> List[List[str]]:
    baseline_events = []
    for _ in range(days):
        daily_events = []
        for i in range(1, len(events)):
            mean = float(stats[i][1])
            sd = float(stats[i][2])
            generated = np.random.normal(mean, sd)
            if events[i][1] == "D":
                daily_events.append(str(int(round(generated))))
            else:
                daily_events.append(f"{generated:.2f}")
        baseline_events.append(daily_events)
    return baseline_events

def write_events_to_file(filename: str, baseline_events: List[List[str]], events: List[List[str]]) -> None:
    with open(filename, 'w') as f:
        for day, daily_events in enumerate(baseline_events, start=1):
            f.write(f"Day {day}\n")
            for i, event in enumerate(daily_events):
                f.write(f"{events[i+1][0]} : {event}\n")
            f.write("\n")

def calculate_statistics(baseline_events: List[List[str]]) -> Tuple[np.ndarray, np.ndarray]:
    numeric_events = np.array(baseline_events, dtype=float)
    means = numeric_events.mean(axis=0)
    std_devs = numeric_events.std(axis=0)
    return means, std_devs

def write_statistics(filename: str, means: np.ndarray, std_devs: np.ndarray, events: List[List[str]]) -> None:
    with open(filename, 'w') as f:
        for i, (mean, sd) in enumerate(zip(means, std_devs)):
            if events[i + 1][1] == "D":
                f.write(f"{events[i+1][0]}:{int(round(mean))}:{sd:.2f}\n")
            else:
                f.write(f"{events[i+1][0]}:{mean:.2f}:{sd:.2f}\n")

def anomaly_report(days: int, baseline_events: List[List[str]], events: List[List[str]], baseline_stats: List[List[str]]) -> None:
    with open("Anomaly_Report.txt", 'w') as f:
        for day, daily_events in enumerate(baseline_events, start=1):
            anomaly_counter = 0.0
            weight_sum = 0
            f.write(f"Day {day}\n")
            for i, value in enumerate(daily_events):
                mean = float(baseline_stats[i][1])
                sd = float(baseline_stats[i][2])
                weight = int(events[i + 1][4])
                deviation = abs(float(value) - mean) / sd
                anomaly_counter += deviation * weight
                weight_sum += weight
            threshold = weight_sum * 2
            f.write(f"Anomaly counter: {anomaly_counter:.1f}\n")
            f.write(f"Threshold: {threshold}\n")
            f.write("Anomaly detected.\n" if anomaly_counter >= threshold else "No anomaly detected.\n")
            f.write("\n")

def main():
    if len(sys.argv) < 4:
        print("Usage: python ids.py <events_file> <stats_file> <days>")
        return
        
    # input
    events_file, stats_file, days_str = sys.argv[1:4]
    
    try:
        days = int(days_str)
        if days <= 0:
            raise ValueError("Days must be a positive integer.")
    except ValueError:
        print("Please input a valid integer for days.")
        return

    events = read_file(events_file)
    stats = read_file(stats_file)
    validate_events(events, stats)

    baseline_events = generate_baseline_events(events, stats, days)
    write_events_to_file("Baseline_Events.txt", baseline_events, events)

    means, std_devs = calculate_statistics(baseline_events)
    write_statistics("Baseline_Stats.txt", means, std_devs, events)

    # Load baseline stats for anomaly reporting
    baseline_stats = read_file("Baseline_Stats.txt")
    anomaly_report(days, baseline_events, events, baseline_stats)
    
    while True:
        choice = input("Enter 'c' to continue with a new file or 'q' to quit: ").strip().lower()
        if choice == 'q':
            break
        elif choice == 'c':
            stats_file = input("Enter new statistics file: ").strip()
            try:
                days = int(input("Enter number of days: ").strip())
            except ValueError:
                print("Please enter a valid integer for days.")
                continue
            stats = read_file(stats_file)
            validate_events(events, stats)
            baseline_events = generate_baseline_events(events, stats, days)
            write_events_to_file("Live_Events.txt", baseline_events, events)
            anomaly_report(days, baseline_events, events, baseline_stats)
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
