"""Utility Module"""
from datetime import datetime
import numpy as np

def convert_date(date_str):
    dt = datetime.strptime(date_str.strip(), "%m/%d/%Y %H:%M")
    formatted_date = dt.strftime("%Y-%m-%d")
    return formatted_date

def get_center(points):
    coords = np.array(points)
    center = coords.mean(axis=0)
    return {
        "latitude": round(center[0], 6),
        "longitude": round(center[1], 6)
    }
