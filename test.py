import time

import pandas as pd
from datetime import timedelta
from utils.functions import *
import json


def occasional_times_overlap(interval1: pd.Interval, interval2: pd.Interval):
    return interval1.overlaps(interval2)


def normalize_interval(start, end):
    """Ensure the interval is valid by rolling over the end time if it's less than the start time."""
    start_dt = pd.Timestamp.combine(pd.Timestamp.min, start)
    if end < start:
        end_dt = pd.Timestamp.combine(pd.Timestamp.min + timedelta(days=1), end)
    else:
        end_dt = pd.Timestamp.combine(pd.Timestamp.min, end)

    # Create additional intervals for comprehensive checking
    start_prev_day = start_dt - timedelta(days=1)
    end_prev_day = end_dt - timedelta(days=1)

    intervals = [
        pd.Interval(start_dt, end_dt),  # Original interval
        pd.Interval(start_prev_day, end_prev_day),  # Interval with start one day earlier
    ]

    return intervals


def fixed_times_overlap(interval1, interval2):
    # Extract time component from interval bounds
    start1 = interval1.left.time()
    end1 = interval1.right.time()
    start2 = interval2.left.time()
    end2 = interval2.right.time()

    # Normalize the intervals to handle day rollover
    interval1_times = normalize_interval(start1, end1)
    interval2_times = normalize_interval(start2, end2)

    # Check if any of the intervals overlap
    for interval1_time in interval1_times:
        for interval2_time in interval2_times:
            if interval1_time.overlaps(interval2_time):
                return True

    return False


def times_overlap(unable_times: dict, request_interval: pd.Interval):
    is_fixed_times = any([fixed_times_overlap(i, request_interval) for i in unable_times['fixed']])
    is_occasional_times = any([occasional_times_overlap(i, request_interval) for i in unable_times['occasional']])
    return is_fixed_times or is_occasional_times


occasional_unable_path = '/Users/matin/paper_gmail_shift_transfer/utils/occasional_unable_times.json'
fixed_unable_path = '/Users/matin/paper_gmail_shift_transfer/utils/fixed_unable_times.json'
occasional_unable_file = open(occasional_unable_path)
fixed_unable_file = open(fixed_unable_path)
occasional_unable_times = array_to_time_intervals(json.load(occasional_unable_file))
fixed_unable_times = array_to_time_intervals(json.load(fixed_unable_file))

unable_times = dict(occasional=occasional_unable_times, fixed=fixed_unable_times)

interval2 = pd.Interval(pd.Timestamp('2024-04-13 08:30:00'), pd.Timestamp('2024-04-23 14:30:00'))

now = time.time()
print(times_overlap(unable_times, interval2))
print(time.time() - now)
# def normalize_interval(start, end):
#     """Ensure the interval is valid by rolling over the end time if it's less than the start time."""
#     start_dt = pd.Timestamp.combine(pd.Timestamp.min, start)
#     if end < start:
#         end_dt = pd.Timestamp.combine(pd.Timestamp.min + timedelta(days=1), end)
#     else:
#         end_dt = pd.Timestamp.combine(pd.Timestamp.min, end)
# 
#     # Create additional intervals for comprehensive checking
#     start_prev_day = start_dt - timedelta(days=1)
#     end_prev_day = end_dt - timedelta(days=1)
# 
#     intervals = [
#         pd.Interval(start_dt, end_dt),  # Original interval
#         pd.Interval(start_prev_day, end_prev_day),  # Interval with start one day earlier
#     ]
# 
#     return intervals
# 
# 
# def times_overlap(interval1, interval2):
#     # Extract time component from interval bounds
#     start1 = interval1.left.time()
#     end1 = interval1.right.time()
#     start2 = interval2.left.time()
#     end2 = interval2.right.time()
# 
#     # Normalize the intervals to handle day rollover
#     interval1_times = normalize_interval(start1, end1)
#     interval2_times = normalize_interval(start2, end2)
# 
#     # Check if any of the intervals overlap
#     for interval1_time in interval1_times:
#         for interval2_time in interval2_times:
#             if interval1_time.overlaps(interval2_time):
#                 return True
# 
#     return False

    # import pandas as pd
#
#
# def check_time_overlap(interval1, interval2):
#     """
#     Check if the time-of-day portions of two pandas datetime intervals overlap.
#
#     Args:
#         interval1 (pd.Interval): The first datetime interval.
#         interval2 (pd.Interval): The second datetime interval.
#
#     Returns:
#         bool: True if the time-of-day portions overlap, False otherwise.
#     """
#
#     # Extract time components and convert to Timedeltas
#     time1_left = pd.to_timedelta(interval1.left.time())
#     time1_right = pd.to_timedelta(interval1.right.time())
#     time1 = pd.Interval(time1_left, time1_right, interval1.closed)
#
#     time2_left = pd.to_timedelta(interval2.left.time())
#     time2_right = pd.to_timedelta(interval2.right.time())
#     time2 = pd.Interval(time2_left, time2_right, interval2.closed)
#
#     # Handle intervals spanning across midnight
#     if time1.left > time1.right:
#         time1 = pd.Interval(pd.Timedelta(0), time1.right, time1.closed) | pd.Interval(time1.left, pd.Timedelta(
#             days=1) - pd.Timedelta(nanoseconds=1), time1.closed)
#
#     if time2.left > time2.right:
#         time2 = pd.Interval(pd.Timedelta(0), time2.right, time2.closed) | pd.Interval(time2.left, pd.Timedelta(
#             days=1) - pd.Timedelta(nanoseconds=1), time2.closed)
#
#     # Check for overlap
#     return time1.overlaps(time2)


# Example intervals
# interval1 = pd.Interval(pd.Timestamp('1111-1-1 20:30:00'), pd.Timestamp('1111-1-2 8:30:00'))
# interval2 = pd.Interval(pd.Timestamp('2023-03-13 02:30:00'), pd.Timestamp('2024-03-23 14:30:00'))
# interval3 = pd.Interval(pd.Timestamp('2024-05-16 03:00:00'), pd.Timestamp('2024-05-16 04:00:00'))
#
# # Check if time of day overlaps
# now = time.time()
# print(times_overlap(interval1, interval2))
# print('it took:', time.time() - now)  # Output: True
# print(times_overlap(interval1, interval3))  # Output: False

# print(check_time_overlap(interval1, interval2))  # Output: True
# print(check_time_overlap(interval1, interval3))  # Output: False
