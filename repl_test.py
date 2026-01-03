# -*- coding: utf-8 -*-
"""
Created on Sat Jan  3 11:43:46 2026

@author: d23gr
"""

import requests

PHY_URL = "http://192.168.12.193:80"

try:
    r = requests.get(PHY_URL, timeout=2)
    print("Status:", r.status_code)
    print("Raw text:", repr(r.text))
except Exception as e:
    print("Error:", e)