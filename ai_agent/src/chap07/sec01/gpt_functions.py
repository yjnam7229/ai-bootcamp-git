from datetime import datetime
import pytz  # timezone package

def get_current_time(timezone:str='Asia/Seoul'):
    try:
        timezone = timezone.strip() # 좌우 여백 제거
        tz = pytz.timezone(timezone)  # 해당 지역의 시간 가져오기\
    except Exception:
        return f'잘못된 타임존입니다: {timezone}'

    now = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    # now = datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분 %S초')
    now_timezone = f'{now} {timezone}'

    print(now_timezone)
    return now_timezone

# 펑션 콜링 적용하기
## GPT에게 함수와 그에 관한 설명을 제공하고 상황에 맞는 특정 함수를 호출하도록 할 수 있음
## 오픈AI에서는 펑션 콜링 기능에 사용할 수 있는 함수 담은 도구 목록을 딕셔너리 형태로 정의
### 도구 목록의 딕셔너리는 GPT 모델이 어떤 도구를 사용할 수 있는지 알려 주는 설명서 역할

tools = [
    {
        'type': 'function',
        'function': {
            'name': 'get_current_time',
            'description': '주어진 타임존(예: Asia/Seoul, Asia/Tokyo, America/New_York)의 현재 날짜와 시간을 반환합니다.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'timezone': {
                        'type': 'string',
                        'description': '현재 날짜와 시간을 반환할 타임존을 입력하세요. (예: Asia/Seoul)',
                    }
                },
                'required': ['timezone']  # parameters 바로 아래 위치
            },
        }
    }
]

if __name__ == '__main__':  # 프로그램의 시작 포인트
    get_current_time('America/New_York')
    # get_current_time('Asia/Seoul')
