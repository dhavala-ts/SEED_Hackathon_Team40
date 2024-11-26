import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import time
import pushbullet
import threading

# Function to generate timestamps for the dataset (if missing)
def add_timestamps(df):
    if 'timestamp' not in df.columns:
        df['timestamp'] = pd.date_range(
            start=datetime.now() - timedelta(days=len(df)),
            periods=len(df),
            freq='D'
        )
    else:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    return df

# Function to group data by daily, weekly, or monthly
def group_data(df, report_type):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    if report_type == 'Daily':
        grouped = df.set_index('timestamp').resample('D').mean()
    elif report_type == 'Weekly':
        grouped = df.set_index('timestamp').resample('W').mean()
    elif report_type == 'Monthly':
        grouped = df.set_index('timestamp').resample('M').mean()
    else:
        grouped = df
    return grouped.reset_index()

# Function to send push notifications
def send_push_notification(message):
    pb = pushbullet.Pushbullet("o.Jwp495Zb7Y0YX0tKgSAkwd2jlqIMefLn")  # Your Pushbullet API Key
    pb.push_note("Health Parameter Alert", message)

# Function to trigger a push notification 30-60 seconds before a specified event
def notify_before_event(event_time):
    time_until_event = event_time - datetime.now()
    # Calculate the time in seconds
    seconds_until_event = time_until_event.total_seconds()

    # If event time is 30-60 seconds away, notify the user
    if 30 <= seconds_until_event <= 60:  # 30 to 60 seconds
        send_push_notification(f"Alert: Fall will occur at {event_time.strftime('%Y-%m-%d %H:%M:%S')}.")

# Main function
def main():
    st.title("Health Parameter Trends Dashboard")
    st.sidebar.title("Options")
    
    # Sidebar selections
    report_type = st.sidebar.selectbox("Report Type", ["Daily", "Weekly", "Monthly"])
    parameter = st.sidebar.selectbox("Parameter to Visualize", [
        "Alpha_Synuclein", "Dopamine", "Gyrometer_X", "Gyrometer_Y", "Gyrometer_Z", "SpO2"
    ])
    param1 = st.sidebar.selectbox("First Parameter (Correlation)", [
        "Alpha_Synuclein", "Dopamine", "SpO2", "Gyrometer_X", "Gyrometer_Y", "Gyrometer_Z"
    ])
    param2 = st.sidebar.selectbox("Second Parameter (Correlation)", [
        "Alpha_Synuclein", "Dopamine", "SpO2", "Gyrometer_X", "Gyrometer_Y", "Gyrometer_Z"
    ])

    # Dataset with 30 rows from your provided data
    data = {
        "Alpha_Synuclein": [
            5.82757205, 8.353209014, 2.397269599, 2.632775095, 4.301560091,
            5.079006693, 6.862596164, 6.618172406, 5.537123946, 2.389480179,
            4.288391148, 5.596878313, 1.496206366, 1.541801747, 1.152963595,
            6.133685554, 3.274635734, 3.901682289, 7.8649506, 4.527118534,
            5.696873717, 2.995158921, 4.166023874, 3.865597475, 3.01796025,
            9.581839977, 4.458305733, 2.015186083, 2.732071608, 7.915468905
        ],
        "Dopamine": [
            93.81822304, -3.959772234, 57.52027196, 35.51066384, -82.13250414,
            -51.56426269, 252.8405379, -39.54889029, 90.06893807, -97.65577238,
            3.626325144, -40.48407227, 24.44278314, -21.72621173, -76.72816722,
            83.61918533, 134.5823373, 63.35747065, 109.4657828, 85.02371147,
            177.3061505, 0.15338754, 30.55893777, 176.3196916, -75.31096712,
            84.58479999, 71.68712112, 42.86651871, 127.0219914, 63.25805351
        ],
        "Gyrometer_X": [
            0.562342544, -0.310289468, 0.233720008, 0.14925184, 0.215676462,
            -0.367528728, 0.877587044, -0.052386502, 0.773552005, -0.379749348,
            -0.316451595, -0.329837098, -0.454340962, 0.77161986, -0.280032989,
            -0.720133619, 0.381042523, -0.066884774, -0.03331193, -0.203458806,
            0.210628156, 0.094986684, 0.393939021, 0.501514113, 0.701180933,
            0.934966023, -0.235079986, 0.494906469, -0.426639753, 0.70450458
        ],
        "Gyrometer_Y": [
            0.264276689, -0.030766252, -0.465710596, 1.192402262, -0.198835993,
            0.427090477, 0.083309326, -0.146155145, 0.46003622, 0.24960306,
            0.080576898, -0.074289543, -0.648620125, 0.498164982, -0.609461288,
            0.599063051, -0.112516564, -0.08661587, -0.88715747, 0.184171611,
            -0.389603814, 0.239563585, -0.180961379, 0.102607295, 0.07553693,
            0.213882292, 0.187365956, 0.205540816, 0.818082091, 0.387285326
        ],
        "Gyrometer_Z": [
            0.569639349, 0.965807153, 0.310221165, 0.551550053, 0.581265633,
            -0.480806746, 0.27548939, -0.213301902, -0.332070201, -0.572380764,
            0.088790799, -0.126070194, -0.725290446, 0.217553399, 0.034974799,
            0.536486484, 0.097688324, -0.582167813, -0.035642296, 0.056161823,
            0.33591992, -0.396384458, 0.379295591, -0.48279833, 0.391037504,
            0.622465907, -0.548491129, 0.480677154, -0.053640969, 0.883491954
        ],
        "SpO2": [
            91.46827168, 93.15686746, 94.97053538, 93.90081823, 91.47454275,
            96.72192079, 90.58186572, 91.00646726, 92.05091645, 92.23104066,
            96.1090092, 97.84208148, 96.97904313, 93.30758851, 93.91105694,
            92.87027629, 94.83687698, 94.14843385, 92.2064724, 94.58693131,
            91.44482303, 91.06608967, 92.50418707, 92.55003594, 96.03745297,
            91.69784735, 93.98744841, 92.55991447, 90.85519755, 92.21578561
        ]
    }

    # Convert data to a DataFrame
    df = pd.DataFrame(data)
    df = add_timestamps(df)

    # Group the data based on the selected report type
    grouped_data = group_data(df, report_type)

    # Display line chart for selected parameter
    st.subheader(f"{parameter} Trend ({report_type})")
    st.line_chart(grouped_data[['timestamp', parameter]].set_index('timestamp'))

    # Correlation line graph
    st.subheader(f"{param1} vs {param2} Over Time ({report_type})")
    correlation_data = grouped_data[['timestamp', param1, param2]].set_index('timestamp')
    st.line_chart(correlation_data)

    # Trigger a notification 30-60 seconds before a specific event (for example, the next data point or user-defined event time)
    event_time = datetime.now() + timedelta(seconds=45)  # Example event time (45 seconds from now)
    threading.Thread(target=notify_before_event, args=(event_time,)).start()

# Run the app
if __name__ == "__main__":
    main()
