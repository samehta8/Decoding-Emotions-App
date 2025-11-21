# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit-based web application for collecting subjective ratings of video clips (originally soccer actions, now adapted for emotion decoding research). Users complete a demographic questionnaire, watch familiarization videos, then rate a series of videos using customizable rating scales. The app supports stratified video sampling and flexible data persistence (local JSON, Google Sheets, or both).

## Running the Application

### Installation

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Important:** The Google Sheets package is `st-gsheets-connection` (with hyphens), but imports as `from streamlit_gsheets import GSheetsConnection` (with underscores).

### Local Development

```bash
# Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### Testing Without Full Setup

To test without videos or database:
1. Set `display_metadata: false` and `display_pitch: false` in `config/config.yaml`
2. Set `enable_familiarization: false` to skip familiarization screens
3. Place a few test `.mp4` files in the configured video path

## Key Architecture Concepts

### Multi-Page Navigation Flow

The app uses session state-based navigation (not Streamlit's native multipage):

```
welcome → login → questionnaire → pre_familiarization →
familiarization → post_familiarization → videoplayer
```

Navigation is controlled by `st.session_state.page` in `app.py:60-102`. Each page imports its module conditionally to avoid loading all pages at startup.

### Dual Storage Architecture

The app supports three storage modes (configured in `config/config.yaml`):

- `"local"`: Save to JSON files only (`user_data/`, `user_ratings/`)
- `"online"`: Save to Google Sheets only (requires `.streamlit/secrets.toml`)
- `"both"`: Write to both simultaneously for redundancy

**Critical implementation details:**
- Storage logic is centralized in `utils/data_persistence.py`
- Google Sheets operations use `utils/gsheets_manager.py`
- Always use `save_rating()` and `save_user_data()` functions—never write directly to files or sheets
- See `GSHEETS_ARCHITECTURE.md` for detailed documentation on Google Sheets integration

### Stratified Video Sampling

Videos can be selected using hierarchical stratified sampling (lines 21-148 in `pages/videoplayer.py`):

```yaml
# In config/config.yaml
variables_for_stratification:
  - variable: "LowHighPD"
    levels: ["Low", "High"]
    proportions: [0.5, 0.5]
  - variable: "WinLose"
    levels: ["Win", "Loss"]
    proportions: [0.5, 0.5]
```

The algorithm (`stratified_sample_videos`) applies each stratification variable hierarchically—first variable has highest priority, then second variable is balanced within each first-level stratum, etc.

### Configuration System

All behavior is driven by YAML files in `config/`:

- `config.yaml`: Paths, storage mode, video sampling, display settings
- `questionnaire_fields.yaml`: Dynamic form generation for demographics
- `rating_scales.yaml`: Dynamic rating scale generation

**Important:** The app loads config once at startup (`app.py:49-54`). Changes to YAML files require an app restart.

### User ID Generation

User IDs are generated from demographic data using fields marked with `required_for_user_id: true` in `questionnaire_fields.yaml`. The algorithm is in `utils/user.py` and ensures anonymous but reproducible identification.

### Video Playback Modes

Two modes configured via `video_playback_mode` in `config.yaml`:

- `"loop"`: Video autoplays and repeats with visible controls
- `"once"`: Video plays once, no controls, cannot be replayed

Implementation is in `pages/videoplayer.py:150+` using custom HTML5 video components.

## Common Development Tasks

### Adding a New Rating Scale

Edit `config/rating_scales.yaml`:

```yaml
- active: true
  type: "discrete"  # or "slider" or "text"
  title: "Scale Name"
  label_low: "Low end"
  label_high: "High end"
  values: [1, 2, 3, 4, 5]  # for discrete only
  required_to_proceed: true
```

### Adding a New Questionnaire Field

Edit `config/questionnaire_fields.yaml`:

```yaml
- active: true
  type: "multiple_choice"  # or "text" or "numeric"
  field_name: "new_field"
  title: "Question Text"
  options: ["Option 1", "Option 2"]
  required_for_user_id: false  # Set true to include in user ID
