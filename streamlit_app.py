import streamlit as st
from streamlit.components.v1 import iframe

st.set_page_config(page_title="Embedded Flask App")
st.title("Embedded Flask App")

st.write("This streamlit app embeds your Flask app using an iframe.")
flask_url = st.text_input("Flask URL", value="http://localhost:5000")

st.info("Make sure your Flask app is running before embedding. Example: `python app.py`")

st.markdown("---")

width = st.slider("Iframe width", min_value=400, max_value=1400, value=1000)
height = st.slider("Iframe height", min_value=300, max_value=1600, value=800)

try:
    iframe(flask_url, width=width, height=height)
except Exception as e:
    st.error(f"Could not load iframe: {e}")

st.markdown("---")
st.write("If the embedded page is blank, check that Flask is listening on the provided URL and that there are no CSP or X-Frame-Options headers blocking embedding.")