from PyQt6.QtCore import Qt, QThread, pyqtSignal
import sys
import os
sys.path.append(os.path.dirname(__file__))
from src.agent.computer import ComputerAgent
from src.speech import Speech

class SpeechThread(QThread):
    finished = pyqtSignal(str)
    def __init__(self, speech:Speech=None):
        super().__init__()
        self.speech = speech

    def run(self):
        response = self.speech.process_audio()
        self.finished.emit(response.content)

class AgentThread(QThread):
    finished = pyqtSignal(str)
    def __init__(self, agent:ComputerAgent=None,query:str=''):
        super().__init__()
        self.agent = agent
        self.query=query

    def run(self):
        response = self.agent.invoke(self.query)
        self.finished.emit(response)