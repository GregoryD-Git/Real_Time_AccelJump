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

app.layout = html.Div([
    dcc.Graph(id="live-graph"),
    dcc.Interval(
        id="interval-component",
        interval=10,  # 1000 ms = 1 second
        n_intervals=0
    )
])

# initialize list for plotting data
y = []

@app.callback(
    Output("live-graph", "figure"),
    Input("interval-component", "n_intervals")
)
def update_graph(n):
    # generate random data each interval
    y.append(np.random.randn())

    fig = go.Figure(
        data=[go.Scatter(y=y, mode="lines+markers")]
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True)
