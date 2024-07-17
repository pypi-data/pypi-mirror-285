import json

from actionstreamer import CommonFunctions
from actionstreamer.Config import WebServiceConfig
from actionstreamer.WebService.Patch import *
from actionstreamer.Model import VideoClip

def create_video_clip(ws_config: WebServiceConfig, device_name: str, video_clip: VideoClip) -> tuple[int, str]:

    try:
        method = "POST"
        path = 'v1/videoclip/' + device_name
        url = ws_config.base_url + path
        headers = {"Content-Type": "application/json"}
        parameters = ''
        body = json.dumps(video_clip.__dict__)

        response_code, response_string = CommonFunctions.send_signed_request(ws_config, method, url, path, headers, parameters, body)

    except Exception as ex:
        
        filename, line_number = CommonFunctions.get_exception_info()
        if filename is not None and line_number is not None:
            print(f"Exception occurred at line {line_number} in {filename}")
        print(ex)

        response_code = -1
        response_string = "Exception in CreateVideoClip. Line number " + str(line_number)

    return response_code, response_string


def update_file_id(ws_config: WebServiceConfig, video_clip_id: int, file_id: int) -> tuple[int, str]:

    try:
        operations_list = []
        add_patch_operation(operations_list, "FileID", file_id)

        method = "PATCH"
        path = 'v1/videoclip/' + str(video_clip_id)
        url = ws_config.base_url + path
        headers = {"Content-Type": "application/json"}
        parameters = ''
        body = generate_patch_json(operations_list)

        response_code, response_string = CommonFunctions.send_signed_request(ws_config, method, url, path, headers, parameters, body)

    except Exception as ex:
        
        filename, line_number = CommonFunctions.get_exception_info()
        if filename is not None and line_number is not None:
            print(f"Exception occurred at line {line_number} in {filename}")
        print(ex)

        response_code = -1
        response_string = "Exception in UpdateVideoClipFileID Line number " + str(line_number)

    return response_code, response_string

def get_video_clip_by_id(ws_config: WebServiceConfig, video_clip_id: int) -> tuple[int, str]:

    try:

        method = "GET"
        path = 'v1/videoclip/' + str(video_clip_id)
        url = ws_config.base_url + path
        headers = {"Content-Type": "application/json"}
        parameters = ''

        response_code, response_string = CommonFunctions.send_signed_request(ws_config, method, url, path, headers, parameters)

    except Exception as ex:
        
        filename, line_number = CommonFunctions.get_exception_info()
        if filename is not None and line_number is not None:
            print(f"Exception occurred at line {line_number} in {filename}")
        print(ex)

        response_code = -1
        response_string = "Exception in get_video_clip_by_id Line number " + str(line_number)

    return response_code, response_string