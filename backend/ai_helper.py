import os
import json
import requests
import torch
from openai import OpenAI
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from huggingface_hub import login

# =================================================================
# 1. API 키 설정
# =================================================================
OPENAI_API_KEY = "".strip()
GOOGLE_API_KEY = "AIzaSyDmxmulDLDDO3x3k6pw9-xZ93qnTvJsv48".strip()
HF_TOKEN       = "".strip()

if HF_TOKEN: login(token=HF_TOKEN)

# =================================================================
# 2. 클라이언트 설정
# =================================================================
openai_client = None
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

gemini_session = None
if GOOGLE_API_KEY:
    gemini_session = requests.Session()
    gemini_session.headers.update({"Content-Type": "application/json"})

loaded_hf_pipelines = {}

# =================================================================
# 3. 만능 질문 함수 (모든 모델 '기자 모드' 적용)
# =================================================================
def ask(model_name, message):
    answer = ""
    model_name = model_name.strip()

    try:
        # ---------------------------------------------------------
        # CASE A: GPT 모델 (OpenAI)
        # ---------------------------------------------------------
        if "gpt" in model_name.lower():
            if not openai_client: return "⚠️ OpenAI 키 없음"
            
            response = openai_client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": message}],
                
                # [GPT 최적화 설정]
                temperature=0.2,       # 냉정하게 (팩트 위주)
                max_tokens=4000,       # 길이 넉넉히
                top_p=0.9,
                frequency_penalty=0.5  # 반복 방지 (GPT는 이게 중요)
            )
            answer = response.choices[0].message.content

        # ---------------------------------------------------------
        # CASE B: Gemini 모델 (Google)
        # ---------------------------------------------------------
        elif "gemini" in model_name.lower():
            if not gemini_session: return "⚠️ Google 키 없음"
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GOOGLE_API_KEY}"
            
            payload = {
                "contents": [{"parts": [{"text": message}]}],
                
                # 1. 생성 설정 (말더듬 방지)
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 4000,
                    "topP": 0.8,
                    "topK": 40
                },
                
                # 2. 안전 설정 (끊김 방지 - Gemini 전용)
                # 금융/주식 뉴스 작성 시 '위험'으로 오인하여 멈추는 것을 방지
                "safetySettings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
            }
            
            response = gemini_session.post(url, data=json.dumps(payload))
            if response.status_code == 200:
                answer = response.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                return f"⚠️ 구글 에러 ({response.status_code}): {response.text}"

        # ---------------------------------------------------------
        # CASE C: 로컬 모델 (Hugging Face)
        # ---------------------------------------------------------
        else:
            if model_name not in loaded_hf_pipelines:
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(
                    model_name, torch_dtype=torch.float16, device_map="auto"
                )
                loaded_hf_pipelines[model_name] = pipeline(
                    "text-generation", model=model, tokenizer=tokenizer, device_map="auto"
                )
            
            pipe = loaded_hf_pipelines[model_name]
            prompt = pipe.tokenizer.apply_chat_template([{"role": "user", "content": message}], tokenize=False, add_generation_prompt=True)
            
            # [로컬 모델 최적화 설정]
            outputs = pipe(
                prompt, 
                max_new_tokens=4000,     # 길이 넉넉히
                do_sample=True, 
                temperature=0.2,         # 냉정하게
                top_p=0.9,
                top_k=40,
                repetition_penalty=1.2   # [중요] 앵무새 방지 (로컬 모델 필수)
            )
            answer = outputs[0]["generated_text"][len(prompt):].strip()

    except Exception as e:
        return f"⚠️ 에러 발생: {str(e)}"

    return answer