"""
Familiarization trials page - Practice rating interface.
Displays familiarization videos with rating scales but doesn't save data.
Always shows the same 3 videos for all users.
"""
import streamlit as st
import streamlit.components.v1 as components
import os
import pandas as pd
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from utils.config_loader import load_rating_scales
from utils.styling import apply_compact_layout, set_video_height, set_spacing

def display_video_with_mode(video_file_path, playback_mode='loop'):
    """
    Display video with specified playback mode.

    Parameters:
    - video_file_path: Path to the video file
    - playback_mode: 'loop' or 'once'
        - 'loop': Autoplay, loop enabled, controls visible
        - 'once': Autoplay, no loop, no controls (plays once only)
    """
    if not os.path.exists(video_file_path):
        st.error(f"Video file not found: {video_file_path}")
        return

    if playback_mode == 'loop':
        # Loop mode: autoplay with controls and looping
        st.video(video_file_path, autoplay=True, loop=True)

    elif playback_mode == 'once':
        # Once mode: autoplay without controls, no loop, plays once only
        # Read video file and encode as base64
        with open(video_file_path, 'rb') as f:
            video_bytes = f.read()
        video_base64 = base64.b64encode(video_bytes).decode()

        # Create HTML5 video player without controls
        # Use object-fit: contain to ensure video is never cropped
        video_html = f"""
        <div style="width: 100%; height: 100vh; display: flex; align-items: center; justify-content: center;">
            <video
                autoplay
                muted
                style="max-width: 100%; max-height: 100%; width: auto; height: auto; object-fit: contain;"
                onended="this.pause();"
            >
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        <style>
            video::-webkit-media-controls {{
                display: none !important;
            }}
            video::-webkit-media-controls-enclosure {{
                display: none !important;
            }}
        </style>
        """
        components.html(video_html, height=600)

    else:
        # Fallback to default
        st.video(video_file_path)

def show():
    """Display the familiarization trials screen."""
    user = st.session_state.user
    config = st.session_state.config

    if not config:
        st.error("Configuration not loaded. Please restart the application.")
        return

    # Initialize familiarization state
    if 'familiarization_initialized' not in st.session_state:
        initialize_familiarization(config)

    # Check if there are videos to show
    if not st.session_state.get('familiarization_videos'):
        st.title("⚠️ Familiarization Videos Not Found")
        st.error(f"""
        No familiarization videos found in the configured directory.

        **Current path in config:** `{config['paths'].get('familiarization_video_path', 'videos_familiarization')}`

        **Current working directory:** `{os.getcwd()}`

        Please check:
        1. The familiarization_video_path in config.yaml is correct
        2. The directory exists and contains .mp4 files
        3. The path is correct relative to the app's working directory
        """)

        if st.button("◀️ Back to Pre-Familiarization", use_container_width=True):
            st.session_state.page = 'pre_familiarization'
            st.session_state.familiarization_initialized = False
            st.rerun()
        return

    # Load current video
    current_video_index = st.session_state.get('familiarization_video_index', 0)
    videos = st.session_state.familiarization_videos

    if current_video_index >= len(videos):
        # All familiarization videos completed - navigate to post-familiarization screen
        st.session_state.page = 'post_familiarization'
        st.session_state.familiarization_initialized = False
        st.rerun()
        return

    current_video = videos[current_video_index]

    # Display the rating interface (without saving)
    display_familiarization_interface(current_video, config)

def initialize_familiarization(config):
    """Initialize familiarization state - load videos and rating scales."""
    # Load rating scales
    st.session_state.rating_scales = load_rating_scales(config)

    # Track which scales are required
    st.session_state.required_scales = [
        scale.get('title') for scale in st.session_state.rating_scales
        if scale.get('required_to_proceed', True)
    ]

    # Get familiarization video path from config
    familiarization_path = config['paths'].get('familiarization_video_path', 'videos_familiarization')

    # Get all video files from familiarization folder
    try:
        all_videos = [f for f in os.listdir(familiarization_path) if f.lower().endswith('.mp4')]
        # Sort to ensure consistent order for all users
        all_videos.sort()
        print(f"[INFO] Found {len(all_videos)} familiarization videos in {familiarization_path}")
    except FileNotFoundError:
        st.error(f"Familiarization video directory not found: {familiarization_path}")
        print(f"[ERROR] Directory not found: {familiarization_path}")
        print(f"[INFO] Current working directory: {os.getcwd()}")
        all_videos = []
    except Exception as e:
        st.error(f"Error loading familiarization videos: {e}")
        print(f"[ERROR] Error loading videos from {familiarization_path}: {e}")
        all_videos = []

    # Store in session state
    st.session_state.familiarization_videos = all_videos
    st.session_state.familiarization_video_index = 0
    st.session_state.familiarization_path = familiarization_path
    st.session_state.familiarization_initialized = True

