def combine_intervals(intervals1, intervals2):
    """
    Combine two interval lists, accounting for overlapping intervals and their combined interpolation factors.

    Parameters:
    intervals1 (list): First list of interval dictionaries with 'start', 'stop', and 'interp' keys.
    intervals2 (list): Second list of interval dictionaries with 'start', 'stop', and 'interp' keys.

    Returns:
    list: Combined list of interval dictionaries.
    """
    combined_intervals = intervals1 + intervals2
    combined_intervals.sort(key=lambda x: (x['start'], x['stop']))

    result = []
    current_start, current_stop, current_interp = combined_intervals[0]['start'], combined_intervals[0]['stop'], combined_intervals[0]['interp']

    for interval in combined_intervals[1:]:
        if interval['start'] <= current_stop:
            # If intervals overlap
            if interval['start'] > current_start:
                result.append({"start": current_start, "stop": interval['start'], "interp": current_interp})
            current_start = interval['start']
            if interval['stop'] <= current_stop:
                current_interp += interval['interp']
            else:
                result.append({"start": current_start, "stop": current_stop, "interp": current_interp + interval['interp']})
                current_start = current_stop
                current_stop = interval['stop']
                current_interp = interval['interp']
        else:
            result.append({"start": current_start, "stop": current_stop, "interp": current_interp})
            current_start, current_stop, current_interp = interval['start'], interval['stop'], interval['interp']

    result.append({"start": current_start, "stop": current_stop, "interp": current_interp})
    return result

# Example usage
intervals1 = [
    {"start": 2, "stop": 4, "interp": 1},
]

intervals2 = [
    {"start": 7, "stop": 9, "interp": 2},
]

print(intervals1)
print(intervals2)

combined_intervals = combine_intervals(intervals1, intervals2)

# Display the results
for interval in combined_intervals:
    print(f"Start: {interval['start']}, Stop: {interval['stop']}, Interp: {interval['interp']}")
