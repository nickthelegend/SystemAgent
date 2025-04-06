from src.inference.gemini import ChatGemini
from src.agent.computer import ComputerAgent
from src.inference.google_speech import GoogleSpeechToText
from src.speech import Speech
from dotenv import load_dotenv
import os

load_dotenv()
google_api_key = "AIzaSyAd5C1JBKOS5ex8hyu-33-wAneu4TOeajc"
google_credentials_path = "eighth-feat-454609-u6-805d5f618312.json"

# Initialize Gemini for text processing
llm = ChatGemini(model='gemini-2.0-flash', api_key=google_api_key, temperature=0)

# Initialize Google Speech-to-Text for audio transcription
speech_to_text = GoogleSpeechToText(api_key=google_credentials_path, verbose=True)

# Initialize the Computer Agent
agent = ComputerAgent(llm=llm, use_vision=False, verbose=True, max_iteration=20)

mode = input('Enter the mode of input (text/voice): ')
if mode == 'text':
    user_query = input('Enter your query: ')
elif mode == 'voice':
    speech = Speech(llm=speech_to_text, verbose=True)    
    user_query = speech.invoke()
    print(f'Enter your query: {user_query.content}')
else:
    raise Exception('Invalid mode of input. Please enter either text or voice.')

agent_response = agent.invoke(user_query)
print(agent_response)

