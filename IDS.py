# CSCI262 Assignment 3 Grp T02-12
import sys
import os
import random
import json
import math

# read events file, returns dict
def read_events_file(filename):
    events = {}
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            num_events = int(lines[0].strip())  # First line is the number of events
            events["num"] = num_events              # store number of events in dictionary
            for line in lines[1:num_events + 1]:    # read only the number of events recorded
                parts = line.strip().split(":")
                event_name = parts[0]
                events[event_name] = {
                    "type": parts[1],    # 'C' for continuous, 'D' for discrete
                    "min": int(parts[2]),
                    "max": int(parts[3]),
                    "weight": int(parts[4])
                }
            
    except FileNotFoundError:
        print(f"File not found: {filename}")
        exit(1)

    # display successful message
    input("Events file read completed. Press Enter to proceed to the next step...")
    return events

# read stats file, returns dict
def read_stats_file(filename):
    stats = {}
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            num_stats = int(lines[0].strip())
            stats["num"] = num_stats              # store number of stats in dictionary
            for line in lines[1:num_stats + 1]:   # read only the number of stats recorded
                parts = line.strip().split(":")
                event_name = parts[0]
                mean = float(parts[1])
                std_dev = float(parts[2])

                stats[event_name] = {"mean": mean, "std_dev": std_dev}
                    
    except FileNotFoundError:
        print(f"File not found: {filename}")
        exit(1)
    # display successful message
    input("Stats file read completed. Press Enter to proceed to the next step...")
    return stats

# check for inconsistences between Events.txt and Stats.txt
def check_inconsistencies(events, stats):
    # check if number of events and stats match
    if (len(events) != len(stats)) or (events.get('num') != stats.get('num')):
        print("Inconsistent number of events.")
        sys.exit(0)

    # check if order of items matches
    event_names = list(events.keys())
    stat_names = list(stats.keys())
    event_names.remove("num")
    stat_names.remove("num")

    if event_names != stat_names:
        print("Error: Order or names of events and stats do not match.")
        sys.exit(0)

    # check for and integer/float inconsistencies in standard deviation
    for event_name, stat_data in stats.items():
        if event_name == 'num':
            continue
        
        std_dev = stat_data["std_dev"]

        if events[event_name]["type"] == "D" and not std_dev.is_integer():
            print(f"Warning: Discrete event '{event_name}' has a non-integer standard deviation.")
        elif events[event_name]["type"] == "C" and std_dev.is_integer():
            print(f"Warning: Continuous event '{event_name}' has an integer standard deviation.")
    
    input("Inconsistencies check completed. Press Enter to proceed to the next step...")

def generate_events(events, stats, days):
    print(f"Generating events for {days} days...")
    baseline_events = []    # list to store generated data for all days
    for day in range(1, days + 1):
        daily_events = {"Day": day}     # initialise dictionary for the day

        for event_name, event_details in events.items():
            if event_name == "num":
                continue

            event_type = event_details["type"]
            min_val = event_details["min"]
            max_val = event_details["max"]
            mean = stats[event_name]["mean"]
            std_dev = stats[event_name]["std_dev"]

            if event_type == "D":   # generate discrete event
                value = round(random.gauss(mean, std_dev))
                value = max(min_val, min(value, max_val))   # restrict to min and max read in events
            else:   # generate continuous event
                value = round(random.gauss(mean, std_dev), 2)   # record in 2 decimals
                value = max(min_val, min(value, max_val))

            daily_events[event_name] = value    # add event data to the day's record

        baseline_events.append(daily_events)    # add day's data to list   

    return baseline_events

def calculate_statistics(baseline_events):
    print("Analysing generated events...")
    # extract all event names 
    event_names = [key for key in baseline_events[0].keys() if key != 'Day']
    # initialise total, mean, standard deviation
    totals = {event: 0 for event in event_names}
    counts = len(baseline_events)

    # compute totals
    for day_data in baseline_events:
        for event in event_names:
            totals[event] += day_data[event]

    # compute mean and standard deviation
    stats = {}
    for event in event_names:
        # mean
        mean = totals[event] / counts
        # standard deviation
        variance = sum((day_data[event] - mean) ** 2 for day_data in baseline_events) / counts
        std_dev = math.sqrt(variance)
        
        stats[event] = {"total": totals[event], "mean": round(mean, 2), "stddev": round(std_dev, 2)}
    
    return stats

