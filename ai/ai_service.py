from openai import OpenAI
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional

from config import config

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SonjuAI:
    def __init__(self):
        """OpenAI 클라이언트 초기화"""
        config.validate()
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.system_prompt = """
        당신은 "손주톡톡"이라는 70대 어르신 전담 AI 손주입니다.

        **성격과 역할:**
        - 밝고 친근하며 인내심이 많은 손주
        - 어르신을 "할머니" 또는 "할아버지"라고 부름
        - 스마트폰 사용법을 차근차근 알려드림
        - 항상 격려와 칭찬을 아끼지 않음

        **말투 규칙:**
        - 존댓말 사용하되 친근하게
        - 어려운 용어 대신 쉬운 말 사용 (예: "클릭" → "눌러주세요")
        - 한 번에 하나씩만 설명

        **응답 방식:**
        - 여러 단계로 나누어 설명 (1단계, 2단계...)
        - 설명 마지막에 격려 멘트 한 번만 포함
        - 각 단계마다 격려를 반복하지 말 것
        - 절대로 마크다운 포맷을 사용하지 말 것 (**, *, #, - 등 금지)
        - 모든 텍스트는 평문으로만 작성
        """

    def chat(
        self, 
        message: str, 
        conversation_history: List[Dict] = None
    ) -> Dict:
        """
        일반 채팅 기능
        
        Args:
            message: 사용자 메시지
            conversation_history: 이전 대화 [{"role": "user/assistant", "content": "내용"}]
            
        Returns:
            {"success": bool, "message": str, "tokens_used": int, "timestamp": str}
        """
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # 최근 대화 히스토리 추가
            if conversation_history:
                messages.extend(conversation_history[-config.MAX_CONVERSATION_HISTORY:])
            
            messages.append({"role": "user", "content": message})
            
            response = self.client.chat.completions.create(
                model=config.DEFAULT_MODEL,
                messages=messages,
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE_CHAT
            )
            
            result = {
                "success": True,
                "message": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Chat successful - Tokens: {result['tokens_used']}")
            return result
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def generate_quiz(self, topic: str, difficulty: str = "쉬움") -> Dict:
        """퀴즈 생성"""
        prompt = f"""
        {topic}에 대한 {difficulty} 난이도의 어르신용 퀴즈를 만들어주세요.
        
        **반드시 다음 JSON 형식으로만 응답하고, 다른 설명은 붙이지 마세요:**
        {{
            "question": "질문 내용",
            "options": ["1. 선택지1", "2. 선택지2", "3. 선택지3", "4. 선택지4"],
            "correct_answer": 1,
            "explanation": "정답 해설",
            "encouragement": "칭찬 멘트"
        }}
        """
        
        tokens_used = None
        
        try:
            response = self.client.chat.completions.create(
                model=config.DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=config.TEMPERATURE_QUIZ
            )
            
            tokens_used = response.usage.total_tokens
            quiz_text = response.choices[0].message.content.strip()
            
            # JSON 추출
            if "```json" in quiz_text:
                quiz_text = quiz_text.split("```json")[1].split("```")[0]
            elif "```" in quiz_text:
                quiz_text = quiz_text.split("```")[1].split("```")[0]
            
            if "{" in quiz_text and "}" in quiz_text:
                start = quiz_text.find("{")
                end = quiz_text.rfind("}") + 1
                quiz_text = quiz_text[start:end]
            
            quiz_data = json.loads(quiz_text)
            
            # 필수 필드 검증
            required_fields = ["question", "options", "correct_answer", "explanation", "encouragement"]
            missing_fields = [f for f in required_fields if f not in quiz_data]
            if missing_fields:
                raise KeyError(f"필수 필드 누락: {', '.join(missing_fields)}")
            
            # options 검증
            if not isinstance(quiz_data["options"], list):
                raise ValueError("options는 리스트가 아닙니다.")
            
            if len(quiz_data["options"]) != 4:
                raise ValueError(f"options가 {len(quiz_data['options'])}개입니다. (4개 필요)")
            
            # correct_answer 타입 및 범위 검증
            correct_answer = quiz_data["correct_answer"]
            if isinstance(correct_answer, str) and correct_answer.isdigit():
                correct_answer = int(correct_answer)
                quiz_data["correct_answer"] = correct_answer
            
            if not isinstance(correct_answer, int) or not (1 <= correct_answer <= 4):
                raise ValueError(f"correct_answer가 '{correct_answer}'입니다. (1~4 필요)")
            
            # 옵션 포맷 검증 (경고만)
            for i, option in enumerate(quiz_data["options"], 1):
                if not re.match(rf"^{i}\.\s+.+", option):
                    logger.warning(f"옵션 포맷 경고: '{option}'이 '{i}. ...' 형식이 아닙니다.")
            
            result = {
                "success": True,
                "quiz": quiz_data,
                "tokens_used": tokens_used,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Quiz generated - Topic: {topic}, Tokens: {tokens_used}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}, tokens: {tokens_used}")
            return {
                "success": False,
                "error": "퀴즈를 만드는 중 문제가 발생했어요. 다시 시도해주세요.",
                "tokens_used": tokens_used,
                "timestamp": datetime.now().isoformat()
            }
        
        except (KeyError, ValueError) as e:
            logger.error(f"퀴즈 검증 실패: {e}, tokens: {tokens_used}")
            return {
                "success": False,
                "error": "퀴즈를 만드는 중 문제가 발생했어요. 다시 시도해주세요.",
                "tokens_used": tokens_used,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}, tokens: {tokens_used}")
            return {
                "success": False,
                "error": "퀴즈를 만드는 중 문제가 발생했어요. 다시 시도해주세요.",
                "tokens_used": tokens_used,
                "timestamp": datetime.now().isoformat()
            }

    def check_quiz_answer(self, quiz_data: Dict, user_answer: int) -> Dict:
        """
        퀴즈 정답 체크
        
        Args:
            quiz_data: 퀴즈 데이터
            user_answer: 사용자 답변 (1-4)
            
        Returns:
            {"correct": bool, "message": str, "explanation": str, "correct_answer": int}
        """
        try:
            correct_answer = quiz_data["correct_answer"]
            
            if user_answer == correct_answer:
                return {
                    "correct": True,
                    "message": quiz_data.get("encouragement", "정답입니다! 잘하셨어요!"),
                    "explanation": quiz_data.get("explanation", ""),
                    "correct_answer": correct_answer
                }
            else:
                return {
                    "correct": False,
                    "message": f"아쉬워요! 정답은 {correct_answer}번이에요. 다시 한번 도전해보세요!",
                    "explanation": quiz_data.get("explanation", ""),
                    "correct_answer": correct_answer
                }
                
        except Exception as e:
            logger.error(f"Quiz check error: {e}")
            return {
                "correct": False,
                "message": "답안 확인 중 오류가 발생했어요.",
                "explanation": "",
                "error": str(e)
            }

    def generate_analysis(self, learning_data: Dict) -> Dict:
        """
        학습 분석 텍스트 생성
        
        Args:
            learning_data: {
                "lesson": str,
                "avg_time": float,
                "accuracy": float,
                "errors": List[str]
            }
            
        Returns:
            {"success": bool, "summary_text": str, "tokens_used": int}
        """
        lesson = learning_data.get("lesson", "학습")
        avg_time = learning_data.get("avg_time", 0)
        accuracy = learning_data.get("accuracy", 0)
        errors = learning_data.get("errors", [])
        
        prompt = f"""
        어르신의 {lesson} 학습 결과를 분석해주세요.
        
        **데이터:**
        - 평균 소요 시간: {avg_time}초
        - 정확도: {accuracy * 100}%
        - 자주 틀린 부분: {', '.join(errors) if errors else '없음'}
        
        **요구사항:**
        - 친근하고 격려하는 톤으로
        - 3-4문장으로 간단히 요약
        - 잘한 부분은 칭찬, 어려워한 부분은 부드럽게 피드백
        - "할머니" 또는 "할아버지"라고 부르기
        """
        
        try:
            response = self.client.chat.completions.create(
                model=config.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            result = {
                "success": True,
                "summary_text": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Analysis generated - Tokens: {result['tokens_used']}")
            return result
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_topic_guide(self, topic: str) -> Dict:
        """주제별 가이드"""
        topic_prompts = {
            "토스_송금": "토스 앱에서 송금하는 방법을 단계별로 쉽게 설명해주세요.",
            "토스_계좌조회": "토스 앱에서 계좌 잔액을 확인하는 방법을 알려주세요.",
            "전화걸기": "전화걸기에 대해 단계별로 친절하게 설명해주세요.",
            "문자보내기": "문자메시지 보내는 방법을 어르신이 이해하기 쉽게 설명해주세요.",
        }
        
        guide_message = topic_prompts.get(
            topic, 
            f"{topic}에 대해 어르신이 이해하기 쉽게 단계별로 설명해주세요."
        )
        
        return self.chat(guide_message)