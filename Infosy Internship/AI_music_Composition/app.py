# app.py - ENHANCED MELODAI WITH BETTER DESIGN
import streamlit as st
from mood_analyzer import MoodAnalyzer
from music_parameters import MusicParameters

def main():
    st.set_page_config(
        page_title="MelodAI - AI Music Composer",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Enhanced pastel color styling
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
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
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
        border: 3px solid #81C784;
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
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize components
    if 'mood_analyzer' not in st.session_state:
        with st.spinner("Loading AI models..."):
            st.session_state.mood_analyzer = MoodAnalyzer()
    if 'music_params' not in st.session_state:
        st.session_state.music_params = MusicParameters()
    if 'user_text' not in st.session_state:
        st.session_state.user_text = ""
    if 'mood_analysis' not in st.session_state:
        st.session_state.mood_analysis = None
    if 'music_params_result' not in st.session_state:
        st.session_state.music_params_result = None
    
    # Header Section
    st.markdown("""
    <div class="main-header">
        <h1 style='font-size: 3.2rem; margin: 0;'>🎵 MelodAI: AI Music Composer</h1>
        <h3 style='font-size: 1.5rem; margin: 0; font-weight: 400;'>
            Transform your emotions into beautiful music
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Input Section
    st.markdown("""
    <div class="input-section">
        <h2 style='color: #5D4037; font-size: 2rem;'>🎤 Describe Your Feelings</h2>
        <p style='color: #757575; font-size: 1.2rem;'>
            Share how you're feeling and we'll generate the perfect music parameters for you
        </p>
    """, unsafe_allow_html=True)
    
    user_text = st.text_area(
        " ",
        placeholder="I'm feeling excited about my new project and looking forward to the weekend...",
        height=120,
        label_visibility="collapsed",
        key="user_input"
    )
    
    # Example Inputs with proper functionality
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
    
    # Create 3 columns for examples
    col1, col2, col3 = st.columns(3)
    example_cols = [col1, col2, col3]
    
    for i, example in enumerate(examples):
        with example_cols[i % 3]:
            if st.button(
                f"🎵 {example}",
                key=f"ex_{i}",
                use_container_width=True
            ):
                st.session_state.user_text = example
                user_text = example
                # Clear previous results when a new example is selected
                st.session_state.mood_analysis = None
                st.session_state.music_params_result = None
                st.rerun()
    
    # Update text area if example is clicked
    if st.session_state.user_text:
        user_text = st.session_state.user_text
    
    # Generate button
    analyze_btn = st.button(
        "🎶 GENERATE MUSIC PARAMETERS", 
        use_container_width=True,
        disabled=not user_text.strip()
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if analyze_btn and user_text:
        with st.spinner("🎵 Analyzing your mood and generating music parameters..."):
            # Analyze mood
            st.session_state.mood_analysis = st.session_state.mood_analyzer.analyze_mood(user_text)
            st.session_state.music_params_result = st.session_state.music_params.get_music_parameters(st.session_state.mood_analysis)
    
    # Display results if available
    if st.session_state.mood_analysis and st.session_state.music_params_result:
        mood_analysis = st.session_state.mood_analysis
        music_params = st.session_state.music_params_result
        
        # Debug: Print the mood analysis to console
        print(f"DEBUG - Mood Analysis: {mood_analysis}")
        
        # Mood Analysis Box - INNOVATIVE LAYOUT
        st.markdown("""
        <div class="analysis-box">
            <h2 style='color: #5D4037; font-size: 2rem; margin-bottom: 2rem; text-align: center;'>🎭 MOOD ANALYSIS</h2>
        """, unsafe_allow_html=True)
        
        # Innovative 2x2 grid layout for mood analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Mood and Sentiment in one column
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
            # Energy and Progress in another column
            energy = mood_analysis.get("energy_level", 5)
            st.markdown(f"""
            <div class="metric-card">
                <h3 style='color: #5D4037; margin: 0; font-size: 1.6rem;'>ENERGY LEVEL</h3>
                <p style='color: #5D4037; margin: 0; font-size: 2.5rem; font-weight: bold;'>{energy}/10</p>
                <div style='margin-top: 1rem;'>
            """, unsafe_allow_html=True)
            st.progress(energy/10)
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Music Parameters Box - ENHANCED LAYOUT
        st.markdown("""
        <div class="music-box">
            <h2 style='color: #2E7D32; font-size: 2rem; margin-bottom: 2rem; text-align: center;'>🎼 MUSIC PARAMETERS</h2>
        """, unsafe_allow_html=True)
        
        # Music parameters in a clean grid
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
        
        # Instruments Section with enhanced colors
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
        
        # Conclusion Box - FINAL USER EXPERIENCE
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
            "neutral": "Well-balanced for various listening experiences."
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

if __name__ == "__main__":
    main()