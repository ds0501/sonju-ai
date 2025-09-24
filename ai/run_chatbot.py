from ai_service import SonjuAI

def main():
    ai = SonjuAI()
    print("손주톡톡 AI 챗봇")
    print("종료하려면 'quit' 입력\n")
    
    while True:
        user_input = input("어르신: ")
        
        if user_input.lower() == 'quit':
            print("안녕히 계세요!")
            break
            
        response = ai.chat(user_input)
        
        if response["success"]:
            print(f"AI 손주: {response['message']}\n")
        else:
            print(f"오류: {response['error']}\n")

if __name__ == "__main__":
    main()