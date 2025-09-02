
import streamlit as st
from datetime import datetime, timedelta

# Helper function to parse time strings
def parse_time(time_str):
    return datetime.strptime(time_str, "%H:%M")

# Calculate overlap with night window (20:00–07:00)
def calculate_weekday_overlap(start, end):
    night_start = parse_time("20:00")
    night_end = parse_time("07:00") + timedelta(days=1)
    if end < start:
        end += timedelta(days=1)
    overlap_start = max(start, night_start)
    overlap_end = min(end, night_end)
    if overlap_end > overlap_start:
        return (overlap_end - overlap_start).total_seconds() / 60
    if start.time() >= night_start.time() or end.time() <= night_end.time():
        # Adjust end time if it is before start (crosses midnight)
        if end < start:
            end += timedelta(days=1)
        overlap_start = max(start, night_start)
        overlap_end = min(end, night_end)
        if overlap_end > overlap_start:
            return (overlap_end - overlap_start).total_seconds() / 60
    return 0

# Calculate longest rest period between intervals
def calculate_weekend_rest(intervals):
    intervals.sort()
    rest_periods = []
    previous_end = parse_time("07:00")
    for start, end in intervals:
        rest_periods.append((start - previous_end).total_seconds() / 60)
        previous_end = end
    rest_periods.append((parse_time("07:00") + timedelta(days=1) - previous_end).total_seconds() / 60)
    longest_rest = max(rest_periods)
    missing_minutes = max(0, 11 * 60 - longest_rest)
    return missing_minutes

# Convert minutes to hours and minutes string
def format_minutes(minutes):
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours}h {mins}m"

# Streamlit UI
st.title("Beräkning av kompenserad vila")
num_days = st.number_input("Antal dygn att registrera", min_value=1, max_value=31, value=1)

total_comp_minutes = 0

for day in range(num_days):
    st.subheader(f"Dygn {day + 1}")
    day_type = st.radio(f"Typ av dygn {day + 1}", ["Vardag", "Helg"], key=f"type_{day}")
    intervals = []
    num_intervals = st.number_input(f"Antal tidsintervall för dygn {day + 1}", min_value=1, max_value=10, value=1, key=f"num_{day}")
    
    for i in range(num_intervals):
        col1, col2 = st.columns(2)
        with col1:
            start_str = st.text_input(f"Starttid {i+1} (HH:MM)", key=f"start_{day}_{i}")
        with col2:
            end_str = st.text_input(f"Sluttid {i+1} (HH:MM)", key=f"end_{day}_{i}")
        if start_str and end_str:
            try:
                start = parse_time(start_str)
                end = parse_time(end_str)
                intervals.append((start, end))
            except:
                st.error("Fel format på tid. Använd HH:MM.")

    if intervals:
        if day_type == "Vardag":
            comp_minutes = sum(calculate_weekday_overlap(start, end) for start, end in intervals)
        else:
            comp_minutes = calculate_weekend_rest(intervals)
        st.write(f"Kompenserad tid för dygn {day + 1}: {format_minutes(comp_minutes)}")
        total_comp_minutes += comp_minutes

# Subtract 4 hours (240 minutes)
adjusted_minutes = max(0, total_comp_minutes - 240)
st.markdown("---")
st.write(f"**Total kompenserad tid (efter avdrag av 4 timmar): {format_minutes(adjusted_minutes)}**")
