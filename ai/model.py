from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

# ========== 채팅 관련 ==========
class ChatRequest(BaseModel):
    message: str = Field(..., description="사용자 메시지")
    user_id: str = Field(..., description="사용자 ID")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None, 
        description="대화 히스토리 [{'role': 'user/assistant', 'content': '내용'}]"
    )

class ChatResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    tokens_used: Optional[int] = None
    error: Optional[str] = None
    timestamp: str

# ========== 퀴즈 관련 ==========
class QuizGenerateRequest(BaseModel):
    topic: str = Field(..., description="퀴즈 주제 (예: 토스_송금)")
    difficulty: str = Field(default="쉬움", description="난이도")
    user_id: str = Field(..., description="사용자 ID")

class QuizData(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    encouragement: str

class QuizGenerateResponse(BaseModel):
    success: bool
    quiz: Optional[QuizData] = None
    tokens_used: Optional[int] = None
    error: Optional[str] = None
    timestamp: str

class QuizCheckRequest(BaseModel):
    quiz_data: Dict = Field(..., description="퀴즈 데이터 (generate_quiz 응답의 quiz)")
    user_answer: int = Field(..., ge=1, le=4, description="사용자 답변 (1-4)")
    user_id: str = Field(..., description="사용자 ID")

class QuizCheckResponse(BaseModel):
    correct: bool
    message: str
    explanation: str
    correct_answer: int

# ========== 분석 관련 ==========
class AnalysisRequest(BaseModel):
    user_id: str = Field(..., description="사용자 ID")
    learning_data: Dict = Field(..., description="학습 데이터 (시간, 정확성 등)")
    # 예시: {"lesson": "토스_송금", "avg_time": 15.5, "accuracy": 0.8, "errors": ["버튼3"]}

class AnalysisResponse(BaseModel):
    success: bool
    summary_text: Optional[str] = None
    tokens_used: Optional[int] = None
    error: Optional[str] = None
    timestamp: str

# ========== 주제별 가이드 ==========
class GuideRequest(BaseModel):
    topic: str = Field(..., description="가이드 주제")
    user_id: str = Field(..., description="사용자 ID")