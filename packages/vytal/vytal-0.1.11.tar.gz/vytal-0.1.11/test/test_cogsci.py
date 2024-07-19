import unittest
import torch
from typing import List, Dict
from vytal.cogsci import *

# Testing script
def run_derivative_tests():
    # Define some test data
    test_data_valid = [
        {
            'time': 1000,
            'left': [1.0, 2.0, 3.0],
            'right': [1.1, 2.1, 3.1],
            'face': [0.1, 0.2, 0.3],
            'left_PoG': [5.0, 6.0],
            'right_PoG': [5.1, 6.1],
            'blink': 0.0
        },
        {
            'time': 2000,
            'left': [2.0, 3.2, 4.0],
            'right': [2.1, 3.1, 4.1],
            'face': [0.2, 0.3, 0.4],
            'left_PoG': [6.0, 7.0],
            'right_PoG': [6.1, 7.1],
            'blink': 0.1
        },
        {
            'time': 2500,
            'left': [3.0, 4.0, 5.0],
            'right': [3.1, 4.1, 5.1],
            'face': [0.3, 0.4, 0.5],
            'left_PoG': [7.0, 8.0],
            'right_PoG': [7.1, 8.1],
            'blink': 0.2
        }
    ]

    test_data_empty = []

    test_data_missing_keys = [
        {
            'time': 1000,
            'left': [1.0, 2.0, 3.0]
        }
    ]

    test_data_invalid_type = [
        {
            'time': 1000,
            'left': 'invalid',
            'right': [1.1, 2.1, 3.1],
            'face': [0.1, 0.2, 0.3],
            'left_PoG': [5.0, 6.0],
            'right_PoG': [5.1, 6.1],
            'blink': 0.0
        }
    ]

    # Test 1: Valid data
    try:
        print("Test 1: Valid data")
        derivatives = calc_velocities(test_data_valid)
        print("Derivatives calculated successfully.")
        for key, value in derivatives.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Test 1 failed: {e}")

    # Test 2: Empty data
    try:
        print("\nTest 2: Empty data")
        calc_velocities(test_data_empty)
    except ValueError as e:
        print(f"Expected error: {e}")

    # Test 3: Missing keys
    try:
        print("\nTest 3: Missing keys")
        calc_velocities(test_data_missing_keys)
    except KeyError as e:
        print(f"Expected error: {e}")

    # Test 4: Invalid data type
    try:
        print("\nTest 4: Invalid data type")
        calc_velocities(test_data_invalid_type)
    except ValueError as e:
        print(f"Expected error: {e}")

    # Test 5: Inconsistent lengths
    try:
        print("\nTest 5: Inconsistent lengths")
        inconsistent_data = test_data_valid.copy()
        inconsistent_data[0]['right'] = [1.1, 2.1]
        calc_velocities(inconsistent_data)
    except ValueError as e:
        print(f"Expected error: {e}")

    # Test 6: Single time point (should return NaNs)
    try:
        print("\nTest 6: Single time point")
        single_point_data = [
            {
                'time': 1000,
                'left': [1.0, 2.0, 3.0],
                'right': [1.1, 2.1, 3.1],
                'face': [0.1, 0.2, 0.3],
                'left_PoG': [5.0, 6.0],
                'right_PoG': [5.1, 6.1],
                'blink': 0.0
            }
        ]
        derivatives = calc_velocities(single_point_data)
        print("Derivatives calculated successfully.")
        for key, value in derivatives.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Test 6 failed: {e}")

# class TestEyeTrackingAnalyzer(unittest.TestCase):
#     def setUp(self):
#         # Sample data mimicking eye tracking output
#         self.sample_data = [
#             {'time': 0, 'left': 0.1, 'right': 0.1, 'face': 0.0, 'left_PoG': 0.2, 'right_PoG': 0.2, 'blink': 0},
#             {'time': 100, 'left': 0.1, 'right': 0.1, 'face': 0.0, 'left_PoG': 0.2, 'right_PoG': 0.2, 'blink': 0},
#             {'time': 200, 'left': 0.2, 'right': 0.2, 'face': 0.1, 'left_PoG': 0.3, 'right_PoG': 0.3, 'blink': 0},
#             {'time': 300, 'left': 0.3, 'right': 0.3, 'face': 0.2, 'left_PoG': 0.4, 'right_PoG': 0.4, 'blink': 0}
#         ]
#         self.analyzer = EyeTrackingAnalyzer(data=self.sample_data, sampling_rate=10.0)

#     def test_preprocess_data(self):
#         # Check if all keys are present
#         processed_keys = set(self.analyzer.data.keys())
#         expected_keys = {'time', 'left', 'right', 'face', 'left_PoG', 'right_PoG', 'blink', 
#                          'left_velocity', 'right_velocity', 'face_velocity', 'left_PoG_velocity', 'right_PoG_velocity', 'blink_velocity'}
#         self.assertEqual(processed_keys, expected_keys)

