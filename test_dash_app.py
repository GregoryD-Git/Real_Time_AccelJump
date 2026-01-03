# -*- coding: utf-8 -*-
"""
Created on Sat Jan  3 10:44:36 2026

@author: d23gr
"""

from dash import Dash, html

app = Dash(__name__)

app.layout = html.Div("Hello Dash")

if __name__ == "__main__":
    app.run(debug=True)