def anomaly_detection(baseline_stats, baseline_weights, new_events):
    threshold = 2 * sum(baseline_weights.values())
    results = []
    
    for day, daily_events in enumerate(new_events, start=1):
        anomaly_counter = 0
        for event_name, event_data in daily_events.items():
            if event_name not in baseline_stats:
                continue    # skip events not in baseline

            mean = baseline_stats[event_name]["mean"]
            stddev = baseline_stats[event_name]["stddev"]
            weight = baseline_weights[event_name]

            # calculate deviation 
            deviation = abs(event_data - mean) / stddev if stddev > 0 else 0
            anomaly_counter += deviation * weight
        
        # determine status of the day
        status = "!!!FLAGGED!!!" if anomaly_counter >= threshold else "OK"

        # add day's result to list
        results.append({
            "Day": day, 
            "anomaly_counter": round(anomaly_counter, 2),
            "threshold": threshold, 
            "status": status
        })
    
    return results

# save and display data to json files
def save_and_display(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    
    print(f"Data saved to {filename}")
    # display saved content
    with open(filename, "r") as f:
        saved_data = json.load(f)

    print(json.dumps(saved_data, indent=4))

def main():
    if len(sys.argv) < 4:
        print("Usage: IDS Events.tx Stats.txt <Days>")
        return
        
    # input
    events_file, stats_file, days_str = sys.argv[1:4]
    # check whether file exists and is text file
    try:
        if not (os.path.isfile(events_file) and events_file.endswith('.txt')):
            raise FileNotFoundError(f"{events_file} does not exist or is not a .txt file.")
        
        if not (os.path.isfile(stats_file) and stats_file.endswith('.txt')):
            raise FileNotFoundError(f"{stats_file} does not exist or is not a .txt file.")
    except FileNotFoundError as e:
        print(e)
        return
    
    # check whether days input is int
    try:
        days = int(days_str)
        if days <= 0:
            raise ValueError
    except ValueError:
        print("Please input a valid integer for days.")
        return
    
    # step 1 - read events file
    events = read_events_file(events_file)
    # step 2 - read stats file
    stats = read_stats_file(stats_file)
    # step 3 - check for inconsistences
    check_inconsistencies(events, stats) 
    # step 4 - generate events based on baseline stats and write to file
    print("Starting activity engine...")
    baseline_events = generate_events(events, stats, days)
    save_and_display("baseline_logs.json", baseline_events)
    input("Events generation completed. Press Enter to proceed to the next step...")

    # step 5 - calculate statistics based on baseline events
    print("Starting analysis engine...")
    baseline_stats = calculate_statistics(baseline_events)
    save_and_display("baseline_analysis_results.json", baseline_stats)
    input("Calculated statistics printed completed. Press Enter to proceed to the next step...")

    # step 6 - start anomaly detection loop
    # get events weight
    baseline_weights = {key: value['weight'] for key, value in events.items() if key != 'num'}
    while True:
        choice = input("Enter 'c' to continue with a new file or 'q' to quit: ").strip().lower()
        if choice.lower() == 'q':
            print("Exiting IDS. Goodbye!")
            break
        elif choice.lower() == 'c':
            try:
                # prompt for new stats file
                new_stats_file = input("Please enter a new statistics file for anomaly detection: ").strip()
                # check whether file exists and is text file
                if not (os.path.isfile(new_stats_file) and new_stats_file.endswith('.txt')):
                    raise FileNotFoundError(f"{new_stats_file} does not exist or is not a .txt file.")
                # check if days input is int
                new_days = int(input("Enter the number of days to generate activities for anomaly detection: ").strip())
                if new_days <= 0:
                    raise ValueError
            except FileNotFoundError as e:
                print(e)
                continue
            except ValueError:
                print("Please enter a valid integer for days.")
                continue

            # go through process of setup, data generate
            new_stats = read_stats_file(new_stats_file)
            # check_inconsistencies(events, new_stats)
            new_events = generate_events(events, new_stats, new_days)
            save_and_display("anomaly_logs.json", new_events)
            input("Anomaly detection activity data generation completed. Press Enter to proceed to the next step...")

            # detect anomalies
            results = anomaly_detection(baseline_stats, baseline_weights, new_events)
            save_and_display("alerts.json", results)
            input("Anomaly detection results printed completed. Press Enter to proceed to the next step...")
        else: 
            print("Invalid option. Please try again.")
        
if __name__ == "__main__":
    main()
