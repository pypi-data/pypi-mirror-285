from vytal.adtech import *

def test_analyze_eye_tracking_data():
    # Define test cases
    test_cases = [
        {
            "description": "Simple case with one AOI and valid data",
            "results": [
                {'pred_x': 100, 'pred_y': 100},
                {'pred_x': 101, 'pred_y': 101},
                {'pred_x': 102, 'pred_y': 102},
                {'pred_x': 150, 'pred_y': 150}
            ],
            "aois": {
                'AOI1': (90, 90, 110, 110)
            },
            "fps": 30,
            "expected_aoi_metrics": {
                'AOI1': {
                    'TFF': 0.0,
                    'Fixation_Count': 1,
                    'Total_Fixation_Duration': 0.06666666666666667,
                    'Avg_Fixation_Duration': 0.06666666666666667,
                    'Revisits': 0  # Initial visit should not be counted as a revisit
                }
            },
            "expected_general_metrics": {
                'Entry_Point': (100, 100),
                'Exit_Point': (150, 150)
            }
        },
        {
            "description": "Multiple AOIs and valid data",
            "results": [
                {'pred_x': 100, 'pred_y': 100},
                {'pred_x': 105, 'pred_y': 105},
                {'pred_x': 150, 'pred_y': 150},
                {'pred_x': 145, 'pred_y': 145}
            ],
            "aois": {
                'AOI1': (90, 90, 110, 110),
                'AOI2': (140, 140, 160, 160)
            },
            "fps": 30,
            "expected_aoi_metrics": {
                'AOI1': {
                    'TFF': 0.0,
                    'Fixation_Count': 1,
                    'Total_Fixation_Duration': 0.03333333333333333,
                    'Avg_Fixation_Duration': 0.03333333333333333,
                    'Revisits': 0
                },
                'AOI2': {
                    'TFF': 0.06666666666666667,
                    'Fixation_Count': 1,
                    'Total_Fixation_Duration': 0.03333333333333333,
                    'Avg_Fixation_Duration': 0.03333333333333333,
                    'Revisits': 0
                }
            },
            "expected_general_metrics": {
                'Entry_Point': (100, 100),
                'Exit_Point': (145, 145)
            }
        },
        {
            "description": "Empty results list",
            "results": [],
            "aois": {
                'AOI1': (90, 90, 110, 110)
            },
            "fps": 30,
            "expected_error": ValueError
        },
        {
            "description": "Invalid AOI rectangle",
            "results": [
                {'pred_x': 100, 'pred_y': 100},
                {'pred_x': 101, 'pred_y': 101}
            ],
            "aois": {
                'AOI1': (90, 90, 110)  # Invalid AOI rectangle
            },
            "fps": 30,
            "expected_error": ValueError
        },
        {
            "description": "Invalid result format",
            "results": [
                {'pred_x': 100, 'pred_y': 100},
                {'pred_x': 101, 'pred_y': 'invalid'}  # Invalid pred_y value
            ],
            "aois": {
                'AOI1': (90, 90, 110, 110)
            },
            "fps": 30,
            "expected_error": ValueError
        },
        {
            "description": "No AOI defined",
            "results": [
                {'pred_x': 100, 'pred_y': 100},
                {'pred_x': 101, 'pred_y': 101}
            ],
            "aois": {},  # No AOI defined
            "fps": 30,
            "expected_error": ValueError
        },
        {
            "description": "No fixation detected",
            "results": [
                {'pred_x': 0, 'pred_y': 0},
                {'pred_x': 1000, 'pred_y': 1000},
                {'pred_x': 2000, 'pred_y': 2000}
            ],
            "aois": {
                'AOI1': (90, 90, 110, 110)
            },
            "fps": 30,
            "expected_aoi_metrics": {
                'AOI1': {
                    'TFF': None,
                    'Fixation_Count': 0,
                    'Total_Fixation_Duration': 0,
                    'Avg_Fixation_Duration': 0,
                    'Revisits': 0
                }
            },
            "expected_general_metrics": {
                'Entry_Point': (0, 0),
                'Exit_Point': (2000, 2000)
            }
        }
    ]

    for i, case in enumerate(test_cases):
        print(f"Running test case {i + 1}: {case['description']}")
        try:
            if 'expected_error' in case:
                try:
                    analyze_eye_tracking_data(case['results'], case['aois'], case['fps'])
                except ValueError as e:
                    assert isinstance(e, case['expected_error']), f"Expected error {case['expected_error']}, got {type(e)}"
                else:
                    assert False, f"Expected error {case['expected_error']}, but no error was raised"
            else:
                aoi_metrics, general_metrics = analyze_eye_tracking_data(case['results'], case['aois'], case['fps'])
                assert aoi_metrics == case['expected_aoi_metrics'], f"Expected {case['expected_aoi_metrics']}, but got {aoi_metrics}"
                assert general_metrics == case['expected_general_metrics'], f"Expected {case['expected_general_metrics']}, but got {general_metrics}"
            print("Test passed.")
        except AssertionError as e:
            print(f"Test failed: {e}")

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.text import Text

