import json

from actionstreamer import CommonFunctions
from actionstreamer.WebService.API import WebServiceResult
from actionstreamer.Config import WebServiceConfig


def create_health(ws_config: WebServiceConfig, device_name: str, health_json: str) -> WebServiceResult:
    
    ws_result = WebServiceResult(0, '', '', '', None)

    try:
        method = "POST"
        path = 'v1/devicehealth'
        url = ws_config.base_url + path
        headers = {"Content-Type": "application/json"}
        parameters = ''

        json_post_data = {
            "deviceName": device_name,
            "healthJSON": health_json
        }

        body = json.dumps(json_post_data)
        
        response_code, response_string = CommonFunctions.send_signed_request(ws_config, method, url, path, headers, parameters, body)
        
        ws_result.http_response_code = response_code
        ws_result.http_response_string = response_string
        ws_result.json_data = json.loads(response_string)

    except Exception as ex:
        ws_result.code = -1
        filename, line_number = CommonFunctions.get_exception_info()
        if filename is not None and line_number is not None:
            print(f"Exception occurred at line {line_number} in {filename}")
        print(ex)

    return ws_result


def update_health(ws_config: WebServiceConfig, device_name: str, health_json: str) -> WebServiceResult:

    ws_result = WebServiceResult(0, '', '', '', None)

    try:
        method = "POST"
        path = 'v1/devicehealth/updatelatest'
        url = ws_config.base_url + path
        headers = {"Content-Type": "application/json"}
        parameters = ''

        json_post_data = {
            "deviceName": device_name,
            "healthJSON": health_json
        }

        body = json.dumps(json_post_data)
        
        response_code, response_string = CommonFunctions.send_signed_request(ws_config, method, url, path, headers, parameters, body)
        
        ws_result.http_response_code = response_code
        ws_result.http_response_string = response_string
        ws_result.json_data = json.loads(response_string)

    except Exception as ex:
        ws_result.code = -1
        filename, line_number = CommonFunctions.get_exception_info()
        if filename is not None and line_number is not None:
            print(f"Exception occurred at line {line_number} in {filename}")
        print(ex)

    return ws_result