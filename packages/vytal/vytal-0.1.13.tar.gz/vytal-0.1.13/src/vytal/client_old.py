import scipy
import time, requests, numpy as np, base64, torch, cv2, websockets, asyncio, sys, pygame, cv2, json, math, threading, pickle, io, os
from typing import Union
from PyQt5.QtWidgets import QApplication
import torch.nn.functional as F

def numpy_to_bytes(array):
    metadata = {
        'dtype': str(array.dtype),
        'shape': array.shape
    }
    data = array.tobytes()
    metadata_encoded = base64.b64encode(str(metadata).encode('utf-8')).decode('utf-8')
    data_encoded = base64.b64encode(data).decode('utf-8')
    return {"metadata": metadata_encoded, "data": data_encoded}

def bytes_to_numpy(data):
    metadata_bstring = data['metadata']
    data_bstring = data['data']
    metadata_decoded = eval(base64.b64decode(metadata_bstring).decode('utf-8'))
    data_decoded = base64.b64decode(data_bstring)
    array = np.frombuffer(data_decoded, dtype=metadata_decoded['dtype']).reshape(metadata_decoded['shape'])
    return array

def tensor_to_bytes(tensor):
    # Convert the PyTorch dtype to a string format that NumPy understands
    numpy_dtype_str = str(tensor.numpy().dtype)
    
    metadata = {
        'dtype': numpy_dtype_str,
        'shape': tensor.shape
    }
    data = tensor.numpy().tobytes()
    metadata_encoded = base64.b64encode(str(metadata).encode('utf-8')).decode('utf-8')
    data_encoded = base64.b64encode(data).decode('utf-8')
    return {"metadata": metadata_encoded, "data": data_encoded}

def bytes_to_tensor(data):
    metadata_bstring = data['metadata']
    data_bstring = data['data']
    metadata_decoded = eval(base64.b64decode(metadata_bstring).decode('utf-8'))
    data_decoded = base64.b64decode(data_bstring)
    
    # Convert the dtype string back into a NumPy dtype
    numpy_dtype = np.dtype(metadata_decoded['dtype'])
    
    array = np.frombuffer(data_decoded, dtype=numpy_dtype).reshape(metadata_decoded['shape'])
    tensor = torch.from_numpy(array)
    return tensor

def convert_dict_values_to_bytes(d):
    if d is None: return None

    result = {}
    for key, value in d.items():
        if isinstance(value, np.ndarray):
            result[key] = numpy_to_bytes(value)
        elif isinstance(value, torch.Tensor):
            result[key] = tensor_to_bytes(value)
        else:
            result[key] = value  # Leave other types unchanged
    return result

def convert_dict_values_to_tensor(d):
    result = {}
    for key, value in d.items():
        result[key] = bytes_to_tensor(value)
    return result

def convert_dict_values_to_numpy(d):
    result = {}
    for key, value in d.items():
        result[key] = bytes_to_numpy(value)
    return result

class TextInput:
    def __init__(self, x, y, width, height, screen_width, color="dodgerblue2"):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.font = pygame.font.Font(os.path.join(os.path.dirname(__file__), "Inter.ttf"), int(48 * screen_width / 1500))
        self.active = False
        self.border_color = pygame.Color(color)
        self.border_width = 3

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

    def draw(self, surface):
        color = pygame.Color('#079eab') if self.active else self.border_color
        pygame.draw.rect(surface, color, self.rect, self.border_width)
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (self.rect.x + 10, text_y))

class Button:
    def __init__(self, x, y, width, height, screen_width, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.original_text = text
        self.color = pygame.Color(color)
        self.original_color = pygame.Color(color)  # Create a new Color object instead of copying
        self.hover_color = self.color.lerp(pygame.Color('white'), 0.3)
        self.font = pygame.font.Font(os.path.join(os.path.dirname(__file__), "Inter.ttf"), int(48 * screen_width / 1500))
        self.is_hovered = False
        self.is_pressed = False
        self.screen_width = screen_width

    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=int(20 * self.screen_width / 1500))
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.is_pressed = True
                self.text = "Starting..."
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed:
                self.is_pressed = False
                self.text = self.original_text
                if self.is_hovered:
                    return True
        return False

    def reset(self):
        self.is_pressed = False
        self.text = self.original_text

