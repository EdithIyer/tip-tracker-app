import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

# Set up Google Sheets authentication
@st.cache_resource
def get_google_sheets_client():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file('/Users/edithiyer-hernandez/Desktop/leisure_apps/tip-calculation-project-7ba01a5e9f72.json', scopes=scope)
    return gspread.authorize(creds)

client = get_google_sheets_client()
SHEET_ID = '18UQTLSQ0o2feCWLVBn21Fr4nVr32qJ4gpvQnsDtoiis'

# Open the Google Sheet (replace with your sheet ID)
sheet = client.open_by_key(SHEET_ID).sheet1

def create_time_input(label, key):
    col1, col2 = st.columns(2)
    with col1:
        hour = st.selectbox(f"{label} (Hour)", range(24), key=f"{key}_hour")
    with col2:
        minute = st.selectbox(f"{label} (Minute)", range(0, 60, 15), key=f"{key}_minute")
    return f"{hour:02d}:{minute:02d}"

def load_data():
    data = sheet.get_all_records()
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["date", "name", "time_started", "time_ended", "check_total", "tip_total"])

def append_row(row_data):
    sheet.append_row(row_data)

def calculate_hours(start_time, end_time):
    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")
    if end < start:
        end += timedelta(days=1)
    return (end - start).total_seconds() / 3600

def calculate_daily_report(df):
    if df.empty:
        return None
    df['hours'] = df.apply(lambda row: calculate_hours(row['time_started'], row['time_ended']), axis=1)
    total_tips = df['tip_total'].sum()
    total_hours = df['hours'].sum()
    df['tip_share'] = df.apply(lambda row: total_tips * (row['hours'] / total_hours), axis=1)
    return df[['name', 'hours', 'tip_share']]

st.title("Tip Tracker App")

# Input form
st.header("Add Employee Shift")
with st.form("employee_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name")
        date = st.date_input("Date")
        time_started = create_time_input("Time Started", "start")
        time_ended = create_time_input("Time Ended", "end")
    with col2:
        check_total = st.number_input("Check Total", min_value=0.0, format="%.2f")
        tip_total = st.number_input("Tip Total", min_value=0.0, format="%.2f")

    submitted = st.form_submit_button("Add Employee")
    if submitted:
        new_row = [
            date.strftime("%Y-%m-%d"),
            name,
            time_started,
            time_ended,
            check_total,
            tip_total
        ]
        append_row(new_row)
        st.success("Employee shift added successfully!")

# Display employee shifts
if st.button("Load Data"):
    df = load_data()
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No employee shifts added yet.")

# Generate daily report
report_date = st.date_input("Select date for report")
if st.button("Generate Daily Report"):
    df = load_data()
    daily_data = df[df['date'] == report_date.strftime("%Y-%m-%d")]
    if daily_data.empty:
        st.warning("No data available for the selected date.")
    else:
        daily_report = calculate_daily_report(daily_data)
        st.header(f"Daily Report for {report_date}")
        st.dataframe(daily_report.style.format({
            "hours": "{:.2f}",
            "tip_share": "${:.2f}"
        }))

# Clear data button
if st.button("Clear All Data"):
    sheet.clear()
    sheet.update([["date", "name", "time_started", "time_ended", "check_total", "tip_total"]])
    st.success("All data has been cleared.")
    st.experimental_rerun()