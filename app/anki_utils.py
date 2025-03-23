import base64
import os
import requests
from constants import (
    ANKI_CONNECT_URL    
)

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    payload = request(action, **params)
    response = requests.post(ANKI_CONNECT_URL, json=payload)
    
    if not response.ok:
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")
    
    response_json = response.json()
    
    if 'error' not in response_json or 'result' not in response_json:
        raise Exception('Invalid response structure')
    if response_json['error'] is not None:
        raise Exception(response_json['error'])
    
    return response_json['result']

def store_audio_file(filename):
    abs_path = os.path.abspath(filename)  # Get absolute path of the file
    with open(abs_path, "rb") as f:
        audio_data = base64.b64encode(f.read()).decode("utf-8")  # Encode to Base64 and decode to a string
    
    print(abs_path)
    
    response = invoke("storeMediaFile", filename=filename, path=abs_path)
    print(f"Stored {filename}: {response}")  # Print Anki Connect response