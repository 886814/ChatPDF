import streamlit as st
from streamlit_chat import message
from test_embedding import Chatbot
from PyPDF2 import PdfReader
import logging as logger
import pandas as pd
import re
import time

chatbot = Chatbot()

st.header("데모 테스트")
st.markdown("[Saltlux](https://www.saltlux.com/)")

logger.info('uploading pdf')
st.sidebar.markdown("## Upload a PDF")
pdf_uploader = st.sidebar.file_uploader("Upload a PDF",accept_multiple_files=False, type="pdf", )

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if pdf_uploader is not None:

    pdf = PdfReader(pdf_uploader)
    pdf_title = re.findall('(?<=\')(.*?)(?=\')', str(pdf_uploader))[0]

    if 'embedding' not in st.session_state:
        st.session_state['embedding'] = dict()

    if pdf_title not in st.session_state['embedding'].keys():
        with st.spinner('잠시 기다려주세요!'):
            paper_text = chatbot.parse_paper(pdf)
            df = chatbot.paper_df(paper_text)
            df = chatbot.calculate_embeddings(df)
            time.sleep(1)
        st.success('Done!')
        st.session_state['embedding'][pdf_title] = df

    def clear_text():
        st.session_state["temp"] = st.session_state["text"]
        st.session_state["text"] = ""

    if "temp" not in st.session_state:
        st.session_state["temp"] = ""

    st.text_input(
        "You: ",
        label_visibility="visible",
        help="Please ask any questions about the paper.",key='text', on_change=clear_text
        )


    if st.session_state["temp"]:
        logger.info("create prompt")
        prompt = chatbot.create_prompt(st.session_state['embedding'][pdf_title], st.session_state["temp"])
        response = chatbot.response(st.session_state['embedding'][pdf_title], prompt)
        st.session_state.past.append(st.session_state["temp"])
        st.session_state.generated.append(response['answer'].strip())


    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))

else:
    st.markdown("<span style='color:black'>PDF 파일을 업로드 해주세요.</span>",
                unsafe_allow_html=True)