import json

import ActionStreamer.CommonFunctions
import ActionStreamer.WebService.API
from ActionStreamer.Config import WebServiceConfig

def create_file(ws_config: ActionStreamer.Config.WebServiceConfig, device_name: str, filename: str, file_size: int, sha256_hash: str) -> tuple[int, str, str, int]:

    """
    Create a file.
    
    Parameters:
    ws_config (Config.WebServiceConfig): The web service configuration.
    device_name (string): The device name.
    filename (string): The filename (no path information, just the name).
    file_size (int): The file size in bytes.
    sha256_hash (string): The SHA256 hash for the file.
    
    Returns:
    response_code: The API HTTP response code.
    response_string: The API HTTP response body
    signed_url: The URL to upload the file to.
    file_id: The ID for the newly generated file.
    """

    try:
        json_post_data = {"deviceName":device_name, "filename":filename, "fileSize":file_size, "sHA256Hash":sha256_hash}

        method = "POST"
        path = 'v1/file'
        url = ws_config.base_url + path
        headers = {"Content-Type": "application/json"}
        parameters = ''
        body = json.dumps(json_post_data)

        response_code, response_string =  ActionStreamer.CommonFunctions.send_signed_request(ws_config, method, url, path, headers, parameters, body)

        signed_url = ''
        file_id = 0
        
        if (response_code == 200):

            # This response should include signedURL, fileID
            response_data = json.loads(response_string)

            signed_url = response_data['signedURL']
            file_id = response_data['fileID']

    except Exception as ex:
        
        filename, line_number = ActionStreamer.CommonFunctions.get_exception_info()

        if filename is not None and line_number is not None:
            print(f"Exception occurred at line {line_number} in {filename}")
        print(ex)

        response_code = -1
        response_string = "Exception in create_file"
        signed_url = ""
        file_id = 0

    return response_code, response_string, signed_url, file_id


def update_file_upload_success(ws_config: WebServiceConfig, device_name: str, file_id: int) -> tuple[int, str]:

    try:
        json_post_data = {'deviceSerial':device_name}

        method = "POST"
        path = 'v1/file/success/' + str(file_id)
        url = ws_config.base_url + path
        headers = {"Content-Type": "application/json"}
        parameters = ''
        body = json.dumps(json_post_data)

        response_code, response_string = ActionStreamer.CommonFunctions.send_signed_request(ws_config, method, url, path, headers, parameters, body)

    except Exception as ex:
        
        filename, line_number = ActionStreamer.CommonFunctions.get_exception_info()
        if filename is not None and line_number is not None:
            print(f"Exception occurred at line {line_number} in {filename}")
        print(ex)

        response_code = -1
        response_string = "Exception in update_file_upload_success"

    return response_code, response_string

