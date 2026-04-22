from youtubesearchpython import VideosSearch
try:
    videos_search = VideosSearch('react tutorial', limit=3)
    results = videos_search.result()
    print(results)
except Exception as e:
    print(f"Test Failed: {e}")