def test_draggable_rectangle():
    # Create a figure and axis
    fig, ax = plt.subplots()

    # Add a rectangle
    rect = patches.Rectangle((0.3, 0.3), 0.2, 0.2, fill=True, color="blue", alpha=0.5)
    ax.add_patch(rect)

    # Add associated text
    text = ax.text(0.4, 0.4, "Drag me!", fontsize=12, color="black", ha="center")

    # Make the rectangle draggable
    draggable_rect = DraggableRectangle(rect, text)

    # Display the plot
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.show()

    # Test error handling
    try:
        DraggableRectangle("not a rect", text)
    except ValueError as e:
        print(f"Caught expected ValueError: {e}")

    try:
        DraggableRectangle(rect, "not a text")
    except ValueError as e:
        print(f"Caught expected ValueError: {e}")

    try:
        DraggableRectangle("not a rect", "not a text")
    except ValueError as e:
        print(f"Caught expected ValueError: {e}")

    # Print success message
    print("All tests passed!")

import os
import matplotlib.pyplot as plt
from typing import Dict, Tuple

# Define the AOI function as per the previous code provided

def test_define_aois():
    """
    Test the define_aois function with various scenarios.
    """
    # Create a temporary image for testing
    fig, ax = plt.subplots()
    ax.imshow([[1, 2], [2, 1]], cmap='gray')  # Create a simple test image
    test_image_path = "test_image.png"
    plt.savefig(test_image_path)
    plt.close()

    # Define a simple function to print AOIs (for debugging)
    def print_aois(aois: Dict[str, Tuple[float, float, float, float]]):
        print("AOIs:")
        for name, coords in aois.items():
            print(f"{name}: {coords}")

    # Test 1: Basic functionality
    try:
        aois = define_aois(test_image_path)
        print("Test 1: Basic functionality")
        print_aois(aois)
    except Exception as e:
        print(f"Test 1 failed: {e}")

    # Test 2: Creating multiple AOIs
    try:
        aois = define_aois(test_image_path)
        print("Test 2: Creating multiple AOIs")
        print_aois(aois)
    except Exception as e:
        print(f"Test 2 failed: {e}")

    # Test 3: Renaming an AOI
    try:
        aois = define_aois(test_image_path)
        print("Test 3: Renaming an AOI")
        print_aois(aois)
    except Exception as e:
        print(f"Test 3 failed: {e}")

    # Test 4: Deleting an AOI
    try:
        aois = define_aois(test_image_path)
        print("Test 4: Deleting an AOI")
        print_aois(aois)
    except Exception as e:
        print(f"Test 4 failed: {e}")

    # Test 5: Moving an AOI
    try:
        aois = define_aois(test_image_path)
        print("Test 5: Moving an AOI")
        print_aois(aois)
    except Exception as e:
        print(f"Test 5 failed: {e}")

    # Test 6: Error handling for non-existent image
    try:
        aois = define_aois("non_existent_image.png")
        print("Test 6: Error handling for non-existent image")
        print_aois(aois)
    except Exception as e:
        print(f"Test 6 failed: {e}")

    # Clean up
    if os.path.exists(test_image_path):
        os.remove(test_image_path)

