from openai import OpenAI
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키 확인
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"✅ API 키 로드 성공: {api_key[:20]}...")
else:
    print("❌ API 키를 찾을 수 없습니다.")
    exit()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)

# 연결 테스트
try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",   # gpt-4o, gpt-4.1-mini 등으로 교체 가능
        messages=[{"role": "user", "content": "안녕하세요"}],
        max_tokens=50
    )
    
    print("✅ OpenAI 연결 성공!")
    print("응답:", response.choices[0].message.content)
    print(f"토큰 사용: {response.usage.total_tokens}")

except Exception as e:
    print(f"❌ 에러: {e}")
