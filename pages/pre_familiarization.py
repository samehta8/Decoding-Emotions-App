"""
Pre-familiarization instructions page.
Displays introductory text before the familiarization trials begin.
"""
import streamlit as st
from utils.styling import apply_compact_layout

def show():
    """Display the pre-familiarization instructions screen."""
    # Apply compact layout
    apply_compact_layout()

    st.markdown("""
    ### Welcome to the Emotion Recognition Survey!
    
    #### Please read the following instructions carefully!

    You will be shown a series of images and videos of athletes, each for 2 seconds, after which you have to answer 2 simple questions:
    """)

    st.info("""
    1. What emotions are being shown by the athlete you just saw? You have to select the **appropriate emotions** from the given options:

            Angry, Happy, Sad, Scared, Surprised, Disgusted, Contempt/Hate/Disdain, and Neutral.
""")
    
    st.info("""
    2. Did the athlete **win or lose** the match/contest?
""")

    st.markdown("""        
    For each clip in the survey, please indicate whether the athlete won or lost, and rate the emotions you observe. You can pick multiple emotions (as many as you need). Each emotion is rated independently on a 0 to 100 scale. Each of these emotions has to be rated separately.

    Neutral emotion is used when you do not see any specific emotions at all. It is used when the other mentioned emotions are absent. 

    Thus, Neutral would be 0 if other emotions are present, and 100 if no other emotions are visible or present according to you. 

    Now, if you have understood these instructions, we will have 3 practice clips, followed by a message, after which your survey will begin. Please press start below, to begin your practice trial.
    """)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("◀️ Back to Questionnaire", use_container_width=True):
            if st.session_state.get('confirm_back_pre_famil', False):
                st.session_state.page = 'questionnaire'
                st.session_state.user_id_confirmed = False
                st.rerun()
            else:
                st.session_state.confirm_back_pre_famil = True
                st.warning("⚠️ Click again to confirm.")

    with col3:
        if st.button("Begin Practice Trials ▶️", use_container_width=True, type="primary"):
            st.session_state.page = 'familiarization'
            st.session_state.confirm_back_pre_famil = False
            st.rerun()
