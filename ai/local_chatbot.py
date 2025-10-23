#기본 테스트 챗봇입니다 손주톡톡 기능과 상관 x

from openai import OpenAI, APIConnectionError, AuthenticationError, RateLimitError
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini" #gpt-3.5-turbo

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)


def get_system_prompt():
    """손주톡톡 AI의 기본 시스템 프롬프트"""
    return """
    당신은 70대 어르신의 하루를 함께하는 손주 AI입니다.
    밝고 다정한 말투로 대화하고, 항상 존댓말을 사용해주세요.
    어르신이 스마트폰 사용에 어려움을 겪으시면 친절하게 도와드리세요.
    """


def run_chatbot():
    """간단한 콘솔 챗봇"""
    print("=" * 50)
    print("손주톡톡 간단 챗봇 (종료: 'exit' 또는 '종료')")
    print("=" * 50 + "\n")

    # 대화 히스토리
    messages = [{"role": "system", "content": get_system_prompt()}]

    while True:
        user_input = input("할머니: ").strip()
        if user_input.lower() in ["exit", "종료", "끝", "quit"]:
            print("\n손주: 다음에 또 이야기해요, 할머니.\n")
            break

        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            # OpenAI API 호출
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            reply = response.choices[0].message.content
            print(f"\n손주: {reply}\n")

            # 대화 히스토리 저장
            messages.append({"role": "assistant", "content": reply})

            # 최근 대화 10개까지만 유지
            if len(messages) > 21:
                messages = [messages[0]] + messages[-20:]

        except AuthenticationError:
            print("\n오류: OpenAI API 키가 올바르지 않습니다. .env 파일을 확인하세요.\n")
            break
        except RateLimitError:
            print("\n오류: 사용량 제한에 도달했습니다. 잠시 후 다시 시도하세요.\n")
            break
        except APIConnectionError:
            print("\n오류: 네트워크 연결 문제입니다. 인터넷 상태를 확인하세요.\n")
            break
        except Exception as e:
            print(f"\n예기치 못한 오류 발생: {e}\n")
            break


if __name__ == "__main__":
    run_chatbot()
