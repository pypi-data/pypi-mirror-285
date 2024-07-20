import sys
import hashlib
import hmac
import uuid
import subprocess
import time
from datetime import datetime
import requests
import os
import re

import pytz
import requests

from actionstreamer.Config import WebServiceConfig

class StandardResult:

    def __init__(self, code: int, description: str):
        self.Code = code
        self.Description = description
        

class switch(object):

	def __init__(self, value):
		self.value = value
		self.fall = False

	def __iter__(self):
		"""Return the match method once, then stop"""
		yield self.match
		raise StopIteration
    
	def match(self, *args) -> bool:
		"""Indicate whether or not to enter a case suite"""
		if self.fall or not args:
			return True
		elif self.value in args:
			self.fall = True
			return True
		else:
			return False


def get_exception_info() -> tuple[str, int] | tuple[None, None]:
    exception_type, exception_object, exception_traceback = sys.exc_info()
    if exception_traceback is not None:
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        return filename, line_number
    return None, None


def get_line_number() -> int | None:
    exception_type, exception_object, exception_traceback = sys.exc_info()
    if exception_traceback is not None:
        return exception_traceback.tb_lineno
    return None


def log_to_console(message: str, agent_name='') -> None:
    # Get the current UTC time
    utc_now = datetime.now(pytz.utc)
    
    # Format the UTC time
    utc_time_formatted = utc_now.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Prepend the formatted UTC time to the string
    if (agent_name):
        result_string = f"[{utc_time_formatted}]: [{agent_name}]: {message}"
    else:
        result_string = f"[{utc_time_formatted}]: {message}"
    
    # Print the result to standard output
    print(result_string)


def send_signed_request(ws_config: WebServiceConfig, method: str, url: str, path: str, headers: dict = None, parameters: str = None, body: str = None) -> tuple[int, str]:
    
    try:
        if headers is None:
            headers = {"Content-Type": "application/json"}
        elif isinstance(headers, str):
            headers = dict(header.strip().split(':', 1) for header in headers.split('\n'))

        nonce = str(uuid.uuid4())
        timestamp = str(int(time.time()))

        headers['X-Nonce'] = nonce
        headers['X-Timestamp'] = timestamp
        headers['Authorization'] = 'HMAC-SHA256 ' + ws_config.access_key
        headers['X-AccessKey'] = ws_config.access_key

        # Generate HMAC signature
        signature, string_to_sign = get_hmac_signature(ws_config.secret_key, method, path, headers, parameters, body)

        # Include signature in headers
        headers['X-Signature'] = signature

        verify = not ws_config.ignore_ssl
        
        if method.upper() == 'POST':
            response = requests.post(url, headers=headers, data=body, verify=verify, timeout=ws_config.timeout)
        elif method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=parameters, verify=verify, timeout=ws_config.timeout)
        if method.upper() == 'PUT':
            response = requests.put(url, headers=headers, data=body, verify=verify, timeout=ws_config.timeout)
        elif method.upper() == 'PATCH':
            response = requests.patch(url, headers=headers, data=body, params=parameters, verify=verify, timeout=ws_config.timeout)
        elif method.upper() == 'DELETE': 
            response = requests.delete(url, headers=headers, params=parameters, verify=verify, timeout=ws_config.timeout)

        status_code = response.status_code
        response_string = response.content.decode('utf-8')

    except Exception as ex:
        filename, line_number = get_exception_info()
        if filename is not None and line_number is not None:
            print(f"Exception occurred at line {line_number} in {filename}")
        print(ex)
        status_code = -1
        response_string = "Error in send_signed_request"

    return status_code, response_string
   

def get_hmac_signature(secret_key: str, method: str, path: str, headers, parameters: dict, body: str = None)-> tuple[str, str] | None:
    
    try:
        if 'Content-Type' in headers:
            del headers['Content-Type']

        headerString = dictionary_to_string(headers)
        parameterString = dictionary_to_string(parameters)

        # Path should be in the format /v1/event
        if not path.startswith('/'):
            path = '/' + path

        if path.endswith('/') and len(path) > 1:
            path = path[:-1]

        string_to_sign = '\n'.join([method, path, headerString, parameterString, body if body else ''])

        string_to_sign = string_to_sign.strip()
        #log_to_console("stringToSign: " + string_to_sign)
        
        # Generate the HMAC SHA256 signature
        hmac_signature = hmac.new(secret_key.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha256)

        # Convert the HMAC signature to hexadecimal
        return hmac_signature.hexdigest(), string_to_sign

    except Exception as ex:
        filename, line_number = get_exception_info()
        if filename is not None and line_number is not None:
            print(f"Exception occurred at line {line_number} in {filename}")
        print(ex)


