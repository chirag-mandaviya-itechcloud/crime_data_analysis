"""Utility Module"""
from datetime import datetime

def convert_date(date_str):
    dt = datetime.strptime(date_str.strip(), "%m/%d/%Y %H:%M")
    formatted_date = dt.strftime("%Y-%m-%d")
    return formatted_date