```

### Modifying Video Selection Logic

Video selection happens in `pages/videoplayer.py:initialize_video_player()`:

1. Load all videos from `video_path`
2. Filter out already-rated videos (via `get_rated_videos_for_user`)
3. Apply stratified sampling if configured
4. Randomize presentation order

### Working with Google Sheets Integration

**Setup:**
1. Create `.streamlit/secrets.toml` with service account credentials (NEVER commit this file)
2. Share the Google Sheet with the service account email
3. Set `storage_mode: "online"` or `"both"` in `config.yaml`

**Key functions:**
- `get_gsheets_connection()`: Cached singleton connection
- `append_rating_to_gsheets()`: Append ratings row
- `append_user_to_gsheets()`: Append user demographics row
- `get_rated_videos_for_user_from_gsheets()`: Query existing ratings

See `GSHEETS_ARCHITECTURE.md` for deployment checklist and troubleshooting.

## Important Files to Understand

### Core Application Files

- `app.py`: Entry point, session state initialization, page routing
- `utils/user.py`: User model and ID generation algorithm
- `utils/data_persistence.py`: All save/load operations (implements storage mode logic)
- `utils/config_loader.py`: YAML configuration parsing

### Page Modules

All pages follow the pattern of having a `show()` function that renders the UI:

- `pages/welcome.py`: Instructions screen
- `pages/login.py`: Returning user validation
- `pages/questionnaire.py`: Dynamic form from `questionnaire_fields.yaml`
- `pages/pre_familiarization.py`: Pre-familiarization instructions
- `pages/familiarization.py`: Practice videos (always shows same 3 videos)
- `pages/post_familiarization.py`: Post-familiarization transition
- `pages/videoplayer.py`: Main rating interface (most complex page)

### Data Export

- `utils/export_to_csv.py`: Standalone script to export all data to CSV
  - Can be run directly: `python utils/export_to_csv.py`
  - Creates `output/ratings.csv`, `output/mean_ratings.csv`, `output/users.csv`

## Deployment Considerations

### Streamlit Cloud

1. Push to GitHub (ensure `.streamlit/secrets.toml` is in `.gitignore`)
2. Add secrets via Streamlit Cloud dashboard (Settings → Secrets)
3. Configure `metadata_path` and `video_path` to use cloud storage (S3, Google Drive, etc.)
4. Set `storage_mode: "online"` since local files are ephemeral on Streamlit Cloud

### Local/Self-Hosted

1. Use `storage_mode: "local"` or `"both"`
2. Configure absolute paths in `config.yaml`
3. Ensure video files are `.mp4` format (H.264 codec recommended)
4. For DuckDB metadata: use `.duckdb` file with `events` table
5. For CSV metadata: ensure `id` column matches video filenames (without `.mp4`)

## Troubleshooting

### Videos Not Loading

- Check `video_path` in `config/config.yaml` is correct
- Verify files are `.mp4` format
- Check file permissions

### Google Sheets Connection Issues

- Verify `.streamlit/secrets.toml` exists and has correct credentials
- Check that sheet is shared with service account email
- Test connection by enabling the optional test in `pages/welcome.py`

### Configuration Errors

- Validate YAML syntax (indentation matters)
- Restart app after config changes
- Check console output for specific error messages

## Migration from Kivy Version

This is a web port of a desktop Kivy application. Key differences:

- Same JSON data format (fully compatible)
- Same configuration files
- Same user ID algorithm
- Web-based navigation instead of keyboard shortcuts
- Browser video player instead of Kivy video widget

See `MIGRATION_GUIDE.md` for complete comparison.

## Related Documentation

- `README.md`: User-facing documentation, installation, features
- `QUICKSTART.md`: Fast setup guide for first-time users
- `GSHEETS_ARCHITECTURE.md`: Detailed Google Sheets integration architecture
- `MIGRATION_GUIDE.md`: Differences from Kivy desktop version
