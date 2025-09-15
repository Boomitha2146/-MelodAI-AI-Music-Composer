class Config:
    # Mood analysis models
    SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    MAX_LENGTH = 128
    DEVICE = "cpu"   # ✅ Force CPU mode
    
    MOOD_CATEGORIES = ["happy", "sad", "calm", "energetic", "mysterious", "romantic"]

    # Music generation models
    MUSICGEN_MODEL = "facebook/musicgen-small"

    MUSICGEN_DURATION = 16 # seconds
    MUSICGEN_SAMPLING_RATE = 32000

    # Audio processing settings
    AUDIO_FORMAT = "mp3"
    AUDIO_BITRATE = "128k"
    DEFAULT_TEMPO = 120  # BPM

    # File paths
    TEMP_AUDIO_DIR = "temp_audio"
    OUTPUT_FILENAME = "generated_music"

    # Generation parameters
    TOP_K = 250
    TOP_P = 0.8
    TEMPERATURE = 1.0
    CLASSIFIER_FREE_GUIDANCE = 3.0  # CFG scale
    TOKENS_PER_SECOND = 50          # controls how long audio is

    # UI settings
    MAX_TEXT_INPUT_LENGTH = 500
