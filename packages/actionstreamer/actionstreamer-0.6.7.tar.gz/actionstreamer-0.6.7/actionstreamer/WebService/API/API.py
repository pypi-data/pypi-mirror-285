import datetime
import json
from json import JSONEncoder

import actionstreamer.CommonFunctions
from actionstreamer.Config import WebServiceConfig

class PatchOperation:

    def __init__(self, field_name: str, value):
        self.fieldName = field_name
        self.value = value
        
class WebServiceResult:

    def __init__(self, code: int, description: str, http_response_code: int, http_response_string: str, json_data: str):
        self.code = code
        self.description = description
        self.http_response_code = http_response_code
        self.http_response_string = http_response_string
        self.json_data = json_data

class DateTimeEncoder(JSONEncoder):

    # Override the default method
    def default(self, obj) -> str | None:
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


def register_agent(ws_config: WebServiceConfig, device_name: str, agent_type: str, agent_version: str, agent_index: int, process_id: int) -> tuple[int, str]:

    try:        
        jsonPostData = {"deviceName":device_name, "agentType":agent_type, "agentVersion":agent_version, "agentIndex":agent_index, "processID":process_id}

        method = "POST"
        path = 'v1/agent'
        url = ws_config.base_url + path
        headers = {"Content-Type": "application/json"}
        parameters = ''
        body = json.dumps(jsonPostData)
        
        response_code, response_string = actionstreamer.CommonFunctions.send_signed_request(ws_config, method, url, path, headers, parameters, body)

    except Exception as ex:
        
        filename, line_number = actionstreamer.CommonFunctions.get_exception_info()
        if filename is not None and line_number is not None:
            print(f"Exception occurred at line {line_number} in {filename}")
        print(ex)

        response_code = -1
        response_string = "Exception in RegisterAgent"

    return response_code, response_string