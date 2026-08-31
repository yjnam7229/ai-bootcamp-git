
import streamlit as st

st.title('카페 매출 대시보드')

## 지표 카드 만들기
# 기본 지표
st.metric('오늘 매출', '450,000')

# 변화량과 함께 표시
st.metric(
    label="일일 방문객",
    value="127명", 
    delta="+23명"
)

# 음수 변화량 (빨간색으로 표시됨)
st.metric(
    label="재고 수량",
    value="85개",
    delta="-15개"
)

# 정보 메시지(파란색)
st.info('시스템 점검이 예정되어 있습니다')

# 성공 메시지(초록색)
st.success('데이터 백업이 완료되었습니다!')

# 경고 메시지 (노란색)  
st.warning('일부 기능이 제한될 수 있습니다')

# 오류 메시지 (빨간색)
st.error('서버 연결에 실패했습니다')

# 로딩 표시하기
import time

with st.spinner('학생 데이터를 처리하는 중...'):
    # 실제로는 데이터를 불러오는 코드가 들어감
    time.sleep(3)  # 3초 대기

st.success('처리완료!')

# 빈 공간 만들기
placeholder = st.empty()

# 나중에 내용 채우기
import time
time.sleep(2)
placeholder.text('검색 결과가 나타났습니다!')

# 내용 교체하기
time.sleep(2)
placeholder.success('검색이 완료되었습니다!')

