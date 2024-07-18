import os
from enum import Enum
from datetime import datetime, timezone
from json.decoder import JSONDecodeError
from langfuse.api.core.api_error import ApiError
from pycookiecheat import firefox_cookies, chrome_cookies


def get_client_custom_params(**kwargs):
    proxy = os.environ.get("LANGFUSE_PROXY", "http://localhost:65230")
    return {
        "timeout": kwargs.get("timeout", TIME_OUT),
        "proxies": kwargs.get("proxies", {"https://": proxy, "http://": proxy}),
    }


def handle_jsonerror(response):
    try:
        response_json = response.json()
    except JSONDecodeError:
        raise ApiError(status_code=response.status_code, body=response.text)
    return response_json


def custom_json_encoder(obj):
    """
    Custom JSON encoder function to handle special types like datetime and enums.

    Args:
        obj: The object to be encoded.

    Returns:
        JSON serializable representation of the object.
    """
    if isinstance(obj, datetime):
        return obj.astimezone(timezone.utc).isoformat()
    elif isinstance(obj, Enum):
        return obj.value
    else:
        raise TypeError(f"Object of type '{type(obj)}' is not JSON serializable")


def datetime_to_str(dt):
    """
    Converts a datetime object to a string in the format 'dd/mm/yyyy'.

    Args:
        dt (datetime): The datetime object to be converted.

    Returns:
        str: The string representation of the datetime object.
    """
    return dt.strftime("%d/%m/%Y")


def compare_date(str_date1, str_date2):
    """
    Compares two dates in the format 'dd/mm/yyyy'.

    Args:
        str_date1 (str): The first date.
        str_date2 (str): The second date.

    Returns:
        int: The difference in days between the two dates. If the second date is before the first date, returns -1.
    """
    date1 = datetime.strptime(str_date1, "%d/%m/%Y")
    date2 = datetime.strptime(str_date2, "%d/%m/%Y")
    if date2 < date1:
        return -1
    return (date2 - date1).days


def get_browser_exist():
    """
    Checks type of browser exist in system.

    Returns:
        str: The type of browser exist in system.
    """
    if os.path.exists(os.path.expanduser("~/.mozilla/firefox")):
        return "firefox"
    elif os.path.exists(os.path.expanduser("~/.config/google-chrome")):
        return "chrome"
    else:
        return None


def get_cookies(url):
    """
    Gets cookies from the browser.

    Args:
        url (str): The URL of the website.

    Returns:
        dict: The cookies.
    """
    browser = get_browser_exist()
    if browser == "firefox":
        return firefox_cookies(url)
    elif browser == "chrome":
        return chrome_cookies(url)
    else:
        return None


SDK_NAME = "python"
THREADS = os.getenv("LANGFUSE_THREADS", 10)
TIME_OUT = os.getenv("LANGFUSE_TIMEOUT", 10)
MAX_RETRIES = os.getenv("LANGFUSE_MAX_RETRIES", 3)
FLUSH_AT = os.getenv("LANGFUSE_FLUSH_AT", 150)
FLUSH_INTERVAL = os.getenv("LANGFUSE_FLUSH_INTERVAL", 0.5)
PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY")
SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY")
BASE_URL = os.environ.get("LANGFUSE_HOST")
COOKIE_AUTH = os.environ.get("COOKIE_AUTH")
