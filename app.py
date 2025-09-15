# app.py 
import streamlit as st
from mood_analyzer import MoodAnalyzer
from music_parameters import MusicParameters
from music_generator import MusicGenerator
from audio_visualizer import AudioVisualizer
from config import Config
from auth import AuthSystem, UserHistory
import tempfile
import os
import warnings
import time
import json
from datetime import datetime
import base64

# Suppress pydub warnings if any
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub.utils")

# FFmpeg setup - optional Windows path used by the user previously
ffmpeg_path = r"B:\Infosy Internship\AI_music_Composition\ffmpeg-8.0-essentials_build\bin"
if os.path.exists(ffmpeg_path):
    try:
        from pydub import AudioSegment
        # Only set if not already set
        if not hasattr(AudioSegment, '_ffmpeg_configured'):
            AudioSegment.converter = os.path.join(ffmpeg_path, "ffmpeg.exe")
            AudioSegment.ffprobe = os.path.join(ffmpeg_path, "ffprobe.exe")
            AudioSegment._ffmpeg_configured = True  # Mark as configured
            print("✅ FFmpeg configured for pydub")
    except Exception:
        # pydub might not be installed locally; we'll continue gracefully
        print("⚠️ pydub not available or FFmpeg configuration failed.")
else:
    print("❌ FFmpeg not found. Audio processing may be limited.")

# Initialize authentication system
auth_system = AuthSystem()
user_history = UserHistory()

