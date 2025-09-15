import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import librosa
import librosa.display
import io
from scipy import signal
from config import Config
import streamlit as st

class AudioVisualizer:
    def __init__(self):
        # Custom color schemes for different moods
        self.color_schemes = {
            'happy': ['#FFEB3B', '#FF9800', '#FF5722'],  # Yellow, Orange, Red
            'sad': ['#3F51B5', '#2196F3', '#03A9F4'],    # Blue, Light Blue
            'calm': ['#4CAF50', '#8BC34A', '#CDDC39'],   # Green, Light Green
            'energetic': ['#F44336', '#E91E63', '#9C27B0'],  # Red, Pink, Purple
            'mysterious': ['#673AB7', '#9C27B0', '#E91E63'], # Purple, Magenta
            'romantic': ['#E91E63', '#F44336', '#FF9800'],   # Pink, Red, Orange
            'neutral': ['#607D8B', '#9E9E9E', '#795548']     # Gray, Brown
        }
        
        # Set matplotlib style
        plt.style.use('dark_background')
    
    def create_waveform_plot(self, audio_array, sampling_rate, mood='neutral', title="Waveform"):
        """Create a waveform visualization of the audio"""
        # Create figure with custom size
        fig, ax = plt.subplots(figsize=(10, 4), facecolor='black')
        
        # Get color scheme based on mood
        colors = self.color_schemes.get(mood, self.color_schemes['neutral'])
        
        # Create time array
        time = np.linspace(0, len(audio_array) / sampling_rate, num=len(audio_array))
        
        # Plot waveform with gradient colors
        ax.plot(time, audio_array, color=colors[0], alpha=0.8, linewidth=1.5)
        
        # Fill under the waveform with gradient
        ax.fill_between(time, audio_array, color=colors[0], alpha=0.3)
        
        # Customize plot
        ax.set_title(title, fontsize=16, fontweight='bold', color='white')
        ax.set_xlabel('Time (seconds)', fontsize=12, color='white')
        ax.set_ylabel('Amplitude', fontsize=12, color='white')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, time[-1])
        
        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        plt.tight_layout()
        return fig
    
    def create_spectrogram(self, audio_array, sampling_rate, mood='neutral', title="Spectrogram"):
        """Create a spectrogram visualization of the audio"""
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 4), facecolor='black')
        
        # Get color scheme based on mood
        colors = self.color_schemes.get(mood, self.color_schemes['neutral'])
        
        # Create custom colormap
        cmap = LinearSegmentedColormap.from_list('mood_cmap', colors, N=256)
        
        # Compute spectrogram
        frequencies, times, spectrogram = signal.spectrogram(
            audio_array, 
            sampling_rate, 
            nperseg=1024, 
            noverlap=512
        )
        
        # Plot spectrogram
        im = ax.pcolormesh(times, frequencies, 10 * np.log10(spectrogram + 1e-10), 
                          shading='gouraud', cmap=cmap, alpha=0.8)
        
        # Customize plot
        ax.set_title(title, fontsize=16, fontweight='bold', color='white')
        ax.set_xlabel('Time (seconds)', fontsize=12, color='white')
        ax.set_ylabel('Frequency (Hz)', fontsize=12, color='white')
        ax.set_ylim(0, 5000)  # Limit frequency range for better visualization
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Intensity (dB)', color='white')
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
        
        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        plt.tight_layout()
        return fig
    
    def create_mel_spectrogram(self, audio_array, sampling_rate, mood='neutral', title="Mel Spectrogram"):
        """Create a Mel spectrogram visualization"""
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 4), facecolor='black')
        
        # Get color scheme based on mood
        colors = self.color_schemes.get(mood, self.color_schemes['neutral'])
        
        # Create custom colormap
        cmap = LinearSegmentedColormap.from_list('mood_cmap', colors, N=256)
        
        # Compute Mel spectrogram
        mel_spectrogram = librosa.feature.melspectrogram(
            y=audio_array, 
            sr=sampling_rate, 
            n_fft=2048, 
            hop_length=512, 
            n_mels=128
        )
        mel_spectrogram_db = librosa.power_to_db(mel_spectrogram, ref=np.max)
        
        # Display Mel spectrogram
        img = librosa.display.specshow(
            mel_spectrogram_db, 
            sr=sampling_rate, 
            hop_length=512, 
            x_axis='time', 
            y_axis='mel', 
            ax=ax, 
            cmap=cmap
        )
        
        # Customize plot
        ax.set_title(title, fontsize=16, fontweight='bold', color='white')
        ax.set_xlabel('Time (seconds)', fontsize=12, color='white')
        ax.set_ylabel('Frequency (Hz)', fontsize=12, color='white')
        
        # Add colorbar
        cbar = plt.colorbar(img, ax=ax, format='%+2.0f dB')
        cbar.set_label('dB', color='white')
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
        
        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        plt.tight_layout()
        return fig
    
    def create_combined_visualization(self, audio_array, sampling_rate, mood='neutral', title="Audio Analysis"):
        """Create a combined visualization with waveform and spectrogram"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), facecolor='black')
        
        # Get color scheme based on mood
        colors = self.color_schemes.get(mood, self.color_schemes['neutral'])
        
        # Create custom colormap
        cmap = LinearSegmentedColormap.from_list('mood_cmap', colors, N=256)
        
        # Waveform plot
        time = np.linspace(0, len(audio_array) / sampling_rate, num=len(audio_array))
        ax1.plot(time, audio_array, color=colors[0], alpha=0.8, linewidth=1.5)
        ax1.fill_between(time, audio_array, color=colors[0], alpha=0.3)
        ax1.set_title(f'{title} - Waveform', fontsize=14, fontweight='bold', color='white')
        ax1.set_ylabel('Amplitude', fontsize=12, color='white')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(0, time[-1])
        
        # Spectrogram plot
        frequencies, times, spectrogram = signal.spectrogram(
            audio_array, 
            sampling_rate, 
            nperseg=1024, 
            noverlap=512
        )
        im = ax2.pcolormesh(times, frequencies, 10 * np.log10(spectrogram + 1e-10), 
                           shading='gouraud', cmap=cmap, alpha=0.8)
        ax2.set_title('Spectrogram', fontsize=14, fontweight='bold', color='white')
        ax2.set_xlabel('Time (seconds)', fontsize=12, color='white')
        ax2.set_ylabel('Frequency (Hz)', fontsize=12, color='white')
        ax2.set_ylim(0, 5000)
        
        # Add colorbar to spectrogram
        cbar = plt.colorbar(im, ax=ax2)
        cbar.set_label('Intensity (dB)', color='white')
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
        
        # Remove spines from both plots
        for ax in [ax1, ax2]:
            for spine in ax.spines.values():
                spine.set_visible(False)
        
        plt.tight_layout()
        return fig
    
    def create_real_time_visualizer(self, audio_array, sampling_rate, mood='neutral'):
        """Create a real-time visualizer effect (simulated)"""
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='black')
        
        # Get color scheme based on mood
        colors = self.color_schemes.get(mood, self.color_schemes['neutral'])
        
        # Create a simulated real-time effect with multiple frequency bands
        n_bands = 8
        band_heights = np.random.random(n_bands) * 0.8 + 0.2
        
        # Create bars with gradient colors
        bars = ax.bar(range(n_bands), band_heights, color=colors[0], alpha=0.8)
        
        # Add gradient effect to bars
        for i, bar in enumerate(bars):
            color_idx = int(i / n_bands * len(colors))
            bar.set_color(colors[color_idx % len(colors)])
            bar.set_alpha(0.7 + 0.3 * (i / n_bands))
        
        # Customize plot
        ax.set_title('Real-time Audio Visualizer', fontsize=16, fontweight='bold', color='white')
        ax.set_ylim(0, 1)
        ax.set_xlim(-0.5, n_bands - 0.5)
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Add glow effect
        for bar in bars:
            bar.set_edgecolor('white')
            bar.set_linewidth(0.5)
        
        # Remove spines and background
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_facecolor('black')
        
        plt.tight_layout()
        return fig
    
    def plot_to_streamlit(self, fig):
        """Convert matplotlib figure to Streamlit-compatible format"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='black')
        buf.seek(0)
        plt.close(fig)  # Close the figure to free memory
        return buf
    
    def display_audio_visualizations(self, audio_array, sampling_rate, mood='neutral', title="Generated Music"):
        """Display all audio visualizations in Streamlit"""
        if audio_array is None:
            st.warning("No audio data available for visualization")
            return
        
        # Create tabs for different visualizations
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Waveform", "Spectrogram", "Mel Spectrogram", "Combined", "Real-time"
        ])
        
        with tab1:
            fig = self.create_waveform_plot(audio_array, sampling_rate, mood, f"{title} - Waveform")
            st.image(self.plot_to_streamlit(fig), use_column_width=True)
        
        with tab2:
            fig = self.create_spectrogram(audio_array, sampling_rate, mood, f"{title} - Spectrogram")
            st.image(self.plot_to_streamlit(fig), use_column_width=True)
        
        with tab3:
            fig = self.create_mel_spectrogram(audio_array, sampling_rate, mood, f"{title} - Mel Spectrogram")
            st.image(self.plot_to_streamlit(fig), use_column_width=True)
        
        with tab4:
            fig = self.create_combined_visualization(audio_array, sampling_rate, mood, title)
            st.image(self.plot_to_streamlit(fig), use_column_width=True)
        
        with tab5:
            fig = self.create_real_time_visualizer(audio_array, sampling_rate, mood)
            st.image(self.plot_to_streamlit(fig), use_column_width=True)
            
            # Add a note about the real-time visualization
            st.info("""
            **Note:** This is a simulated real-time visualization. 
            In a real application, this would update in real-time as the audio plays.
            """)