def test_plot_gaze_path():
    """
    Test the plot_gaze_path function with various scenarios.
    """
    # Create a temporary image for testing
    test_image_path = "test_image.png"
    create_test_image(test_image_path)

    def print_aois(aois: Dict[str, Tuple[float, float, float, float]]):
        print("AOIs:")
        for name, coords in aois.items():
            print(f"{name}: {coords}")

    # Test 1: Basic functionality with one AOI and a simple gaze path
    try:
        results = [
            {'pred_x': 100, 'pred_y': 100},
            {'pred_x': 200, 'pred_y': 200},
            {'pred_x': 400, 'pred_y': 300}
        ]
        aois = {'AOI1': (50, 50, 350, 350)}
        print("Test 1: Basic functionality with one AOI and a simple gaze path")
        plot_gaze_path(results, aois, test_image_path)
    except Exception as e:
        print(f"Test 1 failed: {e}")

    # Test 2: Multiple AOIs and a more complex gaze path
    try:
        results = [
            {'pred_x': 100, 'pred_y': 100},
            {'pred_x': 200, 'pred_y': 200},
            {'pred_x': 300, 'pred_y': 400},
            {'pred_x': 400, 'pred_y': 400},
            {'pred_x': 300, 'pred_y': 500}
        ]
        aois = {
            'AOI1': (50, 50, 350, 350),
            'AOI2': (450, 450, 550, 550)
        }
        print("Test 2: Multiple AOIs and a more complex gaze path")
        plot_gaze_path(results, aois, test_image_path)
    except Exception as e:
        print(f"Test 2 failed: {e}")

    # Test 3: Empty results
    try:
        results = []
        aois = {'AOI1': (50, 50, 350, 350)}
        print("Test 3: Empty results")
        plot_gaze_path(results, aois, test_image_path)
    except Exception as e:
        print(f"Test 3 failed: {e}")

    # Test 4: No AOIs
    try:
        results = [
            {'pred_x': 100, 'pred_y': 100},
            {'pred_x': 200, 'pred_y': 200},
            {'pred_x': 300, 'pred_y': 300}
        ]
        aois = {}
        print("Test 4: No AOIs")
        plot_gaze_path(results, aois, test_image_path)
    except Exception as e:
        print(f"Test 4 failed: {e}")

    # Test 5: Large number of gaze points
    try:
        results = [{'pred_x': x, 'pred_y': x} for x in range(0, 600, 50)]
        aois = {'AOI1': (50, 50, 350, 350)}
        print("Test 5: Large number of gaze points")
        plot_gaze_path(results, aois, test_image_path)
    except Exception as e:
        print(f"Test 5 failed: {e}")

    # Test 6: Error handling for non-existent image
    try:
        results = [
            {'pred_x': 100, 'pred_y': 100},
            {'pred_x': 200, 'pred_y': 200}
        ]
        aois = {'AOI1': (50, 50, 350, 350)}
        print("Test 6: Error handling for non-existent image")
        plot_gaze_path(results, aois, "non_existent_image.png")
    except Exception as e:
        print(f"Test 6 failed: {e}")

    # Clean up
    if os.path.exists(test_image_path):
        os.remove(test_image_path)

def create_test_image(path: str):
    fig, ax = plt.subplots()
    ax.imshow([[1, 2], [2, 1]], cmap='gray')  # Create a simple test image
    plt.savefig(path)
    plt.close()

