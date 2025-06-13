"""Utility Module"""
import random
from datetime import datetime, timedelta
import numpy as np
import itertools

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

def generate_date():
    # Get today's date
    end_date = datetime.now()
    # Calculate the date two years ago
    start_date = end_date - timedelta(days=730)
    # Generate a random date between start_date and end_date
    random_date = start_date + (end_date - start_date) * random.random()
    return random_date


def round_percent_dict_to_100(percent_dict):
    # Step 1: Floor each value
    floored = {k: int(v) for k, v in percent_dict.items()}
    remainder = 100 - sum(floored.values())

    # Step 2: Sort by descending decimal part
    decimals = sorted(
        [(k, percent_dict[k] - floored[k]) for k in percent_dict],
        key=lambda x: x[1],
        reverse=True
    )

    # Step 3: Distribute remaining points using cycle to avoid IndexError
    if decimals:
        cycle_iter = itertools.cycle(decimals)
        for _ in range(remainder):
            k, _ = next(cycle_iter)
            floored[k] = floored.get(k, 0) + 1

    return floored
