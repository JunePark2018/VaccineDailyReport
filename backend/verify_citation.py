import requests
import json

url = "http://localhost:8000/generated-news/citation"
payload = {
    "cluster_id": 81,
    "target_sentence": "도널드 트럼프 미국 대통령이 26일(현지시간) 한국산 제품에 대한 관세를 15%에서 25%로 인상하겠다고 발표했다.",
}

try:
    print(f"Sending POST request to {url}...")
    response = requests.post(url, json=payload)
    response.raise_for_status()

    data = response.json()
    print("Response Status Code:", response.status_code)
    print("Response Data:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"Error: {e}")
    if "response" in locals():
        print(response.text)
