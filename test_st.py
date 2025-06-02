import streamlit as st
from streamlit.runtime.scriptrunner import RerunException, RerunData

def safe_rerun():
    raise RerunException(RerunData(widget_states=None))

st.write("Hello!")

if st.button("Rerun"):
    safe_rerun()
