
import streamlit as st
from datetime import datetime, timedelta

# Helper function to parse time strings
def parse_time(time_str):
    return datetime.strptime(time_str, "%H:%M")

# Calculate compensation for weekday
def calculate_weekday_compensation(in_time, out_time):
    in_dt = parse_time(in_time)
    out_dt = parse_time(out_time)
    if out_dt < in_dt:
        out_dt += timedelta(days=1)

    # Define valid compensation window
    start_window = parse_time("20:00")
    end_window = parse_time("07:00") + timedelta(days=1)

    overlap_start = max(in_dt, start_window)
    overlap_end = min(out_dt, end_window)

    if overlap_start < overlap_end:
        return overlap_end - overlap_start
    else:
        return timedelta(0)

# Calculate compensation for weekend
def calculate_weekend_compensation(start_times, end_times):
    # Convert times to datetime objects
    times = []
    for s, e in zip(start_times, end_times):
        start = parse_time(s)
        end = parse_time(e)
        if end < start:
            end += timedelta(days=1)
        times.append((start, end))

    # Sort by start time
    times.sort()

    # Calculate rest periods between disturbances
    rest_periods = []
    for i in range(len(times) - 1):
        rest_start = times[i][1]
        rest_end = times[i + 1][0]
        if rest_end > rest_start:
            rest_periods.append(rest_end - rest_start)

    # Add rest before first disturbance and after last
    dygn_start = parse_time("07:00")
    dygn_end = dygn_start + timedelta(days=1)
    if times:
        if times[0][0] > dygn_start:
            rest_periods.append(times[0][0] - dygn_start)
        if times[-1][1] < dygn_end:
            rest_periods.append(dygn_end - times[-1][1])
    else:
        rest_periods.append(dygn_end - dygn_start)

    # Find longest rest period
    longest_rest = max(rest_periods) if rest_periods else timedelta(0)

    # Calculate missing time to reach 11 hours
    required_rest = timedelta(hours=11)
    if longest_rest < required_rest:
        return required_rest - longest_rest
    else:
        return timedelta(0)

# Streamlit interface
st.title("Beräkning av kompenserad vila enligt 11-timmarsregeln")

num_days = st.number_input("Hur många dygn vill du registrera?", min_value=1, max_value=31, value=1)
total_compensation = timedelta(0)

for i in range(num_days):
    st.subheader(f"Dygn {i+1}")
    day_type = st.radio(f"Är detta en vardag eller helg?", ["Vardag", "Helg"], key=f"type_{i}")

    if day_type == "Vardag":
        in_time = st.text_input("Tid IN (aktiv tid börjar)", key=f"in_{i}")
        out_time = st.text_input("Tid UT (aktiv tid slutar)", key=f"out_{i}")
        if in_time and out_time:
            comp = calculate_weekday_compensation(in_time, out_time)
            st.write(f"Kompensation för detta dygn: {comp}")
            total_compensation += comp

    else:
        num_disturbances = st.number_input("Antal störningar under dygnet", min_value=0, max_value=10, value=0, key=f"dist_{i}")
        start_times = []
        end_times = []
        for j in range(num_disturbances):
            start = st.text_input(f"START tid för störning {j+1}", key=f"start_{i}_{j}")
            end = st.text_input(f"SLUT tid för störning {j+1}", key=f"end_{i}_{j}")
            if start and end:
                start_times.append(start)
                end_times.append(end)
        if start_times and end_times:
            comp = calculate_weekend_compensation(start_times, end_times)
            st.write(f"Kompensation för detta dygn: {comp}")
            total_compensation += comp

# Subtract 4 hours from total compensation
adjusted_compensation = total_compensation - timedelta(hours=4)
if adjusted_compensation < timedelta(0):
    adjusted_compensation = timedelta(0)

st.markdown("---")
st.write(f"**Total kompenserad tid efter avdrag av 4 timmar:** {adjusted_compensation}")
