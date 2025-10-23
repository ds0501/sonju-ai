import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI 설정
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # 모델 설정
    DEFAULT_MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 600
    TEMPERATURE_CHAT = 0.7
    TEMPERATURE_QUIZ = 0.8
    
    # 대화 설정
    MAX_CONVERSATION_HISTORY = 5
    
    # API 설정
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    
    @classmethod
    def validate(cls):
        """설정 검증"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다.")

config = Config()