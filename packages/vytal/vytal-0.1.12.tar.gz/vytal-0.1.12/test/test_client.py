from vytal.client import Client
import asyncio
import os
import sys
import time
import threading

# Configuration
API_KEY = "sk-3s6r5n64j4u"
IPD = 0.065  # Interpupillary distance in meters
VIDEO_PATH = "/Users/rayhanzirvi/vytalgaze-client/src/vytal/sample_video.MOV"
CALIBRATION_SAVE_DIRECTORY = "path_to_save_calibration"
CALIBRATION_DATA = None  # This will be populated after calibration

 # Initialize the Client with your API key and IPD
client = Client(API_KEY, IPD)

def test_calibration():
    global CALIBRATION_DATA
    try:
        CALIBRATION_DATA = client.calibrate(save_directory=CALIBRATION_SAVE_DIRECTORY)
        if CALIBRATION_DATA:
            print("Calibration successful!")
        else:
            print("Calibration failed or was interrupted.")
    except Exception as e:
        print(f"Calibration error: {e}")

def test_thread():
    # Start the API client in a separate thread
    # api_loop = client.start_thread(eye_frames=True)
    # api_loop = client.start_thread(calib=CALIBRATION_DATA, eye_frames=True)

    # TODO: show frames bug?
    api_loop = client.start_thread(calib=CALIBRATION_DATA, show_frame=True, eye_frames=True)
    
    # Run for 10 seconds and print predictions
    t0 = time.time()
    try:
        while time.time() - t0 < 10:
            if client.preds:
                print(client.preds[-1])
            time.sleep(1)
    except KeyboardInterrupt:
        print("Prediction interrupted by user.")
    finally:
        # End the thread gracefully
        client.end_thread(api_loop)

def test_predict_from_video():
    try:
        # if CALIBRATION_DATA is None:
        #     print("No calibration data available. Please perform calibration first.")
        #     return

        # Check if the video file exists
        # if not os.path.isfile(VIDEO_PATH):
        #     raise FileNotFoundError(f"No such file or directory: '{VIDEO_PATH}'")

        predictions = client.predict_from_video(VIDEO_PATH, CALIBRATION_DATA, eye_frames=False)
        if predictions:
            print("Video prediction successful!")
            print(predictions)
        else:
            print("Video prediction failed.")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except Exception as e:
        print(f"Error during video prediction: {e}")

async def test_predict_from_websocket():
    try:
        # if CALIBRATION_DATA is None:
        #     print("No calibration data available. Please perform calibration first.")
        #     return

        await client.init_websocket(cam_id=0, calib=CALIBRATION_DATA, eye_frames=False)
        predictions = await client.send_websocket_frame(show_frame=False, verbose=True)
        if predictions:
            print("WebSocket prediction successful!")
            print(predictions)
        else:
            print("WebSocket prediction failed.")
        await client.close_websocket()
    except Exception as e:
        print(f"Error during WebSocket prediction: {e}")
        await client.close_websocket()

def test_real_time_pred():
    try:
        # if CALIBRATION_DATA is None:
        #     print("No calibration data available. Please perform calibration first.")
        #     return

        predictions = client.real_time_pred(cam_id=0, calib=CALIBRATION_DATA, verbose=True, show_frame=False)
        if predictions:
            print("Real-time prediction successful!")
            print(predictions)
        else:
            print("Real-time prediction failed.")
    except Exception as e:
        print(f"Error during real-time prediction: {e}")

def main():
    # TODO: what happens if user enters non-numeric to input screen
    test_calibration()
    # test_thread()
    # test_predict_from_video()
    # asyncio.run(test_predict_from_websocket())
    # test_real_time_pred()

if __name__ == "__main__":
    main()
