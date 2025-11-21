"""
Creativity Rating App - Streamlit Version

Main application file with navigation and session state management.
"""
import streamlit as st

import os
import sys

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.user import User
from utils.config_loader import load_config

# Page configuration
st.set_page_config(
    page_title="Creativity Rating App",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide sidebar navigation button
st.markdown(
    """
    <style>
        [data-testid="collapsedControl"] {
            display: none;
        }
        section[data-testid="stSidebar"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
def init_session_state():
    """Initialize session state variables if not already set."""
    if 'user' not in st.session_state:
        st.session_state.user = User()

    if 'page' not in st.session_state:
        st.session_state.page = 'welcome'

    if 'config' not in st.session_state:
        try:
            st.session_state.config = load_config()
        except Exception as e:
            st.error(f"Failed to load configuration: {e}")
            st.session_state.config = None

    if 'user_id_confirmed' not in st.session_state:
        st.session_state.user_id_confirmed = False

# Navigation function
def navigate_to(page_name):
    """Navigate to a specific page."""
    st.session_state.page = page_name
    st.rerun()

# Initialize
init_session_state()

# Display current page based on session state
current_page = st.session_state.page

if current_page == 'welcome':
    import pages.welcome as welcome
    welcome.show()

elif current_page == 'login':
    import pages.login as login
    login.show()

elif current_page == 'questionnaire':
    import pages.questionnaire as questionnaire
    questionnaire.show()

elif current_page == 'pre_familiarization':
    import pages.pre_familiarization as pre_familiarization
    pre_familiarization.show()

elif current_page == 'familiarization':
    import pages.familiarization as familiarization
    familiarization.show()

elif current_page == 'post_familiarization':
    import pages.post_familiarization as post_familiarization
    post_familiarization.show()

elif current_page == 'videoplayer':
    import pages.videoplayer as videoplayer
    videoplayer.show()

else:
    st.error(f"Unknown page: {current_page}")
    st.button("Go to Welcome", on_click=lambda: navigate_to('welcome'))
