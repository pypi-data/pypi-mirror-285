import random
import time
from vytal.hci import *

# Test function to generate synthetic gaze data
def generate_synthetic_gaze_data(num_points, max_x=1000, max_y=1000, max_time_interval=200):
    gaze_data = []
    current_time = 0
    for _ in range(num_points):
        x = random.uniform(0, max_x)
        y = random.uniform(0, max_y)
        current_time += random.uniform(0, max_time_interval)
        gaze_data.append((x, y, current_time))
    return gaze_data

# Function to print test results in a readable format
def print_fixation_results(fixations):
    print(len(fixations))
    for i, (centroid, duration) in enumerate(fixations):
        print(f"Fixation {i+1}: Centroid at {centroid}, Duration: {duration:.2f} seconds")

# Test cases
def test_fixation_detection():
    test_cases = [
        {
            "description": "Simple case with one clear fixation",
            "data": [(100, 100, 0), (102, 98, 500), (101, 99, 1000), (150, 150, 2000)],
            "distance_threshold": 30,
            "time_threshold_ms": 1000,
        },
        {
            "description": "Case with multiple fixations",
            "data": [(100, 100, 0), (102, 98, 500), (101, 99, 1000), (200, 200, 2000), (202, 202, 2500), (201, 201, 3000)],
            "distance_threshold": 30,
            "time_threshold_ms": 500,
        },
        {
            "description": "Case with gap between fixations",
            "data": [(100, 100, 0), (102, 98, 500), (101, 99, 1000), (300, 300, 3000), (200, 200, 2000), (202, 202, 2500), (201, 201, 3000)],
            "distance_threshold": 30,
            "time_threshold_ms": 500,
        },
        {
            "description": "Case with no fixations due to time threshold",
            "data": [(100, 100, 0), (102, 98, 500), (101, 99, 1000), (200, 200, 1800), (202, 202, 2300), (201, 201, 2800)],
            "distance_threshold": 30,
            "time_threshold_ms": 2000,
        },
        {
            "description": "Case with no fixations due to distance threshold",
            "data": [(100, 100, 0), (300, 300, 500), (500, 500, 1000), (700, 700, 1500)],
            "distance_threshold": 50,
            "time_threshold_ms": 1000,
        },
        {
            "description": "Complex case with varied fixations",
            "data": generate_synthetic_gaze_data(100),
            "distance_threshold": 200,
            "time_threshold_ms": 50,
        },
        {
            "description": "Case with non-increasing timestamps",
            "data": [(100, 100, 0), (200, 200, 100), (100, 100, 50), (400, 400, 300)],
            "distance_threshold": 30,
            "time_threshold_ms": 40,
        },
        {
            "description": "Case with non-numeric values",
            "data": [(100, 100, 0), (200, '200', 100), (300, 300, '200'), (400, 400, 300)],
            "distance_threshold": 30,
            "time_threshold_ms": 500,
        },
        {
            "description": "Empty gaze points list",
            "data": [],
            "distance_threshold": 30,
            "time_threshold_ms": 500,
        },
        {
            "description": "Invalid distance threshold",
            "data": [(100, 100, 0), (200, 200, 100), (300, 300, 200)],
            "distance_threshold": -30,
            "time_threshold_ms": 500,
        },
        {
            "description": "Invalid time threshold",
            "data": [(100, 100, 0), (200, 200, 100), (300, 300, 200)],
            "distance_threshold": 30,
            "time_threshold_ms": -500,
        }
    ]
    
    for case in test_cases:
        print(f"Test Case: {case['description']}")
        try:
            fixations = fixation_detection(case["data"], case["distance_threshold"], case["time_threshold_ms"])
            print_fixation_results(fixations)
        except ValueError as e:
            print(f"Error: {e}")
        print("\n")

# Function to print test results in a readable format
def print_saccade_results(saccades):
    for i, saccade in enumerate(saccades):
        print(f"Saccade {i+1}:")
        print(f"  Start Point: {saccade['start_point']}")
        print(f"  End Point: {saccade['end_point']}")
        print(f"  Duration: {saccade['duration']} ms")
        print(f"  Amplitude: {saccade['amplitude']:.2f} pixels")
        print(f"  Peak Velocity: {saccade['peak_velocity']:.2f} pixels/second")
        print(f"  Average Velocity: {saccade['average_velocity']:.2f} pixels/second")

