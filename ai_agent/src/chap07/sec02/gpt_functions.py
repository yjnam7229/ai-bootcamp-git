from datetime import datetime
import pytz
import yfinance as yf

# 주어진 타임존(예: Asia/Seoul, Asia/Tokyo, America/New_York)의 현재 날짜와 시간을 반환
def get_current_time(timezone: str = 'Asia/Seoul'):
    try:
        timezone = timezone.strip()  # 공백 제거
        tz = pytz.timezone(timezone)
    except Exception:
        return f"잘못된 타임존입니다: {timezone}"

    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    now_timezone = f"{now} {timezone}"
    #print(now_timezone)
    return now_timezone

# 주어진 티커(예: AAPL)의 현재 가격, 시가총액 등 핵심 Yahoo Finance 정보를 반환합니다
def get_yf_stock_info(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info # 딕셔너리 형태로 반환
        print(info)
        return str(info) # GPT에게 전달하기 위해 문자열로 변환. 토큰의 크기가 클 수 있어 주의
        # return str({
        #     "symbol": info.get("symbol"),
        #     "shortName": info.get("shortName"),
        #     "currentPrice": info.get("currentPrice"),
        #     "marketCap": info.get("marketCap"),
        # })
    except Exception as e:
        return f"주식 정보를 가져오는 중 오류 발생: {str(e)}"

# 해당 종목의 Yahoo Finance 주가 정보를 반환합니다
def get_yf_stock_history(ticker: str, period: str):
    try:
        ticker = ticker.upper()
        stock = yf.Ticker(ticker)
        history = stock.history(period=period)

        if history.empty:
            return "데이터가 없습니다."

        history = history.tail(10) # 길면 모델 응답 깨질 수 있어 줄임
        history_md = history.to_markdown() # 데이터프레임을 마크다운 형식으로 변환
        print(history_md)
        return history_md

    except Exception as e:
        return f"주가 데이터를 가져오는 중 오류 발생: {str(e)}"

# 해당 종목의 Yahoo Finance 추천 정보를 반환합니다
def get_yf_stock_recommendations(ticker: str):
    stock = yf.Ticker(ticker)
    recommendations = stock.recommendations
    recommendations_md = recommendations.to_markdown() # 데이터프레임을 마크다운 형식으로 변환
    print(recommendations_md)
    return recommendations_md


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "주어진 타임존(예: Asia/Seoul, Asia/Tokyo, America/New_York)의 현재 날짜와 시간을 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    'timezone': {
                        'type': 'string',
                        'description': '현재 날짜와 시간을 반환할 타임존을 입력하세요. (예: Asia/Seoul)',
                    },
                },
                "required": ['timezone'],
            },        
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_yf_stock_info",
            "description": "주어진 티커(예: AAPL)의 현재 가격, 시가총액 등 핵심 Yahoo Finance 정보를 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    'ticker': {
                        'type': 'string',
                        'description': 'Yahoo Finance 정보를 반환할 종목의 티커를 입력하세요. (예: AAPL)',
                    },
                },
                "required": ['ticker'],  # 필수 매개변수(속성)
            },        
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_yf_stock_history",
            "description": "해당 종목의 Yahoo Finance 주가 정보를 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    'ticker': {
                        'type': 'string',
                        'description': 'Yahoo Finance 주가 정보를 반환할 종목의 티커를 입력하세요. (예: AAPL)',
                    },
                    'period': {
                        'type': 'string',
                        'description': '주가 정보를 조회할 기간을 입력하세요. (예: 1d, 5d, 1mo, 1y, 5y)',
                    },
                },
                "required": ['ticker', 'period'],
            },        
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_yf_stock_recommendations",
            "description": "해당 종목의 Yahoo Finance 추천 정보를 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    'ticker': {
                        'type': 'string',
                        'description': 'Yahoo Finance 추천 정보를 반환할 종목의 티커를 입력하세요. (예: AAPL)',
                    },
                },
                "required": ['ticker'],
            },        
        }
    },
]


if __name__ == '__main__':
    # get_current_time('America/New_York')
    get_yf_stock_info('AAPL')  

    # get_yf_stock_history('AAPL', '5d')
    # print('----')
    # get_yf_stock_recommendations('AAPL')
  