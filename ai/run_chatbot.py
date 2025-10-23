import logging
import re

# 개발 시: logging.INFO, 배포 시: logging.CRITICAL
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger('httpx').setLevel(logging.CRITICAL)
logging.getLogger('ai_service').setLevel(logging.CRITICAL)

from ai_service import SonjuAI

def detect_intent(message: str) -> dict:
    """사용자 의도 파악"""
    # 퀴즈 요청 감지
    quiz_keywords = ['퀴즈', '문제', '테스트', '시험', '내줘', '내주']
    if any(keyword in message for keyword in quiz_keywords):
        topics = ['토스', '카카오톡', '전화', '문자', '사진']
        for topic in topics:
            if topic in message:
                return {'type': 'quiz', 'topic': topic}
        return {'type': 'quiz', 'topic': '토스'}
    
    # 가이드 요청 감지
    guide_keywords = ['알려줘', '알려주세요', '알려주', '가르쳐', '방법', '어떻게', '어케', '가이드']
    
    if any(keyword in message for keyword in guide_keywords):
        # 구체적인 기능 가이드
        if '송금' in message or '돈 보내' in message or '보내는' in message:
            return {'type': 'guide', 'topic': '송금'}
        
        if '계좌' in message:
            return {'type': 'guide', 'topic': '계좌'}
        
        if '전화' in message:
            return {'type': 'guide', 'topic': '전화'}
        
        if '문자' in message:
            return {'type': 'guide', 'topic': '문자'}
        
        if '사진' in message:
            return {'type': 'guide', 'topic': '사진'}
        
        # 앱별 기본 가이드
        if '토스' in message:
            return {'type': 'guide', 'topic': 'app_토스'}
        
        if '카카오톡' in message or '카톡' in message:
            return {'type': 'guide', 'topic': 'app_카카오톡'}
    
    return {'type': 'chat'}

def main():
    ai = SonjuAI()
    current_quiz = None
    conversation_history = []
    max_history = 10
    
    print("=" * 50)
    print("손주톡톡 AI 챗봇")
    print("어르신의 스마트폰 사용을 도와드려요!")
    print("=" * 50)
    print("\n사용 예시:")
    print("  - 토스 퀴즈 내줘")
    print("  - 송금하는 방법 알려줘")
    print("  - 카카오톡 어떻게 써?")
    print("  - 종료하려면 '그만' 또는 '종료'")
    print("=" * 50 + "\n")
    
    while True:
        user_input = input("어르신: ").strip()
        
        if user_input.lower() in ['quit', 'q', '종료', '그만', '끝', '나갈래', '안녕']:
            print("\n손주톡톡: 할머니/할아버지, 오늘도 수고 많으셨어요!")
            print("언제든 불러주세요!\n")
            break
        
        if not user_input:
            continue
        
        # 퀴즈 진행 중
        if current_quiz is not None:
            answer = re.sub(r'[^0-9]', '', user_input).strip()
            
            if answer.isdigit() and 1 <= int(answer) <= 4:
                user_answer = int(answer)
                result = ai.check_quiz_answer(current_quiz, user_answer)
                
                print(f"\n손주톡톡: {result['message']}")
                print(f"{result['explanation']}\n")
                
                current_quiz = None
                continue
            elif answer:
                print("\n1, 2, 3, 4 중 하나를 선택해주세요!\n")
            else:
                print("\n숫자로 답변해주세요. 1, 2, 3, 4 중 하나를 선택해주세요!\n")
            continue
        
        # 의도 파악
        intent = detect_intent(user_input)
        
        # 가이드 요청
        if intent['type'] == 'guide':
            topic = intent['topic']
            
            # 앱 가이드 처리
            if topic.startswith('app_'):
                app_name = topic.replace('app_', '')
                print(f"\n{app_name}의 기본 사용법을 알려드릴게요...\n")
                
                # 앱별 기본 사용법 요청
                guide_prompt = f"{app_name} 앱의 기본 사용법을 어르신이 이해하기 쉽게 단계별로 설명해주세요."
                response = ai.chat(guide_prompt, conversation_history=conversation_history)
            else:
                # 기존 기능별 가이드
                print(f"\n{topic} 가이드를 준비하고 있어요...\n")
                
                topic_map = {
                    '송금': '토스_송금',
                    '계좌': '토스_계좌조회',
                    '전화': '전화걸기',
                    '문자': '문자보내기',
                    '사진': '사진찍기'
                }
                
                guide_topic = topic_map.get(topic, topic)
                response = ai.get_topic_guide(guide_topic)
            
            if response["success"]:
                print(f"\n손주톡톡: {response['message']}\n")
                conversation_history.append({"role": "user", "content": user_input})
                conversation_history.append({"role": "assistant", "content": response['message']})
                
                if len(conversation_history) > max_history * 2:
                    conversation_history = conversation_history[-max_history * 2:]
            else:
                print("\n지금은 답변을 드리기 어려워요. 다시 시도해주세요.\n")
            continue
        
        # 퀴즈 요청
        if intent['type'] == 'quiz':
            topic = intent['topic']
            result = ai.generate_quiz(topic)
            
            if result["success"]:
                quiz = result["quiz"]
                current_quiz = quiz
                
                print(f"\n손주톡톡: {quiz['question']}\n")
                for option in quiz['options']:
                    print(f"   {option}")
                print("\n1~4 중 하나를 선택해주세요!\n")
            else:
                print("\n퀴즈를 만드는 중 문제가 발생했어요. 다시 시도해주세요.\n")
            continue
        
        # 일반 대화
        response = ai.chat(user_input, conversation_history=conversation_history)
        
        if response["success"]:
            print(f"\n손주톡톡: {response['message']}\n")
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response['message']})
            
            if len(conversation_history) > max_history * 2:
                conversation_history = conversation_history[-max_history * 2:]
        else:
            print("\n지금은 답변을 드리기 어려워요. 다시 시도해주세요.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n안녕히 계세요!")
    except Exception as e:
        print("\n프로그램에 문제가 생겼어요. 다시 시작해주세요.\n")