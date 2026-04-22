import requests

def test_website_scraping():
    url = "http://localhost:8000/process-link"
    # Use a URL that might fail with newspaper or is simple enough to test fallback
    # Example: A generic tech blog or the one user mentioned if accessible
    payload = {"url": "https://www.freecodecamp.org/news/learn-react-js/"}
    
    try:
        print(f"Testing fallback scraping for: {payload['url']}")
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(f"Source Type: {data.get('sourceType')}")
            print(f"Text Length: {len(data.get('text', ''))}")
            # print(f"Preview: {data.get('text', '')[:200]}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            try:
                print(f"Detail: {response.json()}")
            except:
                print(f"Text: {response.text}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_website_scraping()
