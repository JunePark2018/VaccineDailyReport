import requests
import json

# 선생님의 API 키
API_KEY = "AIzaSyCo3no8H1b2h1olKA_AdUHxr0m25KFgu9Q"

def check_available_models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ 확인된 모델 개수: {len(models)}개")
            print("="*40)
            
            # 사용 가능한 모델 이름만 쫙 뽑아서 보여줍니다.
            for m in models:
                # 'generateContent' 기능을 지원하는 모델만 필터링
                if "generateContent" in m.get('supportedGenerationMethods', []):
                    # "models/gemini-pro" -> "gemini-pro" 로 앞부분 잘라서 출력
                    clean_name = m['name'].replace("models/", "")
                    print(f"사용 가능 👉 {clean_name}")
            
        else:
            print(f"❌ 에러 발생: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"실행 중 에러: {str(e)}")

if __name__ == "__main__":
    check_available_models()