import requests

try:
    url = "http://127.0.0.1:8000/process-link"
    payload = {"url": "https://www.youtube.com/watch?v=y1px8hBl7zg"}
    headers = {"Content-Type": "application/json"}
    
    print(f"Sending request to {url}...")
    response = requests.post(url, json=payload)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Success!")
        print(f"Title in data: {data.get('data', {}).get('basic', {}).get('summary', '')[:50]}...")
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Request failed: {e}")
