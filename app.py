import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO

# --- Hjälpfunktioner ---

def parse_time(time_str: str) -> datetime:
    return datetime.strptime(time_str, "%H:%M")

def normalize_interval(start: datetime, end: datetime) -> tuple:
    if end <= start:
        end += timedelta(days=1)
    return start, end

def calculate_weekday_compensation(start: datetime, end: datetime) -> float:
    """Beräkna all störningstid som faller inom 20:00–07:00."""
    start, end = normalize_interval(start, end)

    # Nattfönster i två delar: 20–24 och 00–07
    night1_start = parse_time("20:00")
    night1_end = parse_time("23:59") + timedelta(minutes=1)  # 24:00
    night2_start = parse_time("00:00") + timedelta(days=1)
    night2_end = parse_time("07:00") + timedelta(days=1)

    overlap_minutes = 0

    # Överlapp med första nattfönstret (20–24)
    overlap_start = max(start, night1_start)
    overlap_end = min(end, night1_end)
    if overlap_end > overlap_start:
        overlap_minutes += (overlap_end - overlap_start).total_seconds() / 60

    # Överlapp med andra nattfönstret (00–07)
    overlap_start = max(start, night2_start)
    overlap_end = min(end, night2_end)
    if overlap_end > overlap_start:
        overlap_minutes += (overlap_end - overlap_start).total_seconds() / 60

    return overlap_minutes

def calculate_weekend_rest(intervals: list) -> float:
    intervals = [normalize_interval(s, e) for s, e in intervals]
    intervals.sort()

    dygn_start = parse_time("07:00")
    dygn_end = dygn_start + timedelta(days=1)

    clipped = []
    for s, e in intervals:
        if e <= dygn_start or s >= dygn_end:
            continue
        clipped.append((max(s, dygn_start), min(e, dygn_end)))

    clipped.sort()

    rest_periods = []
    current = dygn_start
    for s, e in clipped:
        if s > current:
            rest_periods.append((s - current).total_seconds() / 60)
        current = max(current, e)

    if current < dygn_end:
        rest_periods.append((dygn_end - current).total_seconds() / 60)

    if not rest_periods:
        rest_periods = [(dygn_end - dygn_start).total_seconds() / 60]

    longest_rest = max(rest_periods)
    missing_minutes = max(0, 11 * 60 - longest_rest)
    return missing_minutes

def format_minutes(minutes: float) -> str:
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours}h {mins}m"

def to_excel_bytes(df: pd.DataFrame) -> BytesIO:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# --- Streamlit-app ---

st.title("Beräkning av kompenserad vila")
num_days = st.number_input("Antal dygn att registrera", min_value=1, max_value=31, value=1)

total_comp_minutes = 0
results = []

for day in range(num_days):
    st.subheader(f"Dygn {day + 1}")
    day_type = st.radio(f"Typ av dygn {day + 1}", ["Vardag", "Helg"], key=f"type_{day}")
    intervals = []
    num_intervals = st.number_input(
        f"Antal störningar för dygn {day + 1}",
        min_value=1,
        max_value=10,
        value=1,
        key=f"num_{day}"
    )

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
                intervals.append(normalize_interval(start, end))
            except ValueError:
                st.error("Fel format på tid. Använd HH:MM.")

    if intervals:
        if day_type == "Vardag":
            comp_minutes = sum(calculate_weekday_compensation(start, end) for start, end in intervals)
        else:
            comp_minutes = calculate_weekend_rest(intervals)

        total_comp_minutes += comp_minutes

        st.write(f"Kompenserad tid för dygn {day + 1}: {format_minutes(comp_minutes)}")


        results.append({
            "Dygn": day + 1,
            "Typ": day_type,
            "Kompenserad tid (min)": round(comp_minutes),
            "Kompenserad tid": format_minutes(comp_minutes)
        })

# --- Summering ---
adjusted_minutes = max(0, total_comp_minutes - 240)
st.markdown("---")
st.write(f"**Total kompenserad tid (efter avdrag av 4 timmar): {format_minutes(adjusted_minutes)}**")


if results:
    df = pd.DataFrame(results)
    df.loc[len(df.index)] = {
        "Dygn": "Summa",
        "Typ": "",
        "Kompenserad tid (min)": round(total_comp_minutes),
        "Kompenserad tid": format_minutes(total_comp_minutes)
    }
    df.loc[len(df.index)] = {
        "Dygn": "Justering",
        "Typ": "",
        "Kompenserad tid (min)": round(adjusted_minutes),
        "Kompenserad tid": format_minutes(adjusted_minutes)
    }

    excel_data = to_excel_bytes(df)
    st.download_button(
        "Ladda ner resultat som Excel",
        data=excel_data,
        file_name="kompensation.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
