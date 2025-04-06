from src.inference.gemini import ChatGemini
from src.agent.computer import ComputerAgent
from src.inference.google_speech import GoogleSpeechToText
from src.speech import Speech
from src.speech.tts import TextToSpeech
from dotenv import load_dotenv
from ui import launch_app
import os

load_dotenv()
google_api_key = "AIzaSyAd5C1JBKOS5ex8hyu-33-wAneu4TOeajc"
google_credentials_path = "eighth-feat-454609-u6-805d5f618312.json"

# Initialize Gemini for text processing
llm = ChatGemini(model='gemini-2.0-flash', api_key=google_api_key, temperature=0)

# Initialize Google Speech-to-Text for audio transcription
speech_to_text = GoogleSpeechToText(api_key=google_credentials_path, verbose=True)

# Initialize Text-to-Speech
tts = TextToSpeech(
    credentials_path=google_credentials_path, 
    voice_name="en-US-Neural2-F",  # Female voice
    verbose=True
)

# Initialize Speech and Computer Agent
speech = Speech(llm=speech_to_text, verbose=True)
agent = ComputerAgent(
    llm=llm, 
    use_vision=True, 
    max_iteration=30, 
    verbose=True, 
    use_tts=True, 
    tts=tts
)

launch_app(agent=agent, speech=speech)