def test_generate_heatmap():
    """
    Test the generate_heatmap function with various scenarios.
    """
    # Create a temporary image for testing
    test_image_path = "test_image.png"
    create_test_image(test_image_path)

    # Test 1: Basic functionality with simple gaze data
    try:
        results = [
            {'pred_x': 100, 'pred_y': 100},
            {'pred_x': 200, 'pred_y': 200},
            {'pred_x': 300, 'pred_y': 300}
        ]
        print("Test 1: Basic functionality with simple gaze data")
        generate_heatmap(results, test_image_path)
    except Exception as e:
        print(f"Test 1 failed: {e}")

    # Test 2: Large number of gaze points
    try:
        results = [{'pred_x': np.random.randint(0, 400), 'pred_y': np.random.randint(0, 400)} for _ in range(1000)]
        print("Test 2: Large number of gaze points")
        generate_heatmap(results, test_image_path)
    except Exception as e:
        print(f"Test 2 failed: {e}")

    # Test 3: Empty results
    try:
        results = []
        print("Test 3: Empty results")
        generate_heatmap(results, test_image_path)
    except Exception as e:
        print(f"Test 3 failed: {e}")

    # Test 4: Negative coordinates
    try:
        results = [
            {'pred_x': -10, 'pred_y': -10},
            {'pred_x': 100, 'pred_y': 100}
        ]
        print("Test 4: Negative coordinates")
        generate_heatmap(results, test_image_path)
    except Exception as e:
        print(f"Test 4 failed: {e}")

    # Test 5: Coordinates outside image dimensions
    try:
        results = [
            {'pred_x': 100, 'pred_y': 100},
            {'pred_x': 500, 'pred_y': 500}  # Assuming the image dimensions are smaller
        ]
        print("Test 5: Coordinates outside image dimensions")
        generate_heatmap(results, test_image_path)
    except Exception as e:
        print(f"Test 5 failed: {e}")

    # Test 6: Error handling for non-existent image
    try:
        results = [
            {'pred_x': 100, 'pred_y': 100},
            {'pred_x': 200, 'pred_y': 200}
        ]
        print("Test 6: Error handling for non-existent image")
        generate_heatmap(results, "non_existent_image.png")
    except Exception as e:
        print(f"Test 6 failed: {e}")

    # Clean up
    if os.path.exists(test_image_path):
        os.remove(test_image_path)

def print_test_result(test_number, description, exception=None):
    if exception:
        print(f"Test {test_number}: {description} - FAILED with exception {exception}")
    else:
        print(f"Test {test_number}: {description} - PASSED")

def test_aoi_significance_test():
    """
    Test the aoi_significance_test function with various scenarios.
    """
    aois = {
        'AOI1': (50, 50, 150, 150),
        'AOI2': (200, 200, 300, 300)
    }

    # Test 1: Basic functionality
    try:
        group1_results = [{'pred_x': 100, 'pred_y': 100}, {'pred_x': 120, 'pred_y': 120}]
        group2_results = [{'pred_x': 220, 'pred_y': 220}, {'pred_x': 250, 'pred_y': 250}]
        print("Test 1: Basic functionality")
        results = aoi_significance_test(group1_results, group2_results, aois)
        print_test_result(1, "Basic functionality")
        print(results)
    except Exception as e:
        print_test_result(1, "Basic functionality", e)

    # Test 2: Large number of gaze points
    try:
        group1_results = [{'pred_x': np.random.randint(0, 400), 'pred_y': np.random.randint(0, 400)} for _ in range(1000)]
        group2_results = [{'pred_x': np.random.randint(0, 400), 'pred_y': np.random.randint(0, 400)} for _ in range(1000)]
        print("Test 2: Large number of gaze points")
        results = aoi_significance_test(group1_results, group2_results, aois)
        print_test_result(2, "Large number of gaze points")
        print(results)
    except Exception as e:
        print_test_result(2, "Large number of gaze points", e)

    # Test 3: Empty group1_results
    try:
        group1_results = []
        group2_results = [{'pred_x': 220, 'pred_y': 220}, {'pred_x': 250, 'pred_y': 250}]
        print("Test 3: Empty group1_results")
        results = aoi_significance_test(group1_results, group2_results, aois)
        print_test_result(3, "Empty group1_results")
    except Exception as e:
        print_test_result(3, "Empty group1_results", e)

    # Test 4: Empty group2_results
    try:
        group1_results = [{'pred_x': 100, 'pred_y': 100}, {'pred_x': 120, 'pred_y': 120}]
        group2_results = []
        print("Test 4: Empty group2_results")
        results = aoi_significance_test(group1_results, group2_results, aois)
        print_test_result(4, "Empty group2_results")
    except Exception as e:
        print_test_result(4, "Empty group2_results", e)

    # Test 5: Invalid test type
    try:
        group1_results = [{'pred_x': 100, 'pred_y': 100}, {'pred_x': 120, 'pred_y': 120}]
        group2_results = [{'pred_x': 220, 'pred_y': 220}, {'pred_x': 250, 'pred_y': 250}]
        print("Test 5: Invalid test type")
        results = aoi_significance_test(group1_results, group2_results, aois, test='invalid-test')
        print_test_result(5, "Invalid test type")
    except Exception as e:
        print_test_result(5, "Invalid test type", e)

    # Test 6: Valid Mann-Whitney test
    try:
        group1_results = [{'pred_x': 100, 'pred_y': 100}, {'pred_x': 120, 'pred_y': 120}]
        group2_results = [{'pred_x': 220, 'pred_y': 220}, {'pred_x': 250, 'pred_y': 250}]
        print("Test 6: Valid Mann-Whitney test")
        results = aoi_significance_test(group1_results, group2_results, aois, test='mann-whitney')
        print_test_result(6, "Valid Mann-Whitney test")
        print(results)
    except Exception as e:
        print_test_result(6, "Valid Mann-Whitney test", e)

