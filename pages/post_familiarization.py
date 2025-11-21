"""
Post-familiarization instructions page.
Displays instructions for the final rating procedure.
"""
import streamlit as st
from utils.styling import apply_compact_layout

def show():
    """Display the post-familiarization instructions screen."""
    # Apply compact layout
    apply_compact_layout()

    st.success("""
    ### Great job!

    You have now completed the familiarisation trials. You should now be well-versed with the type of stimulus and expected responses.
    """
)
    st.markdown("---")

    st.markdown("""
                
        You will now begin the survey. Please pay maximum attention as possible throughout the trial, and try to be as accurate as possible in your selection of the emotions and result estimates. 
                
        Remember, you can pick as many emotions are you like for each of the clips you are about to see, but you cannot keep all emotions at 0 - if that is the case, Neutral must be greater than 0. 
                
        Good luck and have fun! 
    """)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("◀️ Back to Questionnaire", use_container_width=True):
            if st.session_state.get('confirm_back_post_famil', False):
                st.session_state.page = 'questionnaire'
                st.session_state.user_id_confirmed = False
                st.rerun()
            else:
                st.session_state.confirm_back_post_famil = True
                st.warning("⚠️ Click again to confirm.")

    with col3:
        if st.button("Begin Main Rating Task ▶️", use_container_width=True, type="primary"):
            st.session_state.page = 'videoplayer'
            st.session_state.confirm_back_post_famil = False
            st.rerun()