# Test cases
def test_saccade_detection():
    test_cases = [
        {
            "description": "Simple case with one clear saccade",
            "data": [(100, 100, 0), (200, 200, 100), (300, 300, 200), (400, 400, 300), (500, 500, 400)],
            "velocity_threshold": 500,
        },
        {
            "description": "Case with multiple saccades",
            "data": [(100, 100, 0), (200, 200, 100), (300, 300, 200), (300, 300, 250),
            (100, 100, 300), (200, 200, 400), (300, 300, 500)],
            "velocity_threshold": 500,
        },
        {
            "description": "Case with no saccades due to velocity threshold",
            "data": [(100, 100, 0), (102, 102, 100), (104, 104, 200), (106, 106, 300)],
            "velocity_threshold": 1000,
        },
        {
            "description": "Case with no saccades due to short duration",
            "data": [(100, 100, 0), (102, 102, 10), (104, 104, 20), (106, 106, 30)],
            "velocity_threshold": 500,
        },
        {
            "description": "Complex case with varied saccades",
            "data": generate_synthetic_gaze_data(100),
            "velocity_threshold": 300,
        },
        {
            "description": "Case with non-increasing timestamps",
            "data": [(100, 100, 0), (200, 200, 100), (300, 300, 50), (400, 400, 300)],
            "velocity_threshold": 500,
        },
        {
            "description": "Case with non-numeric values",
            "data": [(100, 100, 0), (200, '200', 100), (300, 300, '200'), (400, 400, 300)],
            "velocity_threshold": 500,
        },
        {
            "description": "Empty gaze points list",
            "data": [],
            "velocity_threshold": 500,
        },
        {
            "description": "Invalid velocity threshold",
            "data": [(100, 100, 0), (200, 200, 100), (300, 300, 200)],
            "velocity_threshold": -500,
        },
    ]
    
    for case in test_cases:
        print(f"Test Case: {case['description']}")
        try:
            saccades = saccade_detection(case["data"], case["velocity_threshold"])
            print_saccade_results(saccades)
        except ValueError as e:
            print(f"Error: {e}")
        print("\n")

# Function to print test results in a readable format
def print_smooth_pursuit_results(smooth_pursuits):
    print(len(smooth_pursuits))
    for i, (start_index, end_index, duration) in enumerate(smooth_pursuits):
        print(f"Smooth Pursuit {i+1}: Start Index: {start_index}, End Index: {end_index}, Duration: {duration:.2f} ms")

# Test cases
def test_smooth_pursuit_detection():
    test_cases = [
        {
            "description": "Simple case with one smooth pursuit",
            "data": [(100, 100, 0), (101, 101, 100), (102, 102, 200), (103, 103, 300), (104, 104, 400)],
            "time_window": 300,
            "velocity_threshold": 30,
            "direction_threshold": 10,
        },
        {
            "description": "Case with multiple smooth pursuits",
            "data": [(100, 100, 0), (101, 101, 100), (200, 200, 200), (201, 201, 300), (202, 202, 400)],
            "time_window": 100,
            "velocity_threshold": 30,
            "direction_threshold": 20,
        },
        {
            "description": "Case with no smooth pursuit due to high velocity",
            "data": [(100, 100, 0), (200, 200, 100), (300, 300, 200), (400, 400, 300)],
            "time_window": 200,
            "velocity_threshold": 10,
            "direction_threshold": 10,
        },
        {
            "description": "Case with no smooth pursuit due to high direction change",
            "data": [(100, 100, 0), (102, 100, 100), (104, 102, 200), (106, 104, 300)],
            "time_window": 200,
            "velocity_threshold": 50,
            "direction_threshold": 5,
        },
        {
            "description": "Complex case with varied smooth pursuits",
            "data": generate_synthetic_gaze_data(100),
            "time_window": 300,
            "velocity_threshold": 3000,
            "direction_threshold": 200,
        },
        {
            "description": "Case with non-increasing timestamps",
            "data": [(100, 100, 0), (101, 101, 100), (102, 102, 50), (103, 103, 300)],
            "time_window": 300,
            "velocity_threshold": 3000,
            "direction_threshold": 3000,
        },
        {
            "description": "Case with non-numeric values",
            "data": [(100, 100, 0), (200, '200', 100), (300, 300, '200'), (400, 400, 300)],
            "time_window": 300,
            "velocity_threshold": 30,
            "direction_threshold": 30,
        },
        {
            "description": "Empty gaze points list",
            "data": [],
            "time_window": 300,
            "velocity_threshold": 30,
            "direction_threshold": 30,
        },
        {
            "description": "Invalid time window",
            "data": [(100, 100, 0), (101, 101, 100), (102, 102, 200)],
            "time_window": -100,
            "velocity_threshold": 30,
            "direction_threshold": 30,
        },
        {
            "description": "Invalid velocity threshold",
            "data": [(100, 100, 0), (101, 101, 100), (102, 102, 200)],
            "time_window": 300,
            "velocity_threshold": -30,
            "direction_threshold": 30,
        },
        {
            "description": "Invalid direction threshold",
            "data": [(100, 100, 0), (101, 101, 100), (102, 102, 200)],
            "time_window": 300,
            "velocity_threshold": 30,
            "direction_threshold": -30,
        },
    ]
    
    for case in test_cases:
        print(f"Test Case: {case['description']}")
        try:
            smooth_pursuits = detect_smooth_pursuit(case["data"], case["time_window"], case["velocity_threshold"], case["direction_threshold"])
            print_smooth_pursuit_results(smooth_pursuits)
        except ValueError as e:
            print(f"Error: {e}")
        print("\n")

# Run the test cases
if __name__ == "__main__":
    test_fixation_detection()
    # test_saccade_detection()
    # test_smooth_pursuit_detection()
