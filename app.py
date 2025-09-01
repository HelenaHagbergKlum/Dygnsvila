
import streamlit as st
from datetime import datetime, timedelta

# Helper function to parse time strings
def parse_time(time_str):
    return datetime.strptime(time_str, "%H:%M")

# Helper function to calculate duration between two times
def calculate_duration(start, end):
    if end < start:
        end += timedelta(days=1)
    return end - start

# Helper function to format timedelta as hours and minutes
def format_duration(td):
    total_minutes = int(td.total_seconds() // 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}h {minutes}m"

# Streamlit interface
st.title("Beräkning av kompenserad vila enligt 11-timmarsregeln")

num_days = st.number_input("Hur många dygn vill du registrera?", min_value=1, max_value=31, step=1)

total_compensation = timedelta()

for day in range(num_days):
    st.subheader(f"Dygn {day + 1}")
    day_type = st.radio(f"Är detta en vardag eller helg?", ["Vardag", "Helg"], key=f"type_{day}")

    intervals = []
    num_intervals = st.number_input(f"Antal störningar detta dygn:", min_value=1, max_value=10, step=1, key=f"intervals_{day}")
    for i in range(num_intervals):
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.text_input(f"Starttid {i+1} (HH:MM)", key=f"start_{day}_{i}")
        with col2:
            end_time = st.text_input(f"Sluttid {i+1} (HH:MM)", key=f"end_{day}_{i}")
        if start_time and end_time:
            try:
                start_dt = parse_time(start_time)
                end_dt = parse_time(end_time)
                intervals.append((start_dt, end_dt))
            except:
                st.error("Felaktigt format på tid. Använd HH:MM.")

    compensated_time = timedelta()

    if day_type == "Vardag":
        for start, end in intervals:
            night_start = parse_time("20:00")
            night_end = parse_time("07:00") + timedelta(days=1)
            if start < night_end and end > night_start:
                overlap_start = max(start, night_start)
                overlap_end = min(end, night_end)
                if overlap_end > overlap_start:
                    compensated_time += calculate_duration(overlap_start, overlap_end)
    else:
        intervals.sort()
        rest_periods = []
        previous_end = parse_time("07:00")
        for start, end in intervals:
            rest_periods.append(calculate_duration(previous_end, start))
            previous_end = end
        rest_periods.append(calculate_duration(previous_end, parse_time("07:00") + timedelta(days=1)))
        longest_rest = max(rest_periods) if rest_periods else timedelta(hours=0)
        if longest_rest < timedelta(hours=11):
            compensated_time += timedelta(hours=11) - longest_rest

    st.write(f"Kompenserad tid för dygn {day + 1}: {format_duration(compensated_time)}")
    total_compensation += compensated_time

adjusted_total = total_compensation - timedelta(hours=4)
if adjusted_total < timedelta(0):
    adjusted_total = timedelta(0)

st.markdown("---")
st.write(f"**Total kompenserad tid (efter avdrag av 4 timmar): {format_duration(adjusted_total)}**")