def dictionary_to_string(dictionary: dict) -> str:

    result = ''

    try:
        sorted_keys = sorted(dictionary.keys())
        
        for key in sorted_keys:
            result += f"{key}: {dictionary[key]}\n"
        
    except Exception as ex:
        filename, line_number = get_exception_info()
        #if filename is not None and line_number is not None:
            #print(f"Exception occurred at line {line_number} in {filename}")
        #print(ex)
    
    return result


def upload_file_to_s3(file_path: str, signed_url: str) -> int:

    retry = True
    retry_count = 0
    result = 0

    while retry:

        try:
            retry_count = retry_count + 1

            if retry_count > 5:
                retry = False
                result = -3
                print("Retry limit exceeded")

            with open(file_path, 'rb') as file:
                response = requests.put(signed_url, data=file)
            
            if response.status_code == 200:
                retry = False
                result = 0
            else:
                print(f"Error uploading file to S3. Status code: {response.status_code}")
                result = -1
            
        except Exception as ex:
            print("Exception occurred while uploading file to S3:", str(ex))
            result = -2
        
    return result


def download_file(file_path: str, url: str) -> int:

    retry = True
    result = 0
    retry_count = 0
    
    while retry:

        try:
            retry_count = retry_count + 1

            if retry_count > 5:
                retry = False
                result = -3
                print("Retry limit exceeded")

            with requests.get(url, stream=True) as response:
                response.raise_for_status()  # Check for any errors

                # Open a local file for writing in binary mode
                with open(file_path, 'wb') as file:
                    # Write the content to the local file in chunks
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
            
            retry = False

        except Exception as ex:
            print("Exception occurred while downloading file:", str(ex))
            result = -2
        
    return result


def get_sha256_hash_for_file(file_path: str) -> str:
    # Initialize the hash object (SHA-256 is used in this example)
    hash_object = hashlib.sha256()

    # Open the file in binary mode to read its contents
    with open(file_path, "rb") as file:
        # Read the file in chunks to avoid loading the entire file into memory
        for chunk in iter(lambda: file.read(4096), b""):
            hash_object.update(chunk)

    # Get the hexadecimal representation of the hash
    file_hash = hash_object.hexdigest()
    
    return file_hash


def create_folders(path: str) -> None:
    # Split the path into individual folders
    folders = path.split(os.sep)

    # Initialize the base folder to the root of the file system
    base_folder = ""

    # Loop through each folder in the path
    for folder in folders:
        # Append the current folder to the base folder
        base_folder = os.path.join(base_folder, folder)

        # Check if the current folder exists
        if not os.path.exists(base_folder):
            # If not, create the folder
            os.makedirs(base_folder)


def get_cpu_frequency() -> float:
    with open("/proc/cpuinfo") as f:
        cpuinfo = f.read()
    # Find the first occurrence of "cpu MHz"
    match = re.search(r"cpu MHz\s+:\s+(\d+\.\d+)", cpuinfo)
    if match:
        return float(match.group(1))
    else:
        raise RuntimeError("Unable to find CPU frequency in /proc/cpuinfo")


def get_clock_cycles_per_millisecond() -> float:

    frequency_mhz = get_cpu_frequency()
    frequency_hz = frequency_mhz * 1_000_000
    cycles_per_millisecond = frequency_hz / 1_000

    return cycles_per_millisecond


def concatenate_videos(input_file_path1: str, input_file_path2: str, output_file_path: str):

    # Generate a unique file name for the temporary file list
    temp_file_name = str(uuid.uuid4()) + '.txt'
    temp_file_path = os.path.join('/tmp', temp_file_name)

    with open(temp_file_path, 'w') as filelist:
        filelist.write(f"file '{input_file_path1}'\n")
        filelist.write(f"file '{input_file_path2}'\n")
    
    # Run the ffmpeg command to concatenate the videos
    try:
        subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', temp_file_path, '-c', 'copy', '-y', output_file_path], check=True)
    except subprocess.CalledProcessError as ex:
        print(f"Error occurred: {ex}")
    finally:
        # Clean up the temporary file
        try:
            os.remove(temp_file_path)
        except OSError as e:
            print(f"Error removing temporary file: {e}")


def get_video_length_in_seconds(file_path):

    """Get the length of a video in seconds."""
    result = subprocess.run(['ffmpeg', '-i', file_path], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    output = result.stderr

    # Find the duration in the output
    duration_match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', output)
    
    if not duration_match:
        raise ValueError(f"Could not determine the duration of the video {file_path}")

    hours, minutes, seconds = map(float, duration_match.groups())
    total_seconds = hours * 3600 + minutes * 60 + seconds
    total_seconds = total_seconds * 1000

    return total_seconds

