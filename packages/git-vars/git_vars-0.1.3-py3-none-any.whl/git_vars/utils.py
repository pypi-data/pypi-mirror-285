from urllib.parse import urlparse
from typing import Dict, Any, List
import configparser


def handle_error(err: Exception) -> None:
    """
    Handles errors by logging them to the console.

    Args:
    err (Exception): The error to handle
    """
    print(err)
    if isinstance(err, Exception):
        print(f"[Error] {str(err)}")
    else:
        raise err


def get_hostname(url: str) -> str:
    """
    Extracts the protocol and hostname from a URL.

    Args:
    url (str): The URL to parse

    Returns:
    str: The protocol and hostname combined
    """
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def format_env_vars(env_vars: List[Dict[str, Any]]) -> str:
    return "\n".join([f"{var['key']}={var['value']}" for var in env_vars])


def write_output_to_file(path: str, data: str) -> None:
    """
    Writes data to a file.

    Args:
    path (str): The path to the file
    data (str): The data to write
    """
    with open(path, "w") as f:
        d = format_env_vars(data)
        f.write(d)


def parse_data_from_env(filepath: str) -> Dict[str, Any]:
    """
    Parses environment variables from a file.

    Args:
    filepath (str): The path to the .env file

    Returns:
    Dict[str, Any]: A dictionary of environment variables
    """
    config = configparser.ConfigParser()
    config.optionxform = str  # This preserves case sensitivity

    # Create a temporary file with a section header
    with open(filepath, "r") as original_file:
        content = "[env]\n" + original_file.read()
    config.read_string(content)

    return dict(config["env"])


# No need for exports in Python, these functions can be imported directly