def show_login_page():
    """Display login/signup page with Login and Sign up tabs"""
    st.markdown("""
    <style>
    .auth-container {
        max-width: 500px;
        margin: 5rem auto;
        padding: 3rem;
        background: linear-gradient(135deg, #FFD6E7 0%, #FFEFBA 100%);
        border-radius: 25px;
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        border: 3px solid #FFACC7;
    }
    .auth-header {
        text-align: center;
        color: #5D4037;
        margin-bottom: 2rem;
    }
    .auth-form {
        background: rgba(255, 255, 255, 0.9);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
    }
    .auth-btn {
        background: linear-gradient(135deg, #FFB74D 0%, #FFA726 100%);
        color: white;
        border: 3px solid #FF9800;
        padding: 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        width: 100%;
        margin-top: 1rem;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .auth-toggle {
        text-align: center;
        margin-top: 1.5rem;
        color: #5D4037;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="auth-container">
        <div class="auth-header">
            <h1>🎵 MelodAI</h1>
            <h3>AI Music Composer</h3>
            <p>Transform your emotions into beautiful music</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Tabs for Login and Sign up
    login_tab, signup_tab = st.tabs(["Login", "Sign up"])

    with login_tab:
        st.markdown("""
        <div class="auth-form">
            <h3 style='color: #5D4037; text-align: center;'>Login to Your Account</h3>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Enter your email", key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
            login_btn = st.form_submit_button("Login", use_container_width=True)

            if login_btn:
                user_name = auth_system.login_user(email, password)
                if user_name:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.session_state.user_name = user_name
                    st.rerun()
                else:
                    st.error("Invalid email or password")

        st.markdown("</div>", unsafe_allow_html=True)

    with signup_tab:
        st.markdown("""
        <div class="auth-form">
            <h3 style='color: #5D4037; text-align: center;'>Create an Account</h3>
        """, unsafe_allow_html=True)

        with st.form("signup_form"):
            name = st.text_input("Full Name", placeholder="Enter your full name", key="signup_name")
            email = st.text_input("Email", placeholder="Enter your email", key="signup_email")
            password = st.text_input("Password", type="password", placeholder="Create a password (min. 6 characters)", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="signup_confirm")
            signup_btn = st.form_submit_button("Sign Up", use_container_width=True)

            if signup_btn:
                if not name or not email or not password:
                    st.error("All fields are required.")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                elif auth_system.register_user(name, email, password):
                    st.success("Account created successfully! You can now log in.")
                else:
                    st.error("Failed to create account. Please try again.")

        st.markdown("</div>", unsafe_allow_html=True)

    # --- Project Overview (shown on home before login) ---
    st.markdown("""
    <div class="auth-form">
        <h3 style='color: #5D4037; text-align: center;'>📘 About MelodAI</h3>
        <p style='color: #5D4037;'>
            MelodAI is an AI-powered music composition app that transforms your text and emotions into
            unique musical pieces. Describe how you feel, and MelodAI analyzes your mood, derives
            musical parameters, composes audio, and provides visualizations you can explore and download.
        </p>
        <h4 style='color: #5D4037;'>Key Features</h4>
        <ul style='color: #5D4037;'>
            <li>🎭 Mood analysis from natural language text</li>
            <li>🎼 Automatic music parameters (tempo, key, instruments, dynamics)</li>
            <li>🎹 AI music generation with quick previews and downloads</li>
            <li>📊 Waveform and spectrum visualizations</li>
            <li>📜 Personal history with favorites, tags, and re-generation</li>
            <li>🔐 Account system with profile and password management</li>
        </ul>
        <h4 style='color: #5D4037;'>How It Works</h4>
        <ol style='color: #5D4037;'>
            <li>Sign up or log in to your account</li>
            <li>Describe your feelings on the Compose page</li>
            <li>Analyze mood to get tailored music parameters</li>
            <li>Generate music, visualize it, and download your track</li>
            <li>Find all your creations anytime in History</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

def show_dashboard():
    """Display user dashboard with history and main app"""
    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'compose'
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1.5rem 0;'>
            <h2 style='color: #5D4037;'>🎵 MelodAI</h2>
            <p style='color: #757575;'>Welcome, {}</p>
        </div>
        """.format(st.session_state.user_name), unsafe_allow_html=True)
        
        # Navigation options
        page_options = {
            'compose': '🎹 Compose Music',
            'history': '📜 Generation History',
            'profile': '👤 Profile Settings'
        }
        
        selected_page = st.radio(
            "Navigation",
            options=list(page_options.keys()),
            format_func=lambda x: page_options[x],
            label_visibility="collapsed"
        )
        
        st.session_state.current_page = selected_page
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                if key not in ['mood_analyzer', 'music_params', 'music_generator', 'audio_visualizer']:
                    del st.session_state[key]
            st.rerun()
    
    # Display selected page
    if st.session_state.current_page == 'compose':
        show_composer()
    elif st.session_state.current_page == 'history':
        show_history()
    elif st.session_state.current_page == 'profile':
        show_profile()

def show_composer():
    """Main music composition interface"""
    # Initialize components in session_state (once)
    if 'mood_analyzer' not in st.session_state:
        with st.spinner("Loading Mood Analysis models..."):
            st.session_state.mood_analyzer = MoodAnalyzer()
    if 'music_params' not in st.session_state:
        st.session_state.music_params = MusicParameters()
    if 'music_generator' not in st.session_state:
        with st.spinner("Loading Music Generation models..."):
            # Use cached or persistent generator; heavy model load only once
            st.session_state.music_generator = MusicGenerator()
    if 'audio_visualizer' not in st.session_state:
        st.session_state.audio_visualizer = AudioVisualizer()

    # initialize other session keys
    if 'user_text' not in st.session_state:
        st.session_state.user_text = ""
    if 'mood_analysis' not in st.session_state:
        st.session_state.mood_analysis = None
    if 'music_params_result' not in st.session_state:
        st.session_state.music_params_result = None
    if 'generated_audio' not in st.session_state:
        st.session_state.generated_audio = None
    if 'wav_file_path' not in st.session_state:
        st.session_state.wav_file_path = None
    if 'mp3_file_path' not in st.session_state:
        st.session_state.mp3_file_path = None
    if 'generation_time' not in st.session_state:
        st.session_state.generation_time = None

    # --- Header Section ---
    st.markdown("""
    <div class="main-header">
        <h1 style='font-size: 3.2rem; margin: 0;'>🎵 MelodAI: AI Music Composer</h1>
        <h3 style='font-size: 1.5rem; margin: 0; font-weight: 400;'>
            Transform your emotions into beautiful music
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # --- Input Section ---
    st.markdown("""
    <div class="input-section">
        <h2 style='color: #5D4037; font-size: 2rem;'>🎤 Describe Your Feelings</h2>
        <p style='color: #757575; font-size: 1.2rem;'>
            Share how you're feeling and we'll generate the perfect music for you
        </p>
    """, unsafe_allow_html=True)

    # Apply any pending sample text before creating the widget
    if 'pending_user_text' in st.session_state:
        st.session_state.user_text = st.session_state.pending_user_text
        del st.session_state.pending_user_text

    user_text = st.text_area(
        " ",
        placeholder="I'm feeling excited about my new project and looking forward to the weekend...",
        height=120,
        label_visibility="collapsed",
        key="user_text",
        max_chars=Config.MAX_TEXT_INPUT_LENGTH
    )

    # Character count
    if user_text:
        chars_remaining = Config.MAX_TEXT_INPUT_LENGTH - len(user_text)
        st.caption(f"Characters remaining: {chars_remaining}")

    # Example Inputs
    st.markdown("""
    <h3 style='color: #5D4037; margin-top: 2rem; font-size: 1.5rem;'>💡 Example Inputs:</h3>
    <p style='color: #757575;'>Click any example to try it out:</p>
    """, unsafe_allow_html=True)

    examples = [
        "I'm so happy and excited for the weekend!",
        "I feel sad and lonely today...",
        "I need calm music for studying and focus",
        "I'm pumped and energetic for my workout!",
        "This mystery novel has me intrigued and curious",
        "I love you so much my darling"
    ]

    # 3 columns for examples
    col1, col2, col3 = st.columns(3)
    example_cols = [col1, col2, col3]

    for i, example in enumerate(examples):
        with example_cols[i % 3]:
            if st.button(f"🎵 {example}", key=f"ex_{i}", use_container_width=True):
                st.session_state.pending_user_text = example
                # Reset results for new example
                st.session_state.mood_analysis = None
                st.session_state.music_params_result = None
                st.session_state.generated_audio = None
                st.session_state.wav_file_path = None
                st.session_state.mp3_file_path = None
                st.rerun()

    # No manual session_state update needed; the widget manages it via key

    # Buttons for analyze and generate
    col_analyze, col_generate = st.columns(2)

    with col_analyze:
        analyze_btn = st.button(
            "🎶 ANALYZE MOOD & PARAMETERS",
            use_container_width=True,
            disabled=not user_text.strip(),
            help="Analyze your text to determine mood and generate music parameters"
        )

    with col_generate:
        generate_music_btn = st.button(
            "🎹 GENERATE MUSIC",
            use_container_width=True,
            disabled=not (st.session_state.mood_analysis and st.session_state.music_params_result),
            type="primary",
            help="Generate actual music based on your mood analysis (may take 1-2 minutes)"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Analyze Button Logic ---
    if analyze_btn and user_text:
        with st.spinner("🎵 Analyzing your mood and generating music parameters..."):
            st.session_state.mood_analysis = st.session_state.mood_analyzer.analyze_mood(user_text)
            st.session_state.music_params_result = st.session_state.music_params.get_music_parameters(st.session_state.mood_analysis)
            # Clear any previous generated audio
            st.session_state.generated_audio = None
            st.session_state.wav_file_path = None
            st.session_state.mp3_file_path = None

    # --- Generate Button Logic ---
    if generate_music_btn and user_text:
        start_time = time.time()
        with st.spinner("🎵 Composing your personalized music (this may take 1-2 minutes)..."):
            # Ensure mood analysis present
            if not st.session_state.mood_analysis:
                st.session_state.mood_analysis = st.session_state.mood_analyzer.analyze_mood(user_text)
                st.session_state.music_params_result = st.session_state.music_params.get_music_parameters(st.session_state.mood_analysis)

            # Build prompt and generate
            prompt = st.session_state.music_params_result.get('musicgen_prompt', user_text)
            # generate_music should return a numpy array with audio samples
            generated_audio = st.session_state.music_generator.generate_music(prompt)
            st.session_state.generated_audio = generated_audio

            # Save audio to temp directory (returns wav_path, mp3_path)
            if st.session_state.generated_audio is not None:
                temp_dir = tempfile.mkdtemp()
                base_wav_path = os.path.join(temp_dir, "generated_music.wav")
                wav_path, mp3_path = st.session_state.music_generator.save_audio(
                    st.session_state.generated_audio,
                    base_wav_path
                )
                st.session_state.wav_file_path = wav_path
                st.session_state.mp3_file_path = mp3_path

        st.session_state.generation_time = time.time() - start_time
        
        # Save to user history
        if st.session_state.generated_audio is not None:
            # Read audio file for saving
            with open(st.session_state.mp3_file_path or st.session_state.wav_file_path, "rb") as f:
                audio_data = f.read()
                
            user_history.save_generation(
                st.session_state.user_email,
                user_text,
                st.session_state.mood_analysis,
                st.session_state.music_params_result,
                audio_data,
                st.session_state.generation_time
            )
            # After saving, navigate to history and autoplay the latest once
            st.session_state.autoplay_latest_once = True
            st.session_state.current_page = 'history'
            st.rerun()

    # --- Display Results (Mood analysis, music parameters, audio, visualizations) ---
    if st.session_state.mood_analysis and st.session_state.music_params_result:
        mood_analysis = st.session_state.mood_analysis
        music_params = st.session_state.music_params_result

        # Mood Analysis Box
        st.markdown("""
        <div class="analysis-box">
            <h2 style='color: #5D4037; font-size: 2rem; margin-bottom: 2rem; text-align: center;'>🎭 MOOD ANALYSIS</h2>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            mood = mood_analysis.get("mood", "neutral").upper()
            confidence = mood_analysis.get("mood_confidence", 0.5) * 100
            st.markdown(f"""
            <div class="metric-card">
                <h3 style='color: #5D4037; margin: 0; font-size: 1.6rem;'>MOOD</h3>
                <p style='color: #5D4037; margin: 0; font-size: 2rem; font-weight: bold;'>{mood}</p>
                <p style='color: #757575; margin: 0; font-size: 1.1rem;'>Confidence: {confidence:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)

            sentiment = mood_analysis.get("sentiment", "neutral").title()
            sent_conf = mood_analysis.get("sentiment_confidence", 0.5) * 100
            st.markdown(f"""
            <div class="metric-card">
                <h3 style='color: #5D4037; margin: 0; font-size: 1.6rem;'>SENTIMENT</h3>
                <p style='color: #5D4037; margin: 0; font-size: 2rem; font-weight: bold;'>{sentiment}</p>
                <p style='color: #757575; margin: 0; font-size: 1.1rem;'>Confidence: {sent_conf:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            energy = mood_analysis.get("energy_level", 5)
            st.markdown(f"""
            <div class="metric-card">
                <h3 style'color: #5D4037; margin: 0; font-size: 1.6rem;'>ENERGY LEVEL</h3>
                <p style='color: #5D4037; margin: 0; font-size: 2.5rem; font-weight: bold;'>{energy}/10</p>
                <div style='margin-top: 1rem;'>
            """, unsafe_allow_html=True)
            st.progress(energy / 10)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Music Parameters Box
        st.markdown("""
        <div class="music-box">
            <h2 style'color: #2E7D32; font-size: 2rem; margin-bottom: 2rem; text-align: center;'>🎼 MUSIC PARAMETERS</h2>
        """, unsafe_allow_html=True)

        col3, col4, col5 = st.columns(3)
        with col3:
            tempo = music_params.get('tempo', 100)
            st.markdown(f"""
            <div class="metric-card">
                <h3 style='color: #2E7D32; margin: 0; font-size: 1.6rem;'>TEMPO</h3>
                <p style='color: #2E7D32; margin: 0; font-size: 2rem; font-weight: bold;'>{tempo} BPM</p>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            key = music_params.get('key', 'C')
            scale = music_params.get('scale', 'major')
            st.markdown(f"""
            <div class="metric-card">
                <h3 style='color: #2E7D32; margin: 0; font-size: 1.6rem;'>KEY & SCALE</h3>
                <p style='color: #2E7D32; margin: 0; font-size: 2rem; font-weight: bold;'>{key} {scale}</p>
            </div>
            """, unsafe_allow_html=True)
        with col5:
            dynamics = music_params.get('dynamics', 'mezzo-piano')
            st.markdown(f"""
            <div class="metric-card">
                <h3 style='color: #2E7D32; margin: 0; font-size: 1.6rem;'>DYNAMICS</h3>
                <p style='color: #2E7D32; margin: 0; font-size: 1.8rem; font-weight: bold;'>{dynamics.upper()}</p>
            </div>
            """, unsafe_allow_html=True)

        # Instruments Section
        st.markdown("""
        <h3 style='color: #2E7D32; font-size: 1.8rem; margin: 2.5rem 0 1.5rem 0; text-align: center;'>🎹 INSTRUMENTS TO USE</h3>
        """, unsafe_allow_html=True)

        instruments = music_params.get('instruments', ['piano'])
        instrument_cols = st.columns(min(3, len(instruments)))
        for i, instrument in enumerate(instruments):
            with instrument_cols[i % 3]:
                st.markdown(f"""
                <div class="instrument-item">
                    <span style='font-size: 1.4rem;'>🎵 {instrument.upper()}</span>
                </div>
                """, unsafe_allow_html=True)

        # Additional parameters
        col6, col7 = st.columns(2)
        with col6:
            complexity = music_params.get('complexity', 'medium').title()
            st.markdown(f"""
            <div class="metric-card">
                <h3 style='color: #2E7D32; margin: 0; font-size: 1.6rem;'>COMPLEXITY</h3>
                <p style='color: #2E7D32; margin: 0; font-size: 1.8rem; font-weight: bold;'>{complexity}</p>
            </div>
            """, unsafe_allow_html=True)
        with col7:
            energy_level = music_params.get('energy_level', 5)
            st.markdown(f"""
            <div class="metric-card">
                <h3 style='color: #2E7D32; margin: 0; font-size: 1.6rem;'>ENERGY</h3>
                <p style='color: #2E7D32; margin: 0; font-size: 1.8rem; font-weight: bold;'>{energy_level}/10</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Display generated audio if available
        if st.session_state.generated_audio is not None and (st.session_state.wav_file_path or st.session_state.mp3_file_path):
            st.markdown("""
            <div class="audio-box">
                <h2 style='color: #BF360C; font-size: 2rem; margin-bottom: 1.5rem; text-align: center;'>🎧 YOUR GENERATED MUSIC</h2>
            """, unsafe_allow_html=True)

            # Show generation time if available
            if st.session_state.generation_time:
                st.info(f"🎵 Music generated in {st.session_state.generation_time:.1f} seconds")

            # Prefer MP3 when available
            file_to_play = st.session_state.mp3_file_path or st.session_state.wav_file_path
            if file_to_play and os.path.exists(file_to_play):
                with open(file_to_play, "rb") as f:
                    audio_bytes = f.read()
                mime = "audio/mp3" if file_to_play.endswith(".mp3") else "audio/wav"
                st.audio(audio_bytes, format=mime)

                # Audio Visualizations
                st.markdown("""
                <div class="visualization-box">
                    <h3 style='color: #4E342E; font-size: 1.5rem; margin-bottom: 1.5rem; text-align: center;'>📊 AUDIO VISUALIZATIONS</h3>
                """, unsafe_allow_html=True)

                # show visualizations (expects numpy audio array and Config.MUSICGEN_SAMPLING_RATE)
                st.session_state.audio_visualizer.display_audio_visualizations(
                    st.session_state.generated_audio,
                    Config.MUSICGEN_SAMPLING_RATE,
                    st.session_state.mood_analysis.get('mood', 'neutral'),
                    "Your Generated Music"
                )

                st.markdown("</div>", unsafe_allow_html=True)

                # Download button
                st.download_button(
                    label="📥 Download Music",
                    data=audio_bytes,
                    file_name="melodai_generated_music.mp3" if mime == "audio/mp3" else "melodai_generated_music.wav",
                    mime=mime,
                    use_container_width=True
                )

            st.markdown("</div>", unsafe_allow_html=True)

        # Conclusion Box
        mood = mood_analysis.get("mood", "neutral")
        sentiment = mood_analysis.get("sentiment", "neutral")
        energy = mood_analysis.get("energy_level", 5)

        conclusion_messages = {
            "happy": "Perfect for uplifting and joyful moments!",
            "sad": "Ideal for reflective and emotional expression.",
            "calm": "Great for relaxation and peaceful atmospheres.",
            "energetic": "Perfect for high-energy activities and motivation!",
            "mysterious": "Excellent for creating intrigue and suspense.",
            "romantic": "Beautiful for intimate and loving moments.",
            "neutral": "Great for various listening experiences."
        }

        conclusion = conclusion_messages.get(mood, "Perfectly tailored to your current mood!")

        st.markdown(f"""
        <div class="conclusion-box">
            <h2 style='color: #4527A0; font-size: 2rem; margin-bottom: 1rem;'>✨ MUSIC COMPOSITION READY!</h2>
            <p style='color: #4527A0; font-size: 1.3rem; font-weight: 500;'>
            Based on your <strong>{mood.upper()}</strong> mood with <strong>{sentiment.upper()}</strong> sentiment, 
            we've created a perfect musical composition with <strong>{energy}/10</strong> energy level.
            </p>
            <p style='color: #4527A0; font-size: 1.4rem; font-weight: 600; margin-top: 1rem;'>
            {conclusion}
            </p>
            <p style='color: #4527A0; font-size: 1.2rem; margin-top: 1.5rem;'>
            🎶 Your personalized music is ready to be composed!
            </p>
        </div>
        """, unsafe_allow_html=True)

def show_history():
    """Display user's generation history with enhanced features"""
    st.markdown("""
    <div class="main-header">
        <h1 style='font-size: 2.8rem; margin: 0;'>📜 Your Generation History</h1>
        <h3 style='font-size: 1.4rem; margin: 0; font-weight: 400;'>
            Review your past music compositions
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user history
    history = user_history.get_user_history(st.session_state.user_email)
    
    if not history:
        st.info("You haven't generated any music yet. Go to the Compose page to create your first composition!")
        return
    
    # Filter and search options
    col_search, col_filter, col_sort = st.columns([2, 2, 2])
    
    with col_search:
        search_text = st.text_input("🔍 Search history", placeholder="Search by text or mood...")
    
    with col_filter:
        mood_filter = st.selectbox("Filter by mood", 
                                 ["All"] + list(set([entry.get('mood_analysis', {}).get('mood', 'Unknown') 
                                                    for entry in history])))
    
    with col_sort:
        sort_order = st.selectbox("Sort by", ["Newest first", "Oldest first"])
    
    # Filter history
    filtered_history = history
    if search_text:
        filtered_history = [entry for entry in filtered_history 
                          if search_text.lower() in entry.get('input_text', '').lower() or
                          search_text.lower() in entry.get('mood_analysis', {}).get('mood', '').lower()]
    
    if mood_filter != "All":
        filtered_history = [entry for entry in filtered_history 
                          if entry.get('mood_analysis', {}).get('mood', '') == mood_filter]
    
    # Sort history
    if sort_order == "Newest first":
        filtered_history = sorted(filtered_history, 
                                key=lambda x: x.get('timestamp', ''), 
                                reverse=True)
    else:
        filtered_history = sorted(filtered_history, 
                                key=lambda x: x.get('timestamp', ''))
    
    if not filtered_history:
        st.info("No matching entries found.")
        return
    
    # Pagination controls
    if 'history_pages_shown' not in st.session_state:
        st.session_state.history_pages_shown = 1

    col_pp, col_more, col_all = st.columns([1, 1, 1])
    with col_pp:
        items_per_page = st.selectbox("Items per page", [5, 10, 20, 50], index=0)
    end_idx = st.session_state.history_pages_shown * items_per_page
    entries_to_show = filtered_history[:end_idx]

    # Autoplay logic: if requested, auto-play the newest entry once
    autoplay_done = False

    # Display history
    for i, entry in enumerate(entries_to_show):
        # Create a unique key for each entry
        entry_key = f"entry_{entry.get('timestamp', str(i))}"
        
        with st.expander(f"🎵 {entry.get('input_text', 'Unknown')[:50]}... - {entry.get('timestamp', 'Unknown date')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Mood Analysis**")
                mood_data = entry.get('mood_analysis', {})
                st.write(f"**Mood:** {mood_data.get('mood', 'Unknown')}")
                st.write(f"**Sentiment:** {mood_data.get('sentiment', 'Unknown')}")
                st.write(f"**Energy Level:** {mood_data.get('energy_level', 'Unknown')}/10")
                if 'mood_confidence' in mood_data:
                    st.write(f"**Confidence:** {mood_data.get('mood_confidence', 0) * 100:.1f}%")
                
            with col2:
                st.markdown("**Music Parameters**")
                params_data = entry.get('music_params', {})
                st.write(f"**Tempo:** {params_data.get('tempo', 'Unknown')} BPM")
                st.write(f"**Key:** {params_data.get('key', 'Unknown')} {params_data.get('scale', 'Unknown')}")
                st.write(f"**Instruments:** {', '.join(params_data.get('instruments', ['Unknown']))}")
                st.write(f"**Duration:** {entry.get('generation_time', 0):.1f} seconds")
            
            # Favorite and play count features
            col_fav, col_play, _ = st.columns([1, 1, 2])
            with col_fav:
                is_favorite = entry.get('favorite', False)
                fav_label = "❤️ Remove from favorites" if is_favorite else "🤍 Add to favorites"
                if st.button(fav_label, key=f"fav_{entry_key}"):
                    user_history.mark_as_favorite(st.session_state.user_email, entry['timestamp'], not is_favorite)
                    st.rerun()

            with col_play:
                st.write(f"▶️ Played: {entry.get('play_count', 0)} times")
            
            # Audio player with enhanced controls
            if 'audio_data' in entry and entry['audio_data']:
                st.markdown("**🎧 Audio Preview**")
                # Standard player
                st.audio(entry['audio_data'], format="audio/mp3")

                # One-time autoplay for the newest entry after generation
                if not autoplay_done and st.session_state.get('autoplay_latest_once'):
                    try:
                        audio_b64 = base64.b64encode(entry['audio_data']).decode('utf-8')
                        st.markdown(f"""
                        <audio autoplay>
                            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                        </audio>
                        """, unsafe_allow_html=True)
                        autoplay_done = True
                    except Exception:
                        pass
                
                # Action buttons
                col_download, col_regenerate, col_delete = st.columns(3)
                
                with col_download:
                    st.download_button(
                        label="📥 Download",
                        data=entry['audio_data'],
                        file_name=f"melodai_{entry.get('timestamp', 'unknown').replace(':', '-').replace(' ', '_')}.mp3",
                        mime="audio/mp3",
                        key=f"download_{entry_key}"
                    )
                
                with col_regenerate:
                    if st.button("🔄 Regenerate", key=f"regenerate_{entry_key}"):
                        # Store the input text for regeneration
                        st.session_state.user_text = entry.get('input_text', '')
                        st.session_state.current_page = 'compose'
                        st.rerun()
                
                with col_delete:
                    if st.button("🗑️ Delete", key=f"delete_{entry_key}"):
                        if user_history.delete_entry(st.session_state.user_email, entry['timestamp']):
                            st.success("Entry deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete entry")
            
            # Tags section
            if 'tags' in entry and entry['tags']:
                st.markdown("**🏷️ Tags:**")
                tag_cols = st.columns(3)
                for i, tag in enumerate(entry['tags'][:3]):
                    with tag_cols[i % 3]:
                        st.markdown(f"`{tag}`")
            
            # Add tags functionality
            with st.form(f"add_tags_{entry_key}"):
                new_tags = st.text_input("Add tags (comma-separated)", key=f"new_tags_{entry_key}")
                if st.form_submit_button("Add Tags"):
                    if new_tags:
                        tags_list = [tag.strip() for tag in new_tags.split(',')]
                        if user_history.add_tags(st.session_state.user_email, entry['timestamp'], tags_list):
                            st.success("Tags added!")
                            st.rerun()
                        else:
                            st.error("Failed to add tags")

    # Clear the autoplay flag after rendering once
    if st.session_state.get('autoplay_latest_once'):
        st.session_state.autoplay_latest_once = False

    # Show more / Show all buttons
    with col_more:
        if end_idx < len(filtered_history):
            if st.button("Show more"):
                st.session_state.history_pages_shown += 1
                st.rerun()
    with col_all:
        if end_idx < len(filtered_history):
            if st.button("Show all"):
                total_pages = (len(filtered_history) + items_per_page - 1) // items_per_page
                st.session_state.history_pages_shown = total_pages
                st.rerun()

def show_profile():
    """Display user profile settings with editing functionality"""
    st.markdown("""
    <div class="main-header">
        <h1 style='font-size: 2.8rem; margin: 0;'>👤 Your Profile</h1>
        <h3 style='font-size: 1.4rem; margin: 0; font-weight: 400;'>
            Manage your account settings
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    user_data = auth_system.get_user_data(st.session_state.user_email)
    
    # Edit mode toggle
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    
    col_toggle, _ = st.columns([1, 3])
    with col_toggle:
        if st.button("✏️ Edit Profile" if not st.session_state.edit_mode else "❌ Cancel Editing", 
                    use_container_width=True):
            st.session_state.edit_mode = not st.session_state.edit_mode
            st.rerun()
    
    st.markdown("""
    <div class="input-section">
        <h2 style='color: #5D4037; font-size: 1.8rem;'>Account Information</h2>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.edit_mode:
            new_name = st.text_input("Name", value=user_data.get('name', ''), key="edit_name")
        else:
            st.text_input("Name", value=user_data.get('name', ''), disabled=True)
    with col2:
        st.text_input("Email", value=st.session_state.user_email, disabled=True)
    
    # Display additional user info
    st.markdown("**Account Details:**")
    col3, col4 = st.columns(2)
    with col3:
        st.write(f"**Created:** {user_data.get('created_at', 'Unknown')}")
    with col4:
        st.write(f"**Last Login:** {user_data.get('last_login', 'Unknown')}")
    
    # Save changes if in edit mode
    if st.session_state.edit_mode:
        if st.button("💾 Save Changes", use_container_width=True):
            if auth_system.update_user_data(st.session_state.user_email, {"name": new_name}):
                st.session_state.user_name = new_name
                st.session_state.edit_mode = False
                st.success("Profile updated successfully!")
                st.rerun()
            else:
                st.error("Failed to update profile")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Change password section
    st.markdown("""
    <div class="input-section">
        <h2 style='color: #5D4037; font-size: 1.8rem;'>Change Password</h2>
    """, unsafe_allow_html=True)
    
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        change_btn = st.form_submit_button("Change Password", use_container_width=True)
        
        if change_btn:
            if new_password != confirm_password:
                st.error("New passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters long")
            elif not auth_system.change_password(st.session_state.user_email, current_password, new_password):
                st.error("Current password is incorrect")
            else:
                st.success("Password changed successfully!")
    
    st.markdown("</div>", unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="MelodAI - AI Music Composer",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    # --- Styling: full pastel theme and custom classes (kept as original) ---
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #FFD6E7 0%, #FFEFBA 100%);
        padding: 3rem;
        border-radius: 25px;
        color: #5D4037;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        border: 3px solid #FFACC7;
    }
    .input-section {
        background: linear-gradient(135deg, #FCE4EC 0%, #F3E5F5 100%);
        padding: 2.5rem;
        border-radius: 25px;
        margin: 1rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.10);
        border: 3px solid #F8BBD0;
    }
    .analysis-box {
        background: linear-gradient(135deg, #FFF9C4 0%, #FFECB3 100%);
        padding: 2.5rem;
        border-radius: 25px;
        color: #5D4037;
        margin: 1rem 0;
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        border: 3px solid #FFD54F;
    }
    .music-box {
        background: linear-gradient(135deg, #C8E6C9 0%, #B3E5FC 100%);
        padding: 2.5rem;
        border-radius: 25px;
        color: #2E7D32;
        margin: 1rem 0;
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        border: 3px solid #81D4FA;
    }
    .conclusion-box {
        background: linear-gradient(135deg, #D1C4E9 0%, #BBDEFB 100%);
        padding: 2.5rem;
        border-radius: 25px;
        color: #4527A0;
        margin: 1rem 0;
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        border: 3px solid #9575CD;
        text-align: center;
    }
    .audio-box {
        background: linear-gradient(135deg, #FFCCBC 0%, #FFE0B2 100%);
        padding: 2.5rem;
        border-radius: 25px;
        color: #BF360C;
        margin: 1rem 0;
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        border: 3px solid #FFAB91;
        text-align: center;
    }
    .visualization-box {
        background: linear-gradient(135deg, #D7CCC8 0%, #BCAAA4 100%);
        padding: 2.5rem;
        border-radius: 25px;
        color: #4E342E;
        margin: 1rem 0;
        box-shadow: 0 12px 20px rgba(0,0,0,0.15);
        border: 3px solid #A1887F;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.8rem;
        border-radius: 20px;
        text-align: center;
        margin: 0.8rem;
        border: 3px solid rgba(255, 255, 255, 0.8);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        color: #5D4037;
    }
    .example-btn {
        background: linear-gradient(135deg, #B3E5FC 0%, #B2EBF2 100%);
        color: #01579B;
        border: 3px solid #4FC3F7;
        padding: 1.2rem;
        border-radius: 20px;
        margin: 0.8rem 0;
        width: 100%;
        text-align: left;
        cursor: pointer;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .example-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        background: linear-gradient(135deg, #4FC3F7 0%, #4DD0E1 100%);
    }
    .generate-btn {
        background: linear-gradient(135deg, #FFB74D 0%, #FFA726 100%);
        color: white;
        border: 3px solid #FF9800;
        padding: 1.5rem 3rem;
        border-radius: 20px;
        font-size: 1.3rem;
        font-weight: bold;
        margin-top: 2rem;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .generate-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.3);
        background: linear-gradient(135deg, #FFA726 0%, #FF9800 100%);
    }
    .generate-music-btn {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
        color: white;
        border: 3px solid #2E7D32;
        padding: 1.5rem 3rem;
        border-radius: 20px;
        font-size: 1.3rem;
        font-weight: bold;
        margin-top: 1rem;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .generate-music-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.3);
        background: linear-gradient(135deg, #66BB6A 0%, #4CAF50 100%);
    }
    .instrument-item {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 18px;
        margin: 1rem 0;
        border: 3px solid #A5D6A7;
        color: #2E7D32;
        font-weight: 700;
        font-size: 1.2rem;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        text-align: center;
    }
    .dark-text {
        color: #5D4037;
        font-weight: bold;
    }
    .light-text {
        color: #757575;
    }
    .stButton>button {
        width: 100%;
    }
    .stTab > div > tab-panel > div > div {
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Check if user is logged in
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        show_login_page()
    else:
        # Get user name if not already in session state
        if 'user_name' not in st.session_state:
            user_data = auth_system.get_user_data(st.session_state.user_email)
            st.session_state.user_name = user_data.get('name', 'User')
        
        show_dashboard()

if __name__ == "__main__":
    main()