import streamlit as st

def configure_page():
    st.set_page_config(
        page_title="HKDSE Math Dashboard", layout="wide"
    )
    st.title("🎓 Math Tuition Dashboard for Anna")

def authenticate():
    # 1) Initialize
    if "role" not in st.session_state:
        st.session_state.role = None

    # 2) If already logged in, just return it
    if st.session_state.role is not None:
        return st.session_state.role

    # 3) Show login UI
    pw = st.text_input("🔒 Enter password", type="password")

    if pw:
        if pw == st.secrets["math_tutor"]["tutor_pw"]:
            st.session_state.role = "Tutor"
            st.success("Access granted (Tutor)!")
            st.rerun()
        elif pw == st.secrets["math_tutor"]["tutee_pw"]:
            st.session_state.role = "Tutee"
            st.success("Access granted (Anna)!")
            st.rerun()
        else:
            st.error("Incorrect password.") #st.sidebar.error?

    # 4) If we reach here, we’re not yet authenticated—stop the script
    st.stop()