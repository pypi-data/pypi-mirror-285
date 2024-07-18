import os
import platform

class WebServiceConfig:
    
    """
    Configuration for connecting to the web service.

    Attributes:
        access_key (str): The access key for authentication.
        secret_key (str): The secret key for authentication.
        base_url (str): The base URL of the web service.
        timeout (int): The timeout for requests in seconds.
        ignore_ssl (bool): Whether to ignore SSL verification.
    """        
    def __init__(self, access_key: str, secret_key: str, base_url: str, timeout: int = 30, ignore_ssl: bool = False):
        """
        Initialize the WebServiceConfig.

        :param access_key: The access key for authentication.
        :param secret_key: The secret key for authentication.
        :param base_url: The base URL of the web service.
        :param timeout: The timeout for requests in seconds (default is 30).
        :param ignore_ssl: Whether to ignore SSL verification (default is False).
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.timeout = timeout
        self.ignore_ssl = ignore_ssl

class LogConfig:

    def __init__(self, ws_config: WebServiceConfig, device_name: str, agent_type: str, agent_version: str, agent_index: int, process_id: int):
        self.ws_config = ws_config
        self.device_name = device_name
        self.agent_type = agent_type
        self.agent_version = agent_version
        self.agent_index = agent_index
        self.process_id = process_id
        

def is_windows() -> bool:
    return platform.system() == 'Windows'


def get_config_folder_path(app_name: str, base_folder_path: str = '') -> str:

    if is_windows():
        username = os.getlogin()
        config_dir = os.path.join('C:\\Users', username, 'AppData', 'Roaming', app_name, "config")
        # If a virtual environment is used, the path will be in something like:
        # C:\Users\Username\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\Roaming

    else:
        if base_folder_path:
            config_dir = os.path.join(base_folder_path, ".config", app_name)
        else:
            config_dir = os.path.expanduser(os.path.join("~", ".config", app_name))

    # Create the directory if it doesn't exist
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    return config_dir


def get_appdata_folder_path(app_name: str, base_folder_path: str = '') -> str:

    if is_windows():
        username = os.getlogin()
        appdata_folder_path = os.path.join('C:\\Users', username, 'AppData', 'Roaming', app_name)
        # If a virtual environment is used, the path will be in something like:
        # C:\Users\Username\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\Roaming
    else:
        if base_folder_path:
            appdata_folder_path = os.path.join(base_folder_path, ".appdata", app_name)
        else:
            appdata_folder_path = os.path.expanduser(os.path.join("~", ".appdata", app_name))

    # Create the directory if it doesn't exist
    if not os.path.exists(appdata_folder_path):
        os.makedirs(appdata_folder_path)

    return appdata_folder_path


def get_config_value(config_folder_path: str, name: str, default_value: str = '') -> str | None:

    if not os.path.exists(config_folder_path):
        os.makedirs(config_folder_path)

    file_path = os.path.join(config_folder_path, name + '.txt')
    
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write(default_value)

    try:
        with open(file_path, 'r') as file:
            contents = file.read()
        return contents
    except FileNotFoundError:
        print(f"File '{name}' not found in the specified folder '{config_folder_path}'")
        return None
    except Exception as ex:
        print(f"Error occurred while reading '{name}': {ex}")
        return None


def set_config_value(config_folder_path: str, name: str, value: str) -> None:

    if not os.path.exists(config_folder_path):
        os.makedirs(config_folder_path)

    # Create the directory if it doesn't exist
    if not os.path.exists(config_folder_path):
        os.makedirs(config_folder_path)

    file_path = os.path.join(config_folder_path, name + '.txt')

    try:
        with open(file_path, 'w') as file:
            file.write(value)
        print(f"Successfully set the value in '{name}'")
    except Exception as ex:
        print(f"Error occurred while setting value in '{name}': {ex}")