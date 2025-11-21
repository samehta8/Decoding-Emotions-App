"""
Questionnaire page - Collect demographic and experience information.
Dynamically builds form based on config/questionnaire_fields.yaml.
"""
import streamlit as st
from utils.config_loader import load_questionnaire_fields
from utils.data_persistence import save_user_data
from utils.styling import apply_compact_layout

def show():
    """Display the questionnaire screen."""
    # Apply compact layout to minimize scrolling
    apply_compact_layout()

    user = st.session_state.user
    config = st.session_state.config

    # Load questionnaire fields
    if 'questionnaire_fields' not in st.session_state:
        st.session_state.questionnaire_fields = load_questionnaire_fields(config)

    fields = st.session_state.questionnaire_fields

    # Check if user has confirmed their ID
    if st.session_state.get('user_id_confirmed', False):
        # Show confirmation panel
        show_confirmation_panel()
    else:
        # Show main questionnaire form
        show_questionnaire_form(fields)

def show_questionnaire_form(fields):
    """Display the main questionnaire form."""
    user = st.session_state.user

    st.title("📋 Questionnaire")
    st.markdown("Please provide the following information:")
    st.markdown("---")

    # Create form
    with st.form("questionnaire_form"):
        # Process fields and group related ones
        processed_groups = set()

        for field_config in fields:
            field_type = field_config.get('type', 'text')
            field_name = field_config.get('field_name', '')
            title = field_config.get('title', '')
            hint_text = field_config.get('hint_text', '')
            group = field_config.get('group', None)

            # Skip if already processed as part of a group
            if group and group in processed_groups:
                continue

            if field_type == 'multiple_choice':
                # Multiple choice field
                options = field_config.get('options', [])
                if title:
                    st.markdown(f"**{title}**")

                selected = st.radio(
                    label=title if not title else "Select one:",
                    options=options,
                    key=f"field_{field_name}",
                    horizontal=True,
                    label_visibility="collapsed" if title else "visible"
                )

                # Store value
                user.set_field_value(field_name, selected)

            elif field_type in ('text', 'numeric'):
                # Handle grouped fields (e.g., birthday)
                if group:
                    # Find all fields in this group
                    group_fields = [f for f in fields if f.get('group') == group]

                    # Get title from first field with a title
                    group_title = next((f.get('title') for f in group_fields if f.get('title')), '')

                    if group_title:
                        st.markdown(f"**{group_title}**")

                    # Create columns for group fields
                    cols = st.columns(len(group_fields))

                    for idx, gf in enumerate(group_fields):
                        gf_name = gf.get('field_name', '')
                        gf_hint = gf.get('hint_text', '')
                        gf_type = gf.get('type', 'text')
                        max_len = gf.get('max_length', None)

                        with cols[idx]:
                            if gf_type == 'numeric':
                                value = st.number_input(
                                    label=gf_hint,
                                    key=f"field_{gf_name}",
                                    min_value=0,
                                    step=1,
                                    value=None,
                                    label_visibility="collapsed",
                                    placeholder=gf_hint
                                )
                            else:
                                value = st.text_input(
                                    label=gf_hint,
                                    key=f"field_{gf_name}",
                                    max_chars=max_len,
                                    placeholder=gf_hint,
                                    label_visibility="collapsed"
                                )

                            # Store value
                            if value is not None:
                                user.set_field_value(gf_name, value)

                    processed_groups.add(group)

                else:
                    # Single field (not grouped)
                    max_len = field_config.get('max_length', None)

                    if field_type == 'numeric':
                        value = st.number_input(
                            label=hint_text,
                            key=f"field_{field_name}",
                            min_value=0,
                            step=1,
                            value=None,
                            placeholder=hint_text
                        )
                    else:
                        value = st.text_input(
                            label=hint_text,
                            key=f"field_{field_name}",
                            max_chars=max_len,
                            placeholder=hint_text
                        )

                    # Store value
                    if value is not None:
                        user.set_field_value(field_name, value)

            st.markdown("")  # Add spacing between fields

        # Form submission buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            back_button = st.form_submit_button("◀️ Back", use_container_width=True)

        with col3:
            next_button = st.form_submit_button("Generate User ID ▶️", use_container_width=True, type="primary")

    # Handle form submission
    if back_button:
        st.session_state.page = 'login'
        st.rerun()

    if next_button:
        # Validate that required fields are filled
        # For simplicity, we'll check if user_id was generated successfully
        if not user.user_id or user.user_id == 'unknown':
            st.error("⚠️ Please ensure all fields are filled in correctly, especially the fields required for user ID generation.")
        else:
            # Show confirmation panel
            st.session_state.user_id_confirmed = True
            st.rerun()

def show_confirmation_panel():
    """Display the user ID confirmation panel."""
    user = st.session_state.user

    st.title("✅ User ID Generated")

    st.markdown("### Your User ID has been generated:")

    # Display user ID prominently
    st.markdown(f"# `{user.user_id}`")

    st.warning("""
    **⚠️ IMPORTANT: Please memorize or write down your User ID!**

    You will need this ID if you want to continue rating videos in a future session.
    This ID is the only way to link your ratings across sessions.
    """)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("◀️ Back to Form", use_container_width=True):
            st.session_state.user_id_confirmed = False
            st.rerun()

    with col3:
        if st.button("Understood. Proceed ▶️", use_container_width=True, type="primary"):
            # Save user data and proceed
            if save_user_data(user):
                # Check if familiarization is enabled
                config = st.session_state.config
                enable_familiarization = config.get('settings', {}).get('enable_familiarization', True)

                if enable_familiarization:
                    st.session_state.page = 'pre_familiarization'
                else:
                    st.session_state.page = 'videoplayer'

                st.rerun()
            else:
                st.error("Failed to save user data. Please try again.")
