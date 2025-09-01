
import streamlit as st
from datetime import datetime, timedelta

# Helper function to parse time strings
def parse_time(time_str):
    return datetime.strptime(time_str, "%H:%M")

# Calculate overlap with 20:00–07:00 window for weekdays
def calculate_weekday_overlap(intervals):
    overlap_minutes = 0
    for start_str, end_str in intervals:
        start = parse_time(start_str)
        end = parse_time(end_str)
        if end <= start:
            end += timedelta(days=1)

        # Define the rest window from 20:00 to 07:00 next day
        rest_start = parse_time("20:00")
        rest_end = parse_time("07:00") + timedelta(days=1)

        # Calculate overlap
        latest_start = max(start, rest_start)
        earliest_end = min(end, rest_end)
        delta = (earliest_end - latest_start).total_seconds() / 60
        if delta > 0:
            overlap_minutes += delta
    return overlap_minutes

# Calculate longest rest period for weekend
def calculate_weekend_rest(intervals):
    # Convert to datetime and sort
    times = []
    for start_str, end_str in intervals:
        start = parse_time(start_str)
        end = parse_time(end_str)
        if end <= start:
            end += timedelta(days=1)
        times.append((start, end))
    times.sort()

    # Add dygnsbryt at 07:00
    dygn_start = parse_time("07:00")
    dygn_end = dygn_start + timedelta(days=1)

    # Add boundary intervals
    times = [(dygn_start, dygn_start)] + times + [(dygn_end, dygn_end)]

    # Calculate rest periods between disturbances
    rest_periods = []
    for i in range(len(times) - 1):
        rest_start = times[i][1]
        rest_end = times[i + 1][0]
        rest_minutes = (rest_end - rest_start).total_seconds() / 60
        rest_periods.append(rest_minutes)

    longest_rest = max(rest_periods) if rest_periods else 0
    missing_minutes = max(0, 11 * 60 - longest_rest)
    return missing_minutes

# Streamlit interface
st.title("Beräkning av kompenserad vila")

num_days = st.number_input("Hur många dygn vill du registrera?", min_value=1, max_value=31, value=1)

total_compensation = 0

for day in range(num_days):
    st.subheader(f"Dygn {day + 1}")
    day_type = st.radio(f"Är detta en vardag eller helg?", ["Vardag", "Helg"], key=f"type_{day}")

    intervals = []
    num_intervals = st.number_input(f"Antal tidsintervall för dygn {day + 1}", min_value=1, max_value=10, value=1, key=f"num_{day}")
    for i in range(num_intervals):
        col1, col2 = st.columns(2)
        with col1:
            start = st.text_input(f"Starttid {i + 1} (HH:MM)", key=f"start_{day}_{i}")
        with col2:
            end = st.text_input(f"Sluttid {i + 1} (HH:MM)", key=f"end_{day}_{i}")
        if start and end:
            intervals.append((start, end))

    if day_type == "Vardag":
        minutes = calculate_weekday_overlap(intervals)
    else:
        minutes = calculate_weekend_rest(intervals)

    st.write(f"Kompenserad tid för dygn {day + 1}: {int(minutes)} minuter")
    total_compensation += minutes

# Subtract 4 hours (240 minutes)
adjusted_total = max(0, total_compensation - 240)
st.markdown(f"### Total kompenserad tid efter avdrag: {int(adjusted_total)} minuter")
