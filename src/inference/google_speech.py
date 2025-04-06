from google.cloud.speech_v1 import SpeechClient
from google.cloud.speech_v1.types import RecognitionAudio, RecognitionConfig
import io
import os
from src.message import AIMessage

class GoogleSpeechToText:
    """
    A class to handle Google Speech-to-Text API for audio transcription.
    """
    
    def __init__(self, api_key=None, language_code="en-US", verbose=False):
        """
        Initialize the Google Speech-to-Text client.
        
        Args:
            api_key (str, optional): Path to Google credentials JSON file. Defaults to None.
            language_code (str, optional): Language code for transcription. Defaults to "en-US".
            verbose (bool, optional): Whether to print verbose output. Defaults to False.
        """
        if api_key:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = api_key
        
        self.client = SpeechClient()
        self.language_code = language_code
        self.verbose = verbose
        
        # Add model attribute for compatibility with Speech class
        self.model = "google-speech-to-text"
    
    def transcribe_audio(self, audio_content):
        """
        Transcribe audio content using Google Speech-to-Text API.
        
        Args:
            audio_content (bytes): Audio content to transcribe.
            
        Returns:
            dict: A dictionary containing the transcription result.
        """
        if self.verbose:
            print("Transcribing audio with Google Speech-to-Text...")
        
        audio = RecognitionAudio(content=audio_content)
        config = RecognitionConfig(
            encoding=RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=44100,
            language_code=self.language_code,
            enable_automatic_punctuation=True,
        )
        
        response = self.client.recognize(config=config, audio=audio)
        
        # Extract the transcription from the response
        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript
        
        if self.verbose:
            print(f"Transcription complete: {transcript}")
        
        # Return in a format compatible with the existing code
        return {"content": transcript}
    
    def invoke(self, file_path=None, messages=None, json=False, model=None):
        """
        Invoke the transcription service.
        
        Args:
            file_path (str, optional): Path to the audio file to transcribe.
            messages (list, optional): Not used for speech-to-text.
            json (bool, optional): Not used for speech-to-text.
            model (BaseModel, optional): Not used for speech-to-text.
            
        Returns:
            AIMessage: An AIMessage containing the transcription result.
        """
        if file_path:
            if self.verbose:
                print(f"Reading audio file from {file_path}")
            
            # Read the audio file
            with open(file_path, 'rb') as audio_file:
                audio_content = audio_file.read()
            
            # Transcribe the audio
            result = self.transcribe_audio(audio_content)
            
            # Return an AIMessage with the transcription
            return AIMessage(content=result["content"])
        
        # If no file_path is provided, return an empty message
        return AIMessage(content="")

