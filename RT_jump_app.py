# -*- coding: utf-8 -*-
"""
Created on Sat Jan  3 09:16:07 2026

@author: d23gr
"""

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import requests
import time
import numpy as np
from collections import deque
from scipy.signal import butter, filtfilt

# error handling
import logging
logging.basicConfig(level=logging.DEBUG)

# URL for data -----------------------------------------------
# this one works, but with empty JSON??
# http://192.168.12.193/get?experiment

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------
PHY_URL = "http://192.168.12.193/get?buffer=accX" # replace with your phone's IP
BUFFER_SIZE = 500
SAMPLE_RATE = 50 # Hz
FILTER_CUTOFF = 10 # Hz for Butterworth filter
FILTER_ORDER = 4

# ------------------------------------------------------------
# DATA BUFFERS
# ------------------------------------------------------------
raw_accel = deque(maxlen=BUFFER_SIZE)
filt_accel = deque(maxlen=BUFFER_SIZE)
time_buffer = deque(maxlen=BUFFER_SIZE)

jump_history = [] # store jump metrics

# ------------------------------------------------------------
# BUTTERWORTH FILTER
# ------------------------------------------------------------
def butterworth_filter(data, cutoff=FILTER_CUTOFF, fs=SAMPLE_RATE, order=FILTER_ORDER):
    if len(data) < order * 3:
        return data # not enough data yet

    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    return filtfilt(b, a, data)

# ------------------------------------------------------------
# JUMP DETECTION
# ------------------------------------------------------------
def detect_jump(accel_data, time_data, threshold=-0.5):
    if len(accel_data) < 5:
        return False, None, None
    
    a = np.array(accel_data)
    t = np.array(time_data)
    
    freefall = np.where(a < threshold)[0]
    if len(freefall) < 2:
        return False, None, None

    takeoff = freefall[0]
    landing = freefall[-1]
    
    flight_time = t[landing] - t[takeoff]
    g = 9.81
    height = g * (flight_time**2) / 8
    
    return True, flight_time, height

# ------------------------------------------------------------
# DASH APP
# ------------------------------------------------------------
app = dash.Dash(__name__)

app.layout = html.Div([
html.H1("Vertical Jump Assessment Dashboard", style={"textAlign": "center"}),

# ------------------ METRIC CARDS ------------------
html.Div([
html.Div([
html.H3("Latest Jump Height"),
html.Div(id="height-card", className="metric-card")
], className="card"),

html.Div([
html.H3("Latest Flight Time"),
html.Div(id="flight-card", className="metric-card")
], className="card"),

html.Div([
html.H3("Total Jumps"),
html.Div(id="count-card", className="metric-card")
], className="card"),
], className="card-container"),

# ------------------ LIVE GRAPH ------------------
html.Div([
dcc.Graph(id="live-graph", animate=False)
], style={"marginTop": "20px"}),

# ------------------ INTERVAL ------------------
dcc.Interval(
id="interval-component",
interval=1000 / SAMPLE_RATE,
n_intervals=0
),

# ------------------ JUMP HISTORY ------------------
html.H2("Jump History", style={"marginTop": "40px"}),
html.Div(id="jump-history-table")
])

# ------------------------------------------------------------
# CALLBACK
# ------------------------------------------------------------
@app.callback(
    Output("live-graph", "figure"),
    Output("height-card", "children"),
    Output("flight-card", "children"),
    Output("count-card", "children"),
    Output("jump-history-table", "children"),
    Input("interval-component", "n_intervals")
)

def update(n):
    # ------------------ STREAM DATA ------------------
    try:
        r = requests.get(PHY_URL, timeout=2).json()
        buf = r.get("buffer", {}).get("accX", {}).get("buffer", [])
        ax = buf[-1] if buf else 0
    except Exception as e:
        print("Callback error:", e)
        ax = 0
    # try:
    #     resp = requests.get(PHY_URL, timeout=2)
    #     data = resp.json()
    #     ax = data["buffer"]["accX"]["buffer"][-1]
    # except Exception as e:
    #     print("Callback error:", e)
    #     ax = 0
    
    timestamp = time.time()
    
    raw_accel.append(ax)
    time_buffer.append(timestamp)
    
    # ------------------ FILTER ------------------
    filtered = butterworth_filter(list(raw_accel))
    filt_accel.clear()
    filt_accel.extend(filtered)
    
    # ------------------ JUMP DETECTION ------------------
    jump_detected, flight_time, height = detect_jump(filt_accel, time_buffer)
    
    height_text = "---"
    flight_text = "---"
    
    if jump_detected:
        height_text = f"{height:.3f} m"
        flight_text = f"{flight_time:.3f} s"
    
    jump_history.append({
    "timestamp": timestamp,
    "height": height,
    "flight_time": flight_time
    })
    
    # ------------------ PLOT ------------------
    fig = go.Figure()
    fig.add_trace(go.Scatter(
    x=list(time_buffer),
    y=list(raw_accel),
    mode="lines",
    name="Raw Acceleration",
    line=dict(color="gray")
    ))
    fig.add_trace(go.Scatter(
    x=list(time_buffer),
    y=list(filt_accel),
    mode="lines",
    name="Filtered Acceleration",
    line=dict(color="blue", width=3)
    ))
    
    fig.update_layout(
    title="Real-Time Vertical Acceleration",
    xaxis_title="Time (s)",
    yaxis_title="Acceleration (g)",
    template="plotly_white"
    )
    
    # ------------------ HISTORY TABLE ------------------
    rows = [
    html.Tr([html.Th("Time"), html.Th("Height (m)"), html.Th("Flight Time (s)")])
    ]
    
    for j in jump_history[-10:]:
        rows.append(html.Tr([
        html.Td(time.strftime("%H:%M:%S", time.localtime(j["timestamp"]))),
        html.Td(f"{j['height']:.3f}"),
        html.Td(f"{j['flight_time']:.3f}")
        ]))
    
    table = html.Table(rows, className="history-table")
    
    return fig, height_text, flight_text, str(len(jump_history)), table

# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
