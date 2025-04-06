from src.inference import BaseInference
from pyaudio import PyAudio, paInt16, Stream
from tempfile import NamedTemporaryFile
from src.message import AIMessage
from typing import Literal
from threading import Thread
import keyboard
import wave
import os

class Speech:
    def __init__(self,llm: BaseInference = None,verbose=False):
        self.chunk_size = 1024
        self.frame_rate = 44100
        self.channels = 1
        self.audio = PyAudio()
        self.stream = None
        self.llm = llm
        self.tempfile_path = ''
        self.is_recording = False
        self.audio_bytes = None
        self.verbose=verbose

    def setup_stream(self):
        """Initialize the audio stream."""
        self.stream = self.audio.open(
            format=paInt16,
            channels=self.channels,
            rate=self.frame_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

    def get_stream(self) -> Stream:
        """Retrieve the current audio stream, initializing if necessary."""
        if self.stream is None:
            self.setup_stream()
        return self.stream

    def record_audio(self):
        """Run the recording process in a separate thread."""
        frames = []
        if self.verbose:
            print("Recording started...")
            print("Press Enter to stop recording...")
        while self.is_recording:
            data = self.stream.read(self.chunk_size)
            frames.append(data)
        self.audio_bytes = b''.join(frames)

    def start_recording(self):
        """Start the recording process in a separate thread."""
        if not self.is_recording:
            self.is_recording = True
            self.stream=self.get_stream()
            if not self.stream.is_active():
                self.stream.start_stream()
            self.recording_thread = Thread(target=self.record_audio, daemon=True)
            self.recording_thread.start()

    def stop_recording(self):
        """Stop the recording process."""
        if self.is_recording:
            if self.verbose:
                print("Recording stopped...")
            self.is_recording = False
            if self.recording_thread:
                self.recording_thread.join() # Ensure the recording thread finishes
                self.stream.stop_stream()

    def bytes_to_tempfile(self, audio_bytes: bytes):
        """Convert recorded bytes to a temporary WAV file."""
        temp_file = NamedTemporaryFile(delete=False, suffix='.wav')
        self.tempfile_path = temp_file.name
        temp_file.close()

        try:
            with wave.open(self.tempfile_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(paInt16))
                wf.setframerate(self.frame_rate)
                wf.writeframes(audio_bytes)
        except Exception as e:
            raise Exception(f"Export failed. {e}")

    def close(self):
        """Cleanup resources."""
        if self.stream is not None:
            self.stream.close()
        if self.audio is not None:
            self.audio.terminate()

    def process_audio(self) -> AIMessage:
        """Process recorded audio using the LLM model."""
        self.bytes_to_tempfile(self.audio_bytes)
        if self.verbose:
            print(f'Processing audio using {self.llm.model}...')
        response = self.llm.invoke(file_path=self.tempfile_path)
        if self.tempfile_path and os.path.exists(self.tempfile_path):
            os.remove(self.tempfile_path)
        return response

    def invoke(self) -> AIMessage:
        """Start and stop recording, then process audio."""
        self.start_recording()
        keyboard.wait('enter')  # Wait for Enter key press to stop
        self.stop_recording()
        response = self.process_audio()
        self.close()
        return response