class Checkbox:
    def __init__(self, x, y, width, height, color=(0, 0, 0)):
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers")
        self.rect = pygame.Rect(x, y, width, height)
        self.checked = False
        self.color = color

    def handle_event(self, event):
        try:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.checked = not self.checked
        except AttributeError as e:
            print(f"AttributeError occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def draw(self, surface):
        try:
            pygame.draw.rect(surface, self.color, self.rect, 2)
            if self.checked:
                pygame.draw.line(surface, self.color, self.rect.topleft, self.rect.bottomright, 2)
                pygame.draw.line(surface, self.color, self.rect.topright, self.rect.bottomleft, 2)
        except Exception as e:
            print(f"An error occurred while drawing the checkbox: {e}")

def tensor_to_surface(tensor):
    np_array = tensor.squeeze().permute(1, 2, 0).cpu().numpy()

    # Clean array
    np_array = np.nan_to_num(np_array, nan=0.0, posinf=0.0, neginf=0.0)
    np_array = (np_array * 255).astype(np.uint8)

    # Rotate the numpy array 90 degrees to the right
    np_array = np.rot90(np_array, k=-1)
    np_array = np.rot90(np_array, k=-1)
    np_array = np.rot90(np_array, k=-1)
    
    surface = pygame.surfarray.make_surface(np_array)
    return surface

def display_dynamic_photo(surface, photo, region):
    photo = pygame.transform.scale(photo, (region[1][0] - region[0][0], region[1][1] - region[0][1]))
    surface.blit(photo, region[0])


def calculate_dot_positions(width, height):
    x_positions = np.linspace(0.1 * width, 0.9 * width, 4)
    y_positions = np.linspace(0.1 * height, 0.9 * height, 4)
    return [(int(x), int(y)) for y in y_positions for x in x_positions]


def is_gaze_stable(predictions_window, threshold=3):
    # if len(predictions_window) < 60:
    #     return False, {}

    if not predictions_window:
        return False, {}
    
    original_length = len(predictions_window)
    predictions_window = [p for p in predictions_window if not (p['left'].isnan().any() or p['right'].isnan().any())]

    if original_length - len(predictions_window) > 10:
        return False, {}

    lefts = np.squeeze(np.array([p['left'].numpy() for p in predictions_window]))
    rights = np.squeeze(np.array([p['right'].numpy() for p in predictions_window]))

    if lefts.shape[-1] != 2 or rights.shape[-1] != 2 or lefts.ndim != 2 or rights.ndim != 2:
        return False, {}

    angles = (lefts + rights) / 2

    avg_face_angle = np.nanmean(angles, axis=0)

    if np.isnan(avg_face_angle).any():
            return False, {}

    def pitchyaw_to_vector(py: torch.Tensor) -> torch.Tensor:
        # Converts pitch and yaw angles (n x 2 x 1) to a 3D direction vector (polar to cartesian) (n x 3 x 1).

        if (py.shape[1] != 2):
            raise ValueError('Input tensor must have 2 columns, not %d' % py.shape[1])

        sin, cos = torch.sin(py), torch.cos(py)
        direction = torch.stack([cos[:, 0] * sin[:, 1],
                                 sin[:, 0],
                                 cos[:, 0] * cos[:, 1]],
                                dim=1)
        return direction

    def angular_error(a, b):
        try:
            a = torch.tensor(a, dtype=torch.float32).reshape((1, 2, 1))
            b = torch.tensor(b, dtype=torch.float32).reshape((1, 2, 1))
        except Exception as e:
            print(f"Error reshaping tensors: {e}")
            return float('inf')  # Return a large value to indicate error
        a = pitchyaw_to_vector(a)
        b = pitchyaw_to_vector(b)
        sim = F.cosine_similarity(a, b, dim=1, eps=1e-8)
        sim = F.hardtanh_(sim, min_val=-1 + 1e-8, max_val=1 - 1e-8)
        return (torch.acos(sim) * 180. / np.pi).item()

    angular_diffs = [angular_error(avg_face_angle, angle) for angle in angles]
    mean_angular_diff = np.mean(angular_diffs)
    median_angular_diff = np.median(angular_diffs)
    std_angular_diff = np.std(angular_diffs)

    stats = {
        "mean": mean_angular_diff,
        "median": median_angular_diff,
        "std": std_angular_diff
    }

    return (mean_angular_diff < threshold), stats


def draw_spinning_triangle(surface, position, size, angle):
    triangle_shape = [
        (0, -size),
        (size * math.sqrt(3) / 2, size / 2),
        (-size * math.sqrt(3) / 2, size / 2)
    ]
    rotated_triangle = [
        (int(x * math.cos(angle) - y * math.sin(angle) + position[0]),
         int(x * math.sin(angle) + y * math.cos(angle) + position[1]))
        for x, y in triangle_shape
    ]
    pygame.draw.polygon(surface, (0, 0, 0), rotated_triangle)

def process_calib_type(calib):
    if type(calib) == str:
        with open(calib, 'rb') as f:
            calib = pickle.load(f)
            b = io.BytesIO()
            pickle.dump(calib, b)
            calib = str(b.getvalue())
    elif type(calib) == bytes:
        calib = str(calib)
    elif type(calib) == scipy.interpolate._rbfinterp.RBFInterpolator:
        b = io.BytesIO()
        pickle.dump(calib, b)
        calib = str(b.getvalue())
    
    return calib

class Client:
    def __init__(self, api_key: str, ipd: float = None):
        self.api_key = api_key
        self.ipd = ipd
        self.cap = None
        self.websocket = None
        self.frame = None
    
    def calibrate(self, save_directory: str = None):
        # video_path, w, h, calibration_points, time_slices = calibration_gui()
        pygame.init()
        infoObject = pygame.display.Info()
        screen_width, screen_height = infoObject.current_w, infoObject.current_h
        screen = pygame.display.set_mode((screen_width, screen_height))
        
        vytal_api_loop = self.start_thread(eye_frames=True)
        try:
            original_bg = pygame.image.load(os.path.join(os.path.dirname(__file__), "background.png"))
        except pygame.error as e:
            raise FileNotFoundError(f"Background image not found: {e}")
        bg_width, bg_height = original_bg.get_size()
        scale_factor = min(screen_width / bg_width, screen_height / bg_height)
        new_bg_width, new_bg_height = int(bg_width * scale_factor), int(bg_height * scale_factor)
        background = pygame.transform.scale(original_bg, (new_bg_width, new_bg_height))
        bg_offset_x, bg_offset_y = (screen_width - new_bg_width) // 2, (screen_height - new_bg_height) // 2
        
        def scale_coords(x, y):
            return (int(x * scale_factor) + bg_offset_x, int(y * scale_factor) + bg_offset_y)
        
        dynamic_photo_region = (scale_coords(2240, 350), scale_coords(3628, 975))
        text_box_1_region = (scale_coords(3092, 1120), scale_coords(3587, 1306))
        text_box_2_region = (scale_coords(3092, 1432), scale_coords(3587, 1618))
        begin_button_region = (scale_coords(2240, 1710), scale_coords(2995, 1910))
        checkbox_region = (scale_coords(3110, 159), scale_coords(3230, 261))
        
        def input_screen():
            text_input1 = TextInput(*text_box_1_region[0],
                                    text_box_1_region[1][0] - text_box_1_region[0][0],
                                    text_box_1_region[1][1] - text_box_1_region[0][1], screen_width, "#04545c")
            text_input2 = TextInput(*text_box_2_region[0],
                                    text_box_2_region[1][0] - text_box_2_region[0][0],
                                    text_box_2_region[1][1] - text_box_2_region[0][1], screen_width, "#04545c")
            begin_button = Button(*begin_button_region[0],
                                begin_button_region[1][0] - begin_button_region[0][0],
                                begin_button_region[1][1] - begin_button_region[0][1],
                                screen_width, "Begin", "#04545c")
            checkbox = Checkbox(*checkbox_region[0],
                                checkbox_region[1][0] - checkbox_region[0][0],
                                checkbox_region[1][1] - checkbox_region[0][1])

            clock = pygame.time.Clock()

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        return None, None
                    text_input1.handle_event(event)
                    text_input2.handle_event(event)
                    checkbox.handle_event(event)
                    if begin_button.handle_event(event):
                        if text_input1.text and text_input2.text and checkbox.checked:
                            return text_input1.text, text_input2.text

                screen.blit(background, (bg_offset_x, bg_offset_y))

                if len(self.preds) > 0:
                    latest_pred = self.preds[-1]
                    if 'left_eye_patch' in latest_pred and 'right_eye_patch' in latest_pred:
                        left_eye_surface = tensor_to_surface(latest_pred['left_eye_patch'])
                        right_eye_surface = tensor_to_surface(latest_pred['right_eye_patch'])
                        # print(left_eye_surface)

                        # Combine left and right eye patches
                        combined_width = left_eye_surface.get_width() + right_eye_surface.get_width()
                        combined_height = max(left_eye_surface.get_height(), right_eye_surface.get_height())
                        combined_surface = pygame.Surface((combined_width, combined_height))
                        combined_surface.blit(left_eye_surface, (0, 0))
                        combined_surface.blit(right_eye_surface, (left_eye_surface.get_width(), 0))

                        # Scale and display in dynamic_photo_region
                        scaled_surface = pygame.transform.scale(combined_surface,
                                                                (dynamic_photo_region[1][0] - dynamic_photo_region[0][0],
                                                                dynamic_photo_region[1][1] - dynamic_photo_region[0][1]))
                        screen.blit(scaled_surface, dynamic_photo_region[0])

                text_input1.draw(screen)
                text_input2.draw(screen)
                begin_button.draw(screen)
                checkbox.draw(screen)
                pygame.display.flip()
                clock.tick(30)
        
        def calibration():
            results = []
            dots = calculate_dot_positions(screen_width, screen_height)
            
            pred_len = len(self.preds)
            time.sleep(1)
            window = 2 * (len(self.preds) - pred_len)
            # print(window)
            
            last_complete = len(self.preds)

            for i, dot in enumerate(dots):
                screen.fill((255, 255, 255))
                start_time = time.time()
                angle = 0
                spin_speed = 0.15

                # Add a 5-second break after the 8th point
                if i == 8:
                    break_start_time = time.time()
                    font = pygame.font.Font(os.path.join(os.path.dirname(__file__), "Inter.ttf"), 36)
                    
                    while time.time() - break_start_time < 5:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                                pygame.quit()
                                return results
                        
                        screen.fill((255, 255, 255))
                        remaining_time = int(5 - (time.time() - break_start_time))
                        text = font.render(f"Break time: {remaining_time+1} second{'s' if remaining_time!=0 else ''}", True, (0, 0, 0))
                        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
                        screen.blit(text, text_rect)
                        pygame.display.flip()
                        pygame.time.delay(33)
                    
                    last_complete = len(self.preds)

                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                            pygame.quit()
                            return results

                    screen.fill((255, 255, 255))
                    draw_spinning_triangle(screen, dot, 15, angle)
                    pygame.display.flip()

                    angle += spin_speed
                    spin_speed = min(spin_speed + 0.01, 0.5)

                    if len(self.preds) - last_complete >= window and (stable := is_gaze_stable(self.preds[-window:]))[0]:
                        predictions = [{k: v.tolist() for k, v in p.items() if 'eye_patch' not in k} for p in self.preds[-window:]]
                        # print(stable[1])
                        results.append({
                            "dot": dot,
                            "predictions": predictions,
                            "stats": stable[1],
                        })
                        last_complete = len(self.preds)
                        break

                    if time.time() - start_time > 10:
                        print(f"Calibration failed on dot {dot}")
                        last_complete = len(self.preds)
                        break

                    pygame.time.delay(33)

            return results
        
        input1, input2 = input_screen()
        if input1 is None or input2 is None:
            self.end_thread(vytal_api_loop)
            pygame.quit()
            cv2.destroyAllWindows()
            return

        results = calibration()
        results = {"input1": input1, "input2": input2, "calibration_results": results}

        self.end_thread(vytal_api_loop)
        pygame.quit()
        cv2.destroyAllWindows()
        
        self.preds = []
        self.cap = None
        self.websocket = None
        self.frame = None
        
        function_endpoint = "video/calibrate"
        params = {"api_key": self.api_key}
        response = requests.post(
            f'http://ec2-54-208-48-146.compute-1.amazonaws.com:8000/{function_endpoint}',
            # f'http://127.0.0.1:8000/{function_endpoint}',
            params=params,
            data=json.dumps(results),
            timeout=1000,
        )
        
        res = response.json()
        
        if save_directory is not None and "data" in res:
            save_path = os.path.join(save_directory, "calibration.pkl")
            with open(save_path, 'wb') as f:
                f.write(eval(res["data"]))
        
        if "data" in res:
            b = io.BytesIO()
            b.write(eval(res["data"]))
            b.seek(0)
            return pickle.load(b)
        else:
            return res
                   
    def predict_from_video(self, video_path: str, calib: Union[scipy.interpolate._rbfinterp.RBFInterpolator, str, bytes] = None, eye_frames: bool = False):    
        function_endpoint = "video/handle_video"

        # Check if the video file exists
        if not os.path.isfile(video_path):
            raise FileNotFoundError(f"No such file or directory: '{video_path}'")
        
        if calib is not None:
            try:
                calib = process_calib_type(calib)
            except Exception as e:
                print(f"Error processing calibration data: {e}")
                return None

        with open(video_path, 'rb') as f:
            params = {"api_key": self.api_key}
            if calib is not None: params["calib_rbf"] = calib
            if self.ipd is not None:
                params["ipd"] = "%.3f" % self.ipd
            params["eye_frames"] = eye_frames

            try:
                response = requests.post(
                    f'http://ec2-54-208-48-146.compute-1.amazonaws.com:8000/{function_endpoint}',
                    params=params,
                    data=f.read(),
                    timeout=1000,
                )
                response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                return None
            
            try:
                response_json = response.json()
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response: {e}")
                return None

            try:
                result = {}
                for key, value in response_json.items():
                    result[key] = bytes_to_tensor(value)
            except Exception as e:
                print(f"Error processing response data: {e}")
                result = response_json
            
            # try:
            #     result = {}
            #     for key, value in response.json().items():
            #         result[key] = bytes_to_tensor(value)
            # except:
            #     result = response.json()

        return result
    
    async def init_websocket(self, cam_id: int = 0, calib: Union[scipy.interpolate._rbfinterp.RBFInterpolator, str, bytes] = None, eye_frames: bool = False):
        if calib is not None:
            calib = process_calib_type(calib)

        function_endpoint = f"ws://ec2-54-208-48-146.compute-1.amazonaws.com:8000/ws/predict?api_key={self.api_key}&eye_frames={eye_frames}"
        # function_endpoint = f"ws://127.0.0.1:8000/ws/predict?api_key={self.api_key}"
        if calib is not None: function_endpoint += f"&calib_rbf={calib}"
        if self.ipd is not None: function_endpoint += "&ipd=%.3f" % self.ipd
        self.websocket = await websockets.connect(function_endpoint)
        self.cap = cv2.VideoCapture(cam_id)
        
    async def close_websocket(self):
        await self.websocket.close()
        self.cap.release()
        cv2.destroyAllWindows()
    
    async def send_websocket_frame(self, show_frame: bool = False, verbose: bool = False):
        while True:
            ret, frame = self.cap.read()
            self.frame = frame
            if not ret:
                break

            _, buffer = cv2.imencode('.jpg', frame)
            image_bytes = base64.b64encode(buffer).decode('utf-8')
                        
            await self.websocket.send(str(image_bytes) + "==abc==")
            
            response = await self.websocket.recv()
            response = convert_dict_values_to_tensor(eval(response))

            if show_frame:
                cv2.imshow('Live Stream', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                if verbose:
                    print(f"Response from server: {response}")
                    print()
                
            return response
    
    def start_thread(self, cam_id: int = 0, calib: Union[scipy.interpolate._rbfinterp.RBFInterpolator, str, bytes] = None, verbose: bool = False, show_frame: bool = False, eye_frames: bool = False):
        self.preds = []
        async def main():
            try:
                await self.init_websocket(cam_id, calib, eye_frames)
                # print("WebSocket connection established.")
            except Exception as e:
                print("Failed to connect to WebSocket server:", e)
                await self.close_websocket()
                return
            
            while True:
                if not self.cap or not self.websocket:
                    continue
                try:
                    pred = await self.send_websocket_frame(show_frame, verbose)
                    self.preds.append(pred)
                except Exception as e:
                    await self.close_websocket()
                    break

        def loop_in_thread(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        loop = asyncio.get_event_loop()
        t = threading.Thread(target=loop_in_thread, args=(loop,))
        t.start()

        task = asyncio.run_coroutine_threadsafe(main(), loop)
        while not self.preds:
            continue
        
        return loop

    def end_thread(self, loop):
        tasks = asyncio.all_tasks(loop)
        for t in tasks:
            t.cancel()
        loop.stop()

    async def predict_from_websocket(self, cam_id: int = 0, calib: Union[scipy.interpolate._rbfinterp.RBFInterpolator, str, bytes] = None, verbose: bool = False, show_frame: bool = False):
        function_endpoint = f"ws://ec2-54-208-48-146.compute-1.amazonaws.com:8000/ws/predict?api_key={self.api_key}"
        # function_endpoint = f"ws://ec2-54-208-48-146.compute-1.amazonaws.com:5000/ws/predict?api_key={self.api_key}"
        # function_endpoint = f"ws://127.0.0.1:8000/ws/predict?api_key={self.api_key}"
        if calib is not None:
            calib = process_calib_type(calib)
            function_endpoint += f"&calib_rbf={calib}"
        if self.ipd is not None: function_endpoint += "&ipd=%.3f" % self.ipd
        start_time = time.time()
        self.preds = []
        try:
            async with websockets.connect(function_endpoint) as websocket:
                print("WebSocket connection established")
                cap = cv2.VideoCapture(cam_id) 
                start_time = time.time()
                print("Opened camera feed")

                async def send_frames():
                    try:
                        while True:
                            ret, frame = cap.read()
                            if not ret:
                                break

                            _, buffer = cv2.imencode('.jpg', frame)
                            image_bytes = base64.b64encode(buffer).decode('utf-8')

                            await websocket.send(str(image_bytes) + "==abc==")

                            if show_frame:
                                cv2.imshow('Live Stream', frame)
                                if cv2.waitKey(1) & 0xFF == ord('q'):
                                    break
                    finally:
                        cap.release()
                        cv2.destroyAllWindows()

                async def receive_responses():
                    while True:
                        response = await websocket.recv()
                        response = convert_dict_values_to_tensor(eval(response))
                        self.preds.append(response)
                        
                        if verbose:
                            print(f"Response from server: {response}")
                            print(f"Time per frame for {len(self.preds)} frames: {(time.time() - start_time) / len(self.preds):.3f} seconds")
                            print()

                await asyncio.gather(send_frames(), receive_responses())
        except Exception as e:
            print(f"An error occurred: {e}")

        return self.preds
    
    def real_time_pred(self, cam_id: int = 0, calib: Union[scipy.interpolate._rbfinterp.RBFInterpolator, str, bytes] = None, verbose: bool = False, show_frame: bool = False):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.predict_from_websocket(cam_id, calib, verbose, show_frame))
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            loop.close()
        
        return self.preds