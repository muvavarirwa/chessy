import requests

def getCycle():
    request = 'http://127.0.0.1:8000/policy/cycle'
    response = requests.get(request)
    return int(response.json())
