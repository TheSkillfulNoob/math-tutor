import streamlit as st
import os

def render(config):
    st.header("Official Documents")
    docs = os.listdir(config['docs_folder'])
    for pdf in docs:
        if pdf.lower().endswith('.pdf'):
            st.markdown(f"- [{pdf}](file://{config['docs_folder']}/{pdf})")