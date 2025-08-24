import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from scipy.special import softmax
import re
from collections import defaultdict

class MoodAnalyzer:
    def __init__(self):
        # Sentiment analysis model
        self.sentiment_model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.sentiment_tokenizer = AutoTokenizer.from_pretrained(self.sentiment_model_name)
        self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(self.sentiment_model_name)
        
        # Enhanced mood keywords with energy profiles
        self.mood_keywords = {
            'happy': {
                'keywords': ['happy', 'excited', 'joy', 'joyful', 'delighted', 'cheerful', 'glad', 'pleased', 'ecstatic'],
                'base_energy': 8.0,
                'energy_range': (6, 10)
            },
            'sad': {
                'keywords': ['sad', 'unhappy', 'depressed', 'miserable', 'heartbroken', 'gloomy', 'sorrow', 'lonely', 'blue'],
                'base_energy': 3.5,
                'energy_range': (2, 5)
            },
            'calm': {
                'keywords': ['calm', 'peaceful', 'relaxed', 'serene', 'tranquil', 'quiet', 'still', 'chill', 'mellow'],
                'base_energy': 5.0,
                'energy_range': (4, 7)
            },
            'energetic': {
                'keywords': ['energetic', 'active', 'lively', 'dynamic', 'vibrant', 'pumped', 'exhilarated', 'energized'],
                'base_energy': 9.0,
                'energy_range': (7, 10)
            },
            'mysterious': {
                'keywords': ['mysterious', 'curious', 'intrigued', 'puzzled', 'enigmatic', 'cryptic', 'wondering'],
                'base_energy': 6.5,
                'energy_range': (5, 8)
            },
            'romantic': {
                'keywords': ['romantic', 'loving', 'affectionate', 'passionate', 'intimate', 'tender', 'love', 'heart', 
                           'adore', 'cherish', 'desire', 'yearning', 'amorous', 'enamored'],
                'base_energy': 7.0,
                'energy_range': (6, 9)
            }
        }
        
        # Energy modifiers with more balanced values
        self.energy_modifiers = {
            'excited': 1.2, 'energetic': 1.3, 'pumped': 1.5, 'dynamic': 0.8,
            'lively': 1.0, 'vibrant': 0.9, 'active': 0.8, 'hyper': 1.8,
            'calm': -0.8, 'relaxed': -0.7, 'peaceful': -0.6, 'serene': -0.7,
            'tired': -1.2, 'exhausted': -1.5, 'sleepy': -1.0, 'lethargic': -1.1,
            'romantic': 0.5, 'loving': 0.4, 'passionate': 0.7, 'intimate': 0.3
        }
        
        print("✅ Models loaded successfully!")

    def analyze_sentiment(self, text):
        try:
            encoded_text = self.sentiment_tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
            output = self.sentiment_model(**encoded_text)
            scores = output.logits[0].detach().numpy()
            scores = softmax(scores)
            
            sentiment_labels = {0: 'negative', 1: 'neutral', 2: 'positive'}
            sentiment_idx = scores.argmax()
            sentiment = sentiment_labels[sentiment_idx]
            confidence = float(scores[sentiment_idx])
            
            return sentiment, confidence
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return "neutral", 0.5

    def detect_mood(self, text):
        text_lower = text.lower()
        mood_scores = defaultdict(float)
        
        for mood, mood_data in self.mood_keywords.items():
            for keyword in mood_data['keywords']:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, text_lower)
                if matches:
                    mood_scores[mood] += len(matches) * 1.5
        
        if not mood_scores:
            sentiment, _ = self.analyze_sentiment(text)
            if sentiment == 'positive':
                return 'happy', 0.6
            elif sentiment == 'negative':
                return 'sad', 0.6
            else:
                return 'calm', 0.6
        
        detected_mood = max(mood_scores, key=mood_scores.get)
        max_score = mood_scores[detected_mood]
        total_score = sum(mood_scores.values())
        
        confidence = max_score / total_score if total_score > 0 else 0.5
        confidence = max(0.1, min(0.99, confidence))
        
        return detected_mood, confidence

    def calculate_energy(self, text, sentiment, sentiment_confidence, detected_mood):
        text_lower = text.lower()
        
        # Start with mood-specific base energy
        mood_data = self.mood_keywords.get(detected_mood, {'base_energy': 5.0, 'energy_range': (3, 8)})
        energy = mood_data['base_energy']
        
        # Adjust for sentiment strength
        sentiment_strength = sentiment_confidence - 0.5
        if sentiment == 'positive':
            energy += sentiment_strength * 1.5
        elif sentiment == 'negative':
            energy -= sentiment_strength * 1.5
        else:  # neutral
            energy += (sentiment_strength * 0.5)
        
        # Apply energy modifiers from keywords
        modifier_total = 0
        modifier_count = 0
        
        for keyword, modifier in self.energy_modifiers.items():
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.findall(pattern, text_lower)
            if matches:
                modifier_total += modifier * len(matches)
                modifier_count += len(matches)
        
        # Average the modifiers
        if modifier_count > 0:
            average_modifier = modifier_total / modifier_count
            energy += average_modifier
        
        # Ensure energy stays within mood's typical range
        min_energy, max_energy = mood_data.get('energy_range', (3, 8))
        energy = max(min_energy, min(max_energy, energy))
        
        # Round to nearest 0.5 for cleaner output
        energy = round(energy * 2) / 2
        
        return energy

    def analyze_mood(self, text):
        if not text or not text.strip():
            return {
                "mood": "neutral",
                "mood_confidence": 0.5,
                "sentiment": "neutral",
                "sentiment_confidence": 0.5,
                "energy_level": 5.0
            }
        
        try:
            sentiment, sentiment_confidence = self.analyze_sentiment(text)
            mood, mood_confidence = self.detect_mood(text)
            energy_level = self.calculate_energy(text, sentiment, sentiment_confidence, mood)
            
            print(f"📝 Input: {text}")
            print(f"🎭 Sentiment: {sentiment} (confidence: {sentiment_confidence:.2f})")
            print(f"🔍 Mood scores: {dict(self.get_mood_scores(text))}")
            print(f"🎯 Detected mood: {mood} (confidence: {mood_confidence:.2f})")
            print(f"⚡ Energy level: {energy_level}/10")
            print("-" * 50)
            
            return {
                "mood": mood,
                "mood_confidence": round(mood_confidence, 2),
                "sentiment": sentiment,
                "sentiment_confidence": round(sentiment_confidence, 2),
                "energy_level": energy_level
            }
            
        except Exception as e:
            print(f"Error in mood analysis: {e}")
            return {
                "mood": "neutral",
                "mood_confidence": 0.5,
                "sentiment": "neutral",
                "sentiment_confidence": 0.5,
                "energy_level": 5.0
            }
    
    def get_mood_scores(self, text):
        text_lower = text.lower()
        mood_scores = defaultdict(float)
        
        for mood, mood_data in self.mood_keywords.items():
            for keyword in mood_data['keywords']:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, text_lower)
                if matches:
                    mood_scores[mood] += len(matches)
        
        return mood_scores

# Test with your specific examples
def test_specific_cases():
    analyzer = MoodAnalyzer()
    
    test_cases = [
        "I feel sad and lonely today...",
        "I need calm music for studying and focus",
        "I love you so much my darling",
        "I'm so happy and excited for the weekend!",
        "I'm pumped and energetic for my workout!",
        "This mystery novel has me intrigued and curious"
    ]
    
    for test_text in test_cases:
        result = analyzer.analyze_mood(test_text)
        print(f"Result: {result}")
        print()

if __name__ == "__main__":
    test_specific_cases()