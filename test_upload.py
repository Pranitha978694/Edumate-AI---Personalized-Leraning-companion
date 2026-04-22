import requests
import sys

filename = "minimal_test.pdf"
url = "http://localhost:8000/process"

try:
    with open(filename, 'rb') as f:
        files = {'file': (filename, f, 'application/pdf')}
        print(f"Uploading {filename} to {url}...")
        r = requests.post(url, files=files)
        
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        print("Success! Data preview:")
        print(r.json().get('text', '')[:100])
    else:
        print("Failed!")
        print(r.text)

except Exception as e:
    print(f"Error: {e}")