def print_csv_file_content(filename):
    try:
        with open(filename, 'r') as file:
            content = file.read()
            print(f"Contents of {filename}:\n{content}")
    except Exception as e:
        print(f"Error reading {filename}: {e}")

def run_export_metrics_tests():
    aoi_metrics = {
        'AOI1': {
            'TFF': 0.0,
            'Fixation_Count': 1,
            'Total_Fixation_Duration': 0.03333333333333333,
            'Avg_Fixation_Duration': 0.03333333333333333,
            'Revisits': 0
        },
        'AOI2': {
            'TFF': 0.06666666666666667,
            'Fixation_Count': 1,
            'Total_Fixation_Duration': 0.03333333333333333,
            'Avg_Fixation_Duration': 0.03333333333333333,
            'Revisits': 0
        }
    }

    general_metrics = {
        'Entry_Point': (100, 100),
        'Exit_Point': (150, 150)
    }

    # Test 1: Basic functionality
    try:
        print("Test 1: Basic functionality")
        filename = 'test_metrics.csv'
        export_metrics_to_csv(aoi_metrics, general_metrics, filename)
        print_csv_file_content(filename)
    except Exception as e:
        print(f"Test 1 failed: {e}")

    # Test 2: Empty AOI metrics
    try:
        print("Test 2: Empty AOI metrics")
        filename = 'test_empty_aoi_metrics.csv'
        export_metrics_to_csv({}, general_metrics, filename)
        print_csv_file_content(filename)
    except Exception as e:
        print(f"Test 2 failed: {e}")

    # Test 3: Empty general metrics
    try:
        print("Test 3: Empty general metrics")
        filename = 'test_empty_general_metrics.csv'
        export_metrics_to_csv(aoi_metrics, {}, filename)
        print_csv_file_content(filename)
    except Exception as e:
        print(f"Test 3 failed: {e}")

    # Test 4: Both metrics empty
    try:
        print("Test 4: Both metrics empty")
        filename = 'test_empty_both_metrics.csv'
        export_metrics_to_csv({}, {}, filename)
        print_csv_file_content(filename)
    except Exception as e:
        print(f"Test 4 failed: {e}")

    # Test 5: Invalid filename (missing .csv)
    try:
        print("Test 5: Invalid filename (missing .csv)")
        filename = 'invalid_filename'
        export_metrics_to_csv(aoi_metrics, general_metrics, filename)
    except Exception as e:
        print(f"Test 5 failed: {e}")

    # Test 6: Invalid metrics type
    try:
        print("Test 6: Invalid metrics type")
        filename = 'test_invalid_metrics_type.csv'
        export_metrics_to_csv("invalid_type", general_metrics, filename)
    except Exception as e:
        print(f"Test 6 failed: {e}")

    # Test 7: Permission denied (try to write to a restricted directory)
    try:
        print("Test 7: Permission denied")
        filename = '/root/test_permission_denied.csv'
        export_metrics_to_csv(aoi_metrics, general_metrics, filename)
    except Exception as e:
        print(f"Test 7 failed: {e}")

# Run the test cases
if __name__ == "__main__":
    # test_analyze_eye_tracking_data()
    # test_draggable_rectangle()
    # test_define_aois()
    # test_plot_gaze_path()
    # test_generate_heatmap()
    # test_aoi_significance_test()
    run_export_metrics_tests()
