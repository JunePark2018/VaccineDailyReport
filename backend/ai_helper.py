import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from openai import OpenAI
import google.generativeai as genai
from huggingface_hub import login

# =================================================================
# 1. API 키 설정 구간
# 사용하려는 모델의 API 키를 따옴표("") 안에 넣어주세요.
# =================================================================
OPENAI_API_KEY = "sk-..."
GOOGLE_API_KEY = "AIza..."
HF_TOKEN       = "hf..."

# 토큰이 있을 때만 로그인 시도 (Llama-3 같은 모델용)
if HF_TOKEN: login(token=HF_TOKEN)

# [Gemini] 전역 설정 (로그인)
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# [OpenAI] 클라이언트 미리 생성
# 키가 있으면 클라이언트를 만들고, 없으면 None으로 둡니다.
openai_client = None
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

# =================================================================
# 2. 모델 캐시 저장소
# 설명: Hugging Face 모델은 용량이 커서 매번 새로 불러오면 시간이 오래 걸립니다.
#      한 번 불러온 모델은 여기에 저장해두고 계속 재사용하기 위함입니다.
# =================================================================
loaded_hf_pipelines = {}

def ask(model_name, message):
    """
    [함수 설명]
    사용자가 '모델 이름'과 '하고 싶은 말'을 넣으면,
    알아서 적절한 AI를 찾아가 답변을 받아오고 화면에 출력해주는 함수입니다.
    
    사용 예시: ask("gpt-4o", "안녕?")
    """
    
    # 답변을 저장할 변수 초기화
    answer = ""
    
    try:
        # ---------------------------------------------------------
        # CASE A: 모델 이름에 'gpt'가 들어가는 경우 (OpenAI 사용)
        # ---------------------------------------------------------
        if "gpt" in model_name.lower():
            # API 키가 제대로 있는지 먼저 확인합니다.
            if not OPENAI_API_KEY or "sk-" not in OPENAI_API_KEY:
                print("[오류] OpenAI API 키가 설정되지 않았습니다.")
                return # 함수를 여기서 강제로 종료합니다.

            # 질문을 보내고 답변을 받아옵니다.
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": message}], # 사용자의 메시지
                temperature=0.7 # 창의성 조절 (0.7은 무난한 수치)
            )
            # 받아온 결과에서 텍스트 부분만 뽑아냅니다.
            answer = response.choices[0].message.content

        # ---------------------------------------------------------
        # CASE B: 모델 이름에 'gemini'가 들어가는 경우 (Google 사용)
        # ---------------------------------------------------------
        elif "gemini" in model_name.lower():
            # 구글 API 키 확인
            if not GOOGLE_API_KEY or "AIza" not in GOOGLE_API_KEY:
                print("[오류] Google API 키가 설정되지 않았습니다.")
                return
            
            # 해당 모델을 불러옵니다.
            model = genai.GenerativeModel(model_name)
            
            # 질문을 던지고 답변을 생성합니다.
            response = model.generate_content(message)
            
            # 결과 텍스트를 추출합니다.
            answer = response.text

        # ---------------------------------------------------------
        # CASE C: 그 외 나머지 (Hugging Face 로컬 모델 사용)
        # ---------------------------------------------------------
        else:
            # 1. 모델이 이미 로드되어 있는지 확인합니다. (없으면 새로 로드)
            if model_name not in loaded_hf_pipelines:
                print(f"'{model_name}' 모델을 준비 중입니다...")
                
                # 토크나이저(글자를 숫자로 바꾸는 도구) 로드
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                
                # 모델 본체 로드 (GPU가 있으면 자동으로 GPU를 씁니다)
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16, # 메모리를 아끼기 위해 16비트 사용
                    device_map="auto"          # 알아서 그래픽카드(GPU) 할당
                )
                
                # 텍스트 생성 파이프라인 만들기
                pipe = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    device_map="auto"
                )
                
                # 다 만든 파이프라인을 저장소(캐시)에 저장해둡니다. (다음엔 바로 쓰려고)
                loaded_hf_pipelines[model_name] = pipe
            
            # 2. 저장소에서 파이프라인을 꺼내옵니다.
            pipe = loaded_hf_pipelines[model_name]
            
            # 3. 채팅 템플릿 적용 (모델이 알아듣는 대화 형식으로 변환)
            messages = [{"role": "user", "content": message}]
            prompt = pipe.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )

            # 4. 실제 생성 작업 수행
            outputs = pipe(
                prompt,
                max_new_tokens=512, # 최대 답변 길이
                do_sample=True,     # 확률적으로 단어 선택 (더 자연스러움)
                temperature=0.7,    # 창의성
                top_p=0.9           # 답변 품질 조절
            )
            
            # 5. 질문(프롬프트)은 빼고, 답변 부분만 잘라냅니다.
            generated_text = outputs[0]["generated_text"]
            answer = generated_text[len(prompt):].strip()

    except Exception as e:
        # 뭔가 에러가 나면 붉은색 경고와 함께 에러 내용을 보여줍니다.
        print(f"에러가 발생했습니다: {str(e)}")
        return

    # =============================================================
    # 최종 결과 출력 (여기가 원하시는 '답변만 출력' 부분입니다)
    # =============================================================
    print(answer)


# =================================================================
# 3. 실행 예시 (여기서 함수를 사용하세요)
# =================================================================
if __name__ == "__main__":
    ask("gpt-4o", "대한민국의 수도는 어디야?")