from google.cloud import texttospeech
import pygame
import os
import tempfile
import time
import re

class TextToSpeech:
    def __init__(self, credentials_path=None, language_code="en-US", voice_name="en-US-Neural2-F", verbose=False):
        """
        Initialize the TextToSpeech class.
        
        Args:
            credentials_path: Path to Google Cloud credentials JSON file
            language_code: Language code for the voice
            voice_name: Name of the voice to use
            verbose: Whether to print debug information
        """
        self.language_code = language_code
        self.voice_name = voice_name
        self.verbose = verbose
        
        # Set credentials if provided
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            
        # Initialize pygame for audio playback
        pygame.mixer.init()
        
        # Create the client
        self.client = texttospeech.TextToSpeechClient()
        
        # Configure voice selection
        self.voice = texttospeech.VoiceSelectionParams(
            language_code=self.language_code,
            name=self.voice_name
        )
        
        # Configure audio config
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.1  # Slightly faster than normal
        )
        
    def clean_text(self, text):
        """
        Clean text for better speech output.
        
        Args:
            text: The text to clean
        
        Returns:
            Cleaned text
        """
        # Remove ANSI color codes
        text = re.sub(r'\x1b\[[0-9;]*m', '', text)
        
        # Remove URLs for better speech
        text = re.sub(r'https?://\S+', 'URL', text)
        
        # Replace special characters
        text = text.replace('```', '')
        
        return text
            
    def speak(self, text):
        """
        Convert text to speech and play it.
        
        Args:
            text: The text to convert to speech
        """
        if not text:
            return
        
        # Clean the text
        text = self.clean_text(text)
            
        if self.verbose:
            print(f"Speaking: {text[:50]}..." if len(text) > 50 else f"Speaking: {text}")
            
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        try:
            # Perform the text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice,
                audio_config=self.audio_config
            )
            
            # Create a temporary file to store the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(response.audio_content)
                temp_file_path = temp_file.name
                
            # Play the audio
            pygame.mixer.music.load(temp_file_path)
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
        except Exception as e:
            if self.verbose:
                print(f"Error in text-to-speech: {str(e)}")

