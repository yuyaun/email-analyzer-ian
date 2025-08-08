import requests
import time

URL = "http://localhost:8000/email-analyzer/api/public/v1/generate"
AUTH = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyU24iOiJzdHJpbmciLCJleHAiOjE3NTQ1MzkzNTZ9.OsvtL8_OVqJ1LjJzEc069wtXNAPfr0HwJcxPq8CGw1E"

HEADERS = {
    "accept": "application/json",
    "Authorization": AUTH,
    "Content-Type": "application/json"
}

DATA = {
    "campaignSn": "string",
    "magicType": "title_optimize",
    "content": "string"
}

for round_num in range(1, 11):
    print(f"\n▶ Round {round_num}")
    for i in range(1, 31):
        start_time = time.time()
        response = requests.post(URL, headers=HEADERS, json=DATA)
        duration = time.time() - start_time
        print(f"Request {i:02d}: Status {response.status_code}, Time {duration:.2f}s")
    time.sleep(1)  # 可選：每輪後休息 1 秒
