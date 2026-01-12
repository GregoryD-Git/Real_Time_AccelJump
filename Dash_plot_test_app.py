# -*- coding: utf-8 -*-
"""
Created on Wed Jan  7 19:24:38 2026

@author: d23gr
"""
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np

app = dash.Dash(__name__)

# Number of points to keep in the rolling window
WINDOW = 500

# Track x-axis index manually
x_pos = 0

# Pre-initialize the figure for speed
initial_fig = go.Figure(
    data=[go.Scatter(y=[], x=[], mode="lines")],
    layout=go.Layout(
        xaxis=dict(autorange=True), # auto-update the range of the x-axis
        yaxis=dict(range=[-3, 3]),
        margin=dict(l=40, r=20, t=20, b=40),
        uirevision=True  # prevents resetting view on updates
    )
)


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
    
    # # generate random data each interval
    # y.append(np.random.randn())

    # fig = go.Figure(
    #     data=[go.Scatter(y=y, mode="lines+markers")]
    # )
    # return fig

    # Replace this with your accelerometer API call\
    # new_y = *try stuff for API
    new_y = np.random.randn()

    update = dict(
        x=[[x_pos]],
        y=[[new_y]]
    )

    x_pos += 1

    # extendData return format:
    # (update_dict, trace_indices, max_points)
    return update, [0], WINDOW


if __name__ == "__main__":
    app.run(debug=True)