def display_familiarization_interface(video_filename, config):
    """Display the familiarization rating interface."""
    # Apply compact layout to minimize scrolling
    apply_compact_layout()

    # Optionally set video height (as percentage of viewport height)
    set_video_height(height_vh=40)  # Video takes 40% of screen height

    familiarization_path = st.session_state.familiarization_path
    rating_scales = st.session_state.rating_scales

    # Display options from config
    video_playback_mode = config['settings'].get('video_playback_mode', 'loop')

    # Add familiarization header
    st.info("🎯 **Familiarization Trial** - Practice rating videos. These ratings will not be saved.")

    current_index = st.session_state.familiarization_video_index
    total_videos = len(st.session_state.familiarization_videos)
    st.markdown(f"**Video {current_index + 1} of {total_videos}**")

    st.markdown("---")

    # Video display (no metadata or pitch for familiarization)
    video_file = os.path.join(familiarization_path, video_filename)
    display_video_with_mode(video_file, video_playback_mode)

    # Action not recognized button
    action_not_recognized = st.button(
        "⚠️ Action not recognized", type="primary",
        key=f"famil_not_recognized_{video_filename}",
        help="Check this if you cannot identify or rate this action",
        use_container_width=True
    )

    st.markdown("---")

    # Rating scales
    st.markdown("### Please rate the action on the following dimensions:")

    scale_values = {}

    for scale_config in rating_scales:
        scale_type = scale_config.get('type', 'discrete')
        title = scale_config.get('title', 'Scale')
        label_low = scale_config.get('label_low', '')
        label_high = scale_config.get('label_high', '')
        required = scale_config.get('required_to_proceed', True)

        # Display scale title and labels
        st.markdown(f"**{title}** {'*(required)*' if required and not action_not_recognized else ''}")

        col_low, col_scale, col_high = st.columns([1, 3, 1])

        with col_low:
            st.markdown(f"*{label_low}*")

        with col_scale:
            if scale_type == 'discrete':
                values = scale_config.get('values', [1, 2, 3, 4, 5, 6, 7])
                selected = st.pills(
                    label=title,
                    options=values,
                    key=f"famil_scale_{video_filename}_{title}",
                    label_visibility="collapsed",
                    width="stretch"
                )
                scale_values[title] = selected

            elif scale_type == 'slider':
                slider_min = scale_config.get('slider_min', 0)
                slider_max = scale_config.get('slider_max', 100)
                selected = st.slider(
                    label=title,
                    min_value=float(slider_min),
                    max_value=float(slider_max),
                    value=float(slider_min + slider_max) / 2,
                    key=f"famil_scale_{video_filename}_{title}",
                    label_visibility="collapsed"
                )
                scale_values[title] = selected

            elif scale_type == 'text':
                selected = st.text_input(
                    label=title,
                    key=f"famil_scale_{video_filename}_{title}",
                    placeholder="Enter your response...",
                    label_visibility="collapsed"
                )
                scale_values[title] = selected if selected else None

        with col_high:
            st.markdown(f"*{label_high}*")

        st.markdown("")  # Spacing

    st.markdown("---")

    # Navigation and submission buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("◀️ Back to Questionnaire", use_container_width=True):
            if st.session_state.get('confirm_back_famil', False):
                st.session_state.page = 'questionnaire'
                st.session_state.user_id_confirmed = False
                st.session_state.familiarization_initialized = False
                st.rerun()
            else:
                st.session_state.confirm_back_famil = True
                st.warning("⚠️ Click again to confirm.")

    with col3:
        if st.button("Continue ▶️", use_container_width=True, type="primary"):
            # Validate ratings (same validation as main rating screen)
            if not action_not_recognized:
                # Check that all required scales have values
                required_scales = st.session_state.required_scales
                missing_scales = [
                    title for title in required_scales
                    if scale_values.get(title) is None or scale_values.get(title) == ''
                ]

                if missing_scales:
                    st.error(f"⚠️ Please provide ratings for all required scales: {', '.join(missing_scales)}")
                    st.stop()

            # Don't save rating - just move to next video
            st.session_state.familiarization_video_index += 1
            st.session_state.confirm_back_famil = False
            st.rerun()
