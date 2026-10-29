import streamlit as st
st.title('나의 첫 웹페이지 만들기!')
a=st.text_input('이름을 입력해 주세요')
b=st.selectbox('좋아하는 음식을 선택해 주세요',['케이크','타르트','소세지빵'])
if st.button('인삿말 생성'):
  st.write('반갑습니다!')
  st.info(a+'님 안녕하세요!')
  st.warning(b+'를 좋아하시나봐요!')
  st.error('잘 부탁드립니다!')
  st.balloons()
