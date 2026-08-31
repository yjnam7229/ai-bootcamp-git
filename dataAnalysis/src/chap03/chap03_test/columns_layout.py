
import streamlit as st

st.title('학생 정보 관리 시스템')

# 4개의 열로 나누기
col1, col2, col3, col4 = st.columns(4)  # columns(4) 화면을 4개의 동일한 크기 열로 나눈다 

with col1:
    st.metric('전체 학생 수', '245명')

with col2:
    st.metric('평균 점수', '82.5점')

with col3:
    st.metric('출석률', '94.2%')

with col4:
    st.metric('과제 제출률', '87.8%')

# 첫 번째 열을 다른 열보다 2배 크게 만들기
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.write('메인 콘텐츠 영역 - 이 열이 가장 넓습니다')

with col2:
    st.write('통계 정보')

with col3:
    st.write('빠른 메뉴')

with st.container():
    st.subheader('이번 달 도서관 현황')    
    st.write('이 영역에는 도서관의 주요 통계가 표시됩니다')
    st.metric('대출 도서 수', '1,245권')
    st.metric('신규 회원', '+23명')

with st.expander('상세 통계 정보'):
    st.write("여기에는 자세한 분석 결과가 들어갑니다")
    st.write("평소에는 숨겨져 있다가 필요할 때만 펼쳐볼 수 있습니다")
