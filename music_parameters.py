# music_parameters.py
from config import Config

class MusicParameters:
    def __init__(self):
        # Mood to music parameter mappings
        self.mood_mappings = {
            'happy': {
                'tempo': 120,
                'key': 'C',
                'scale': 'major',
                'dynamics': 'mezzo-forte',
                'instruments': ['piano', 'violin', 'flute', 'acoustic guitar', 'mandolin', 'celesta'],
                'complexity': 'medium',
                'energy_level': 8,
                'description': 'upbeat cheerful joyful positive uplifting'
            },
            'sad': {
                'tempo': 60,
                'key': 'D',
                'scale': 'minor',
                'dynamics': 'piano',
                'instruments': ['cello', 'piano', 'harp', 'viola', 'english horn', 'glass harmonica'],
                'complexity': 'low',
                'energy_level': 3,
                'description': 'melancholic sorrowful emotional reflective'
            },
            'calm': {
                'tempo': 80,
                'key': 'G',
                'scale': 'major',
                'dynamics': 'piano',
                'instruments': ['harp', 'flute', 'strings', 'piano', 'wind chimes', 'ambient pad'],
                'complexity': 'low',
                'energy_level': 4,
                'description': 'peaceful relaxing ambient soothing tranquil'
            },
            'energetic': {
                'tempo': 140,
                'key': 'F',
                'scale': 'major',
                'dynamics': 'forte',
                'instruments': ['drums', 'electric guitar', 'trumpet', 'saxophone', 'bass guitar', 'tambourine'],
                'complexity': 'high',
                'energy_level': 9,
                'description': 'energetic powerful driving intense exciting'
            },
            'mysterious': {
                'tempo': 90,
                'key': 'E',
                'scale': 'minor',
                'dynamics': 'mezzo-piano',
                'instruments': ['cello', 'bassoon', 'harp', 'theremin', 'vibraphone', 'waterphone'],
                'complexity': 'medium',
                'energy_level': 6,
                'description': 'mysterious suspenseful enigmatic atmospheric'
            },
            'romantic': {
                'tempo': 100,
                'key': 'A',
                'scale': 'major',
                'dynamics': 'mezzo-piano',
                'instruments': ['violin', 'piano', 'cello', 'french horn', 'clarinet', 'harp'],
                'complexity': 'medium',
                'energy_level': 7,
                'description': 'romantic loving passionate emotional tender'
            },
            'neutral': {
                'tempo': 100,
                'key': 'C',
                'scale': 'major',
                'dynamics': 'mezzo-piano',
                'instruments': ['piano', 'acoustic guitar', 'strings', 'flute', 'soft synth', 'xylophone'],
                'complexity': 'medium',
                'energy_level': 5,
                'description': 'balanced neutral pleasant background'
            }
        }

    def get_music_parameters(self, mood_analysis):
        mood = mood_analysis.get('mood', 'neutral')
        energy_level = mood_analysis.get('energy_level', 5)

        # Get base parameters for the mood
        params = self.mood_mappings.get(mood, self.mood_mappings['neutral']).copy()

        # Adjust tempo based on energy level
        energy_factor = energy_level / 10
        params['tempo'] = int(params['tempo'] * (0.8 + 0.4 * energy_factor))

        # Adjust dynamics based on energy
        if energy_level >= 8:
            params['dynamics'] = 'forte'
        elif energy_level >= 6:
            params['dynamics'] = 'mezzo-forte'
        elif energy_level >= 4:
            params['dynamics'] = 'mezzo-piano'
        else:
            params['dynamics'] = 'piano'

        # Update energy level in params
        params['energy_level'] = energy_level

        # Generate a text prompt for MusicGen based on parameters
        params['musicgen_prompt'] = self._generate_musicgen_prompt(params)

        return params

    def _generate_musicgen_prompt(self, params):
        """Generate a text prompt for MusicGen based on musical parameters."""
        # Select top 2-3 instruments for the prompt
        instruments = params['instruments'][:3] if len(params['instruments']) > 2 else params['instruments']

        prompt_parts = [
            params['description'],
            f"{params['tempo']} bpm",
            f"{params['key']} {params['scale']}",
            f"with {', '.join(instruments)}",
            params['dynamics'] + " dynamics"
        ]

        return ", ".join(prompt_parts)
