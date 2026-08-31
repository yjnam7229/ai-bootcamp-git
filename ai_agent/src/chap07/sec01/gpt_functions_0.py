from datetime import datetime

def get_current_time():
    now = datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분 %S초')
    # now = datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')

    print(now)
    return now

# 펑션 콜링 적용하기
## GPT에게 함수와 그에 관한 설명을 제공하고 상황에 맞는 특정 함수를 호출하도록 할 수 있음
## 오픈AI에서는 펑션 콜링 기능에 사용할 수 있는 함수 담은 도구 목록을 딕셔너리 형태로 정의
### 도구 목록의 딕셔너리는 GPT 모델이 어떤 도구를 사용할 수 있는지 알려 주는 설명서 역할

tools = [
    {
        'type': 'function',
        'function': {
            'name': 'get_current_time',
            'descrption': '현재 날짜와 시간을 반환합니다.'
        }
    },
]


if __name__ == '__main__':  # 프로그램의 시작 포인트
    get_current_time()