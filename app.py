import streamlit as st
import yaml
from modules import paper_system, aesthetics, docs_display

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Authentication
def authenticate():
    st.sidebar.title("Login")
    password = st.sidebar.text_input("Enter password:", type="password")
    if password == config['tutor_password']:
        return 'tutor'
    elif password == config['tutee_password']:
        return 'tutee'
    else:
        st.sidebar.error("Invalid password")
        return None


def main():
    role = authenticate()
    if not role:
        return

    st.title("HKDSE Math Student Dashboard")
    # Display weekly motivational quote
    aesthetics.show_weekly_quote()

    # Tabs for core functions
    tab1, tab2, tab3 = st.tabs(["Exercises & Upload", "Progress Tracker", "Official Docs"])

    with tab1:
        paper_system.render(role=role, config=config)

    with tab2:
        aesthetics.render_progress(config=config)

    with tab3:
        docs_display.render(config=config)

if __name__ == "__main__":
    main()