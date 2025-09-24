from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SonjuAI:
    def __init__(self):
        self.system_prompt = """
        당신은 70대 어르신을 도와주는 친근한 AI 손주입니다.
        - 존댓말 사용
        - 쉬운 말로 설명
        - 천천히 단계별로
        - 격려 많이 하기
        """
        
    def chat(self, user_message):
        """대화 기능"""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200
            )
            return {
                "success": True,
                "message": response.choices[0].message.content,
                "tokens": response.usage.total_tokens
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_quiz(self, topic):
        """퀴즈 생성"""
        prompt = f"{topic}에 대한 쉬운 퀴즈를 만들어주세요."
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"오류: {e}"

# 테스트
if __name__ == "__main__":
    ai = SonjuAI()
    
    print("=== 대화 테스트 ===")
    result = ai.chat("안녕하세요")
    print(result["message"] if result["success"] else result["error"])
    
    print("\n=== 퀴즈 테스트 ===")
    quiz = ai.generate_quiz("카카오톡")
    print(quiz)