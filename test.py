import datetime
from llm import get_retriever, get_ai_response, get_date_filter

def test_get_retriever():
    test_inputs = [
        "오늘 올라온 공지를 보여줘",
        "어제 공지가 뭐였는지 확인해줘",
        "이번 주 공지 알려줘",
        "최근에 올라온 정보 궁금해",
        "2024-11-21 공지 확인",
    ]

    for user_input in test_inputs:
        print(f"테스트 입력: {user_input}")
        
        # 날짜 필터가 제대로 적용되는지 확인
        date_filter = get_date_filter(user_input)
        print(f"적용된 날짜 필터: {date_filter}")
        
        # 검색 결과를 출력하지 않음
        
        print("-" * 50)

def test_get_ai_response():
    test_inputs = [
        "오늘 올라온 공지를 보여줘",
        "어제 공지가 뭐였는지 확인해줘",
        "이번 주 공지 알려줘",
        "최근에 올라온 정보 궁금해",
        "2024-11-21 공지 확인",
    ]

    for user_input in test_inputs:
        print(f"테스트 입력: {user_input}")
        
        ai_response_stream = get_ai_response(user_input)

        # AI 응답 출력 (번역이 필요하면 그에 맞게 변경)
        buffer = ""
        for chunk in ai_response_stream:
            buffer += chunk
            if len(buffer) > 100:
                print(f"AI 응답 (부분): {buffer}")
                buffer = ""
        if buffer:
            print(f"AI 응답 (마지막): {buffer}")
        
        print("-" * 50)

# 메인 함수로 테스트 실행
if __name__ == "__main__":
    print("=== get_retriever 테스트 ===")
    test_get_retriever()
    
    print("=== get_ai_response 테스트 ===")
    test_get_ai_response()