#     def test_calc_velocities(self):
#         # Check calculated velocities for correctness
#         left_velocity = self.analyzer.data['left_velocity']
#         expected_velocity = torch.tensor([0, 1, 1, torch.nan]).unsqueeze(1)  # Add .unsqueeze(1) to match shape
#         self.assertTrue(torch.allclose(left_velocity, expected_velocity, equal_nan=True))

#     def test_find_saccade_locs(self):
#         # Assuming the functionality of find_saccade_locs is implemented correctly
#         left_saccades, right_saccades = self.analyzer.find_saccade_locs()
#         self.assertIsInstance(left_saccades, list)
#         self.assertIsInstance(right_saccades, list)

#     def test_remove_overlapping_saccades(self):
#         # Simulate overlapping saccade scenario and test removal
#         saccades = [{'start': 0, 'end': 5, 'peak_velocity': 20}, {'start': 3, 'end': 8, 'peak_velocity': 25}]
#         cleaned = EyeTrackingAnalyzer.remove_overlapping_saccades(saccades)
#         self.assertEqual(len(cleaned), 1)
#         self.assertEqual(cleaned[0]['peak_velocity'], 25)

class TestEyeTrackingAnalyzer(unittest.TestCase):
    def setUp(self):
        # Initialize with sample data that should clearly contain detectable saccades
        self.sample_data = [
            {'time': 1000*i, 'left': i % 10, 'right': i % 10, 'face': 0, 'left_PoG': 0, 'right_PoG': 0, 'blink': 0} for i in range(100)
        ]
        # Simulate a saccade with a sudden jump in eye position
        for i in range(50, 55):
            self.sample_data[i]['left'] += 100
            self.sample_data[i]['right'] += 100
        self.analyzer = EyeTrackingAnalyzer(data=self.sample_data, sampling_rate=100.0)

    def test_find_saccade_locs(self):
        # Setting thresholds for detection
        velocity_threshold = 1000  # set threshold to catch the simulated saccade
        min_duration = 10  # minimum duration in milliseconds of a saccade

        # Invoke the method
        left_saccades, right_saccades = self.analyzer.find_saccade_locs(velocity_threshold, min_duration)

        # Check that saccades are detected correctly
        self.assertGreater(len(left_saccades), 0, "Should detect at least one saccade in left eye")
        self.assertGreater(len(right_saccades), 0, "Should detect at least one saccade in right eye")

        # Optional: Check specific properties of the detected saccades
        for saccade in left_saccades:
            start, end, peak = saccade
            # print(start)
            # print(end)
            # print(peak)
            # self.assertTrue(50 <= start <= 54, "Saccade start index should be within the range of the simulated saccade")
            # self.assertTrue(50 <= end <= 54, "Saccade end index should be within the range of the simulated saccade")
            # self.assertTrue(50 <= peak <= 54, "Saccade peak index should be within the range of the simulated saccade")

class TestDetectFixations(unittest.TestCase):
    def setUp(self):
        self.data = [
            {'time': i * 20, 'left': i, 'right': i, 'face': i, 'POG_x': (i // 10) * 5, 'POG_y': (i // 10) * 5} for i in range(100)
        ]

    def test_normal_operation(self):
        fixations = detect_fixations(self.data, dispersion_threshold=0.5, duration_threshold=50, angle_type='face')
        self.assertTrue(len(fixations) > 0, "Should detect fixations under normal conditions.")

    def test_no_fixation_detected(self):
        fixations = detect_fixations(self.data, dispersion_threshold=0.1, duration_threshold=1000, angle_type='face')
        self.assertEqual(len(fixations), 0, "Should not detect any fixations with high threshold or long duration.")

    def test_error_on_empty_data(self):
        with self.assertRaises(ValueError):
            detect_fixations([], dispersion_threshold=1.0, duration_threshold=100, angle_type='face')

    def test_error_on_missing_keys(self):
        with self.assertRaises(ValueError):
            detect_fixations([{'time': 1, 'POG_x': 2}], dispersion_threshold=1.0, duration_threshold=100, angle_type='face')

    def test_edge_case_last_element(self):
        # Ensure last element handling is correct
        fixations = detect_fixations(self.data, dispersion_threshold=4, duration_threshold=100, angle_type='face')
        self.assertTrue(len(fixations) > 0, "Should detect at least one fixation.")
        self.assertTrue(fixations[-1]['end_index'] == len(self.data) - 1, "Last fixation should include the last element if criteria met.")

if __name__ == "__main__":
    # run_derivative_tests()
    unittest.main()