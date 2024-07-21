import requests

url = "https://google.com"
timeout = 5
def chk_net():
    try:
        response = requests.get(url , timeout=timeout)
        return True
    except (requests.ConnectionError,requests.Timeout):
        return False

