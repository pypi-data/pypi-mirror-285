import requests
import numpy as np
import base64
import torch

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

class Client:
    def __init__(self, calib_info=None):
        self.base_url = "http://VytalGazeAPILB-884689726.us-east-1.elb.amazonaws.com/"
        self.calib_info = calib_info
        self.calib_info_bytes = convert_dict_values_to_bytes(calib_info)
        self.carry = None

    def predict_from_video(self, video_path):    
        function_endpoint = "video/handle_video"

        with open(video_path, 'rb') as f:

            response = requests.post(
                f'{self.base_url}{function_endpoint}',
                files = {"file": f},
                timeout=1000,
            )
            
            try:
                result = {}
                for key, value in response.json().items():
                    result[key] = bytes_to_tensor(value)
            except:
                result = response

        return result

