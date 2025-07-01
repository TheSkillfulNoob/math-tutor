import streamlit as st


def configure_page():
    st.set_page_config(
        page_title="HKDSE Math Dashboard", layout="wide"
    )
    st.title("🎓 Math Tutuition Dashboard for Anna")

def authenticate():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        pw = st.text_input("🔒 Enter password", type="password")
        if pw == st.secrets["math_tutor"]["tutor_pw"]:
            st.session_state.authenticated = True
            st.success("Access granted (Tutor)!")
            st.rerun()
            return "Tutor"
        elif pw == st.secrets["math_tutor"]["tutee_pw"]:
            st.session_state.authenticated = True
            st.success("Access granted (Student)!")
            st.rerun()
            return "Tutee"
        elif pw:
            st.sidebar.error("Incorrect password.")
        st.stop()
        return None