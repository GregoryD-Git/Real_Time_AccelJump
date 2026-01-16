# -*- coding: utf-8 -*-
"""
Created on Wed Jan  7 19:24:38 2026

@author: d23gr
"""
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.io as pio
template_list = list(pio.templates) # get list of plotly templates
import numpy as np
import time
from collections import deque
from datetime import datetime 
import requests

# ------------------------------------------------------------
# USEFUL FUNCTIONS
# ------------------------------------------------------------

# ------------------------------------------------------------
# INITIALIZE THE APP
# ------------------------------------------------------------
app = dash.Dash(__name__)

# ------------------------------------------------------------
# INITIALIZE
# ------------------------------------------------------------
# PHY_URL = "http://192.168.12.193/get?buffer=accX" # replace with your phone's IP
signal_grab = 'accX'
PHY_URL = f"http://172.20.10.1:80/get?buffer={signal_grab}"

WINDOW = 500  # Number of points to keep in the rolling window
BUFFER_SIZE = 500

time_buffer = deque(maxlen=BUFFER_SIZE)
start_time = time.time()
# Track x-axis index manually
x_pos = 0

# Pre-initialize the figure for speed
# initial_fig = go.Figure(
#     data=[go.Scatter(y=[], x=[], mode="lines")],
#     layout=go.Layout(
#         xaxis=dict(autorange=True), # auto-update the range of the x-axis
#         yaxis=dict(range=[-3, 3]),
#         margin=dict(l=40, r=20, t=20, b=40),
#         uirevision=True  # prevents resetting view on updates
#     )
# )
initial_fig = go.Figure(
    data=[go.Scatter(y=[], x=[], mode="lines")],
    layout=go.Layout(
        title=dict(
            text="Real-Time Signal",
            x=0.5,
            font=dict(size=22)
        ),
        xaxis=dict(
            title=dict(
                text="Time (s)",
                font=dict(size=16)
            ),
            autorange=True,
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title=dict(
                text="Amplitude",
                font=dict(size=16)
            ),
            range=[-3, 3],
            tickfont=dict(size=12)
        ),
        margin=dict(l=60, r=30, t=60, b=60),
        height=500,
        width=900,
        template="ggplot2",
        uirevision=True
    )
)

# initial_fig.update_traces(
#     line=dict(width=2, color="cyan"),
#     hovertemplate="x: %{x}<br>y: %{y}<extra></extra>"
# )

# html.Div is a container that holds the app components that will appear on the webpage
app.layout = html.Div([
    dcc.Graph(id="live-graph", figure=initial_fig),             # plot graph to be updated, Dash identifies it by the id, which is needed in callback
    dcc.Interval(
        id="interval-component",
        interval=50,                      # 50 = 20 intervals per second - if interval=1000, triggers a callback every second (1000ms)
        n_intervals=0                       # interval counter increasing by 1 for each callback
    )
])

# initialize list for plotting data
y = []

# The callback connects inputs (things that trigger updates) to outputs (things that get updated)
# # this version of the callback redraws the figure each time, and is slow
# @app.callback(
#     Output("live-graph", "figure"),             # callback will produce a new figure for the component with the given id
#     Input("interval-component", "n_intervals")  # Tells Dash to run the callback every time the counter increments
# )

# This version of the callback extends the figure instead of redrawing it
@app.callback(
    Output("live-graph", "extendData"),             # callback will produce a new figure for the component with the given id
    Input("interval-component", "n_intervals")  # Tells Dash to run the callback every time the counter increments
)
def update_graph(n):
    global x_pos

    # ---------------------------------
    # API call
    # ---------------------------------
    try:
        r = requests.get(PHY_URL, timeout=2).json()
        buf = r.get("buffer", {}).get(signal_grab, {}).get("buffer", [])
        # ax = buf[-1] if buf else 0
        new_y = buf[-1] if buf else 0
        # print(requests.get("http://172.20.10.1:8080/get", timeout=2).json())
    except Exception as e:
        print("Callback error:", e)
        # ax = 0
        new_y = 0
        print('\n Connections seems to work but no data from JSON!!\n')
    
    # ---------------------------------
    # RANDOM NUMBER GENERATOR PLOT FOR TESTING
    # ---------------------------------
    # new_y = np.random.randn()
    
    # timestamp = datetime.fromtimestamp(time.time()).second
    elapsed_time = time.time() - start_time
    timestamp = round(elapsed_time, 3)  # trim to milliseconds
    
    update = dict(
        x=[[timestamp]], # formerly x_pos
        y=[[new_y]]
    )

    # ---------------------------------
    # RETURN DATA FOR CALLBACK
    # ---------------------------------
    # x_pos += 1

    # extendData return format:
    # (update_dict, trace_indices, max_points)
    return update, [0], WINDOW


if __name__ == "__main__":
    app.run(debug=True)
