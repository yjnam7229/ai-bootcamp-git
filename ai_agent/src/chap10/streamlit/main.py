# main.py

import streamlit as st
import numpy as np
import pandas as pd

# st.title('Streamlit x LangChain')
st.header('랭체인 기본 문법')
st.subheader('Text element')

st.write('Hellow, World!')
st.markdown('Hellow, **World!!**')
# st.markdown('## Hellow, **World!!**')
# st.markdown('### Hellow, **World!!**')

chart_data = pd.DataFrame(
    np.random.randn(5, 3),  # randn(): randnormal 5행 * 3열,
    columns=['a', 'b', 'c']
)

# st.write(chart_data)
st.line_chart(chart_data)
st.area_chart(chart_data)
st.bar_chart(chart_data)

col1, col2, col3 = st.columns([1, 1, 1], vertical_alignment='bottom')   # 브라우저 화면을 균등하게 3등분 (1:1:1), vertical_alignment='bottom' 수직정렬 하단정렬 :

with col1: # col1의 UI상의 영역을 확보(컨테이너)
    st.header('A.cat')
    st.image('https://static.streamlit.io/examples/cat.jpg')
with col2:
    st.header('A.dog')    
    st.image('https://static.streamlit.io/examples/dog.jpg')
with col3:
    st.header('An owl')    
    st.image('https://static.streamlit.io/examples/owl.jpg')