# Example usage and testing
if __name__ == "__main__":
    # Test the audio visualizer
    visualizer = AudioVisualizer()
    
    # Generate test audio data
    sampling_rate = 44100
    duration = 3  # seconds
    t = np.linspace(0, duration, int(sampling_rate * duration))
    
    # Create test audio with multiple frequencies
    audio_data = 0.5 * np.sin(2 * np.pi * 440 * t)  # A4 note
    audio_data += 0.3 * np.sin(2 * np.pi * 880 * t)  # A5 note
    audio_data += 0.2 * np.sin(2 * np.pi * 1320 * t)  # E6 note
    
    # Normalize audio
    audio_data = audio_data / np.max(np.abs(audio_data))
    
    print("Testing Audio Visualizer with different moods...")
    
    # Test with different moods
    test_moods = ['happy', 'sad', 'calm', 'energetic', 'mysterious', 'romantic']
    
    for mood in test_moods:
        print(f"Testing {mood} mood visualization...")
        
        # Create and save visualizations
        fig_waveform = visualizer.create_waveform_plot(audio_data, sampling_rate, mood, f"Test - {mood.capitalize()}")
        fig_waveform.savefig(f"waveform_{mood}.png", dpi=100, bbox_inches='tight')
        
        fig_spectrogram = visualizer.create_spectrogram(audio_data, sampling_rate, mood, f"Test - {mood.capitalize()}")
        fig_spectrogram.savefig(f"spectrogram_{mood}.png", dpi=100, bbox_inches='tight')
        
        plt.close('all')  # Close all figures
    
    print("Test completed! Check the generated PNG files.")