from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QTextEdit, QGraphicsDropShadowEffect, QVBoxLayout
from ui.thread import SpeechThread, AgentThread
from PyQt6.QtGui import QIcon, QColor, QCursor
from PyQt6.QtCore import Qt, QEvent
import sys
import os
import re
sys.path.append(os.path.dirname(__file__))
from src.agent.computer import ComputerAgent
from src.speech import Speech

class ChatUI(QWidget):
    def __init__(self, agent:ComputerAgent=None, speech:Speech=None):
        self.agent = agent
        self.speech = speech
        self.is_recording = False
        self.speech_thread = None
        self.agent_thread = None
        super().__init__()

        self.setWindowTitle("Computer Agent")
        self.setFixedSize(470, 80)  # ✅ Set window size slightly larger for shadow effect
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # ✅ Move to top center
        screen = QApplication.primaryScreen().size()
        x = (screen.width() - self.width()) // 2
        y = -8  # Keep close to top
        self.move(x, y)

        # ✅ Create the main container (with rounded borders)
        self.container = QWidget(self)
        self.container.setFixedSize(450, 45)  # ✅ Slightly smaller than window for padding

        # ✅ Apply Drop Shadow to the container
        self.add_shadow()

        # ✅ Layout inside the container
        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)  # ✅ No margins
        layout.setSpacing(0)  # ✅ No spacing between widgets

        # ✅ Mic Button
        self.mic_button = QPushButton()
        self.mic_button.setFixedSize(40, 45)
        self.mic_button.setIcon(QIcon("./ui/assets/mic.svg"))
        self.mic_button.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0;
                border: none;
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
            }
            QPushButton:hover {
                background-color: #CBD5E1;
            }
        """)
        self.mic_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.mic_button.clicked.connect(self.on_mic_clicked)

        # ✅ Text Input (No border, No extra padding)
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Press and hold SPACE to record...")
        self.text_input.setFixedHeight(45)
        self.text_input.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_input.setStyleSheet("""
            QTextEdit {
                background-color: #F1F5F9;
                border: none;
                font-size: 16px;
                font-family: 'Segoe UI', sans-serif;
                color: #1E293B;
                padding: 6px;
                margin: 0;
                outline: none;
            }
            QTextEdit:focus {
                outline: none;
            }
        """)
        self.text_input.textChanged.connect(self.on_text_changed)
        # Override keyPressEvent for the existing QTextEdit instance
        self.text_input.keyPressEvent = self.handle_text_key_press
        self.text_input.keyReleaseEvent = self.handle_text_key_release
        
        # Install event filter to capture space bar events
        self.text_input.installEventFilter(self)

        # ✅ Send Button
        self.send_button = QPushButton()
        self.send_button.setFixedSize(40, 45)
        self.send_button.setIcon(QIcon("./ui/assets/send.svg"))
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0;
                border: none;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QPushButton:hover {
                background-color: #CBD5E1;
            }
        """)
        self.send_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.send_button.clicked.connect(self.on_send_clicked)

        # ✅ Add widgets inside the container
        layout.addWidget(self.mic_button)
        layout.addWidget(self.text_input, 1)  # Expand text input
        layout.addWidget(self.send_button)

        # ✅ Center container inside main window
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)  # ✅ Space for shadow
        main_layout.addWidget(self.container)
        
        # Set focus to text input by default
        self.text_input.setFocus()

    def eventFilter(self, obj, event):
        # Filter out space key events from being processed by the text input
        if obj == self.text_input and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Space:
                # Don't add space to the text input when used for recording
                return True
        return super().eventFilter(obj, event)
        
    def handle_text_key_press(self, event):
        # Start recording when space is pressed
        if event.key() == Qt.Key.Key_Space and not self.is_recording:
            self.start_recording()
            return  # Don't process the space key further
        elif event.key() == Qt.Key.Key_Return and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.on_send_clicked()
        else:
            # Default handling for other keys
            QTextEdit.keyPressEvent(self.text_input, event)
            
    def handle_text_key_release(self, event):
        # Stop recording when space is released
        if event.key() == Qt.Key.Key_Space and self.is_recording:
            self.stop_recording()
            return  # Don't process the space key further
        else:
            # Default handling for other keys
            QTextEdit.keyReleaseEvent(self.text_input, event)

    def start_recording(self):
        self.is_recording = True
        self.update_style(self.mic_button, "background-color", "#CBD5E1")
        self.speech.start_recording()
        self.text_input.setPlaceholderText('Recording... (release SPACE when done)')
        
    def stop_recording(self):
        self.is_recording = False
        self.update_style(self.mic_button, "background-color", "#E2E8F0")
        self.speech.stop_recording()
        self.speech_thread = SpeechThread(self.speech)
        self.speech_thread.start()
        self.speech_thread.finished.connect(self.on_speech_finished)
        self.text_input.setPlaceholderText('Processing...')

    def add_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 30))  # Black shadow with opacity
        self.container.setGraphicsEffect(shadow)  # ✅ Apply shadow to container
    
    def on_mic_clicked(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def on_speech_finished(self, content:str):
        content = content.strip()
        if len(content):
            self.text_input.setText(content)
            self.send_button.setDisabled(False)
            # Auto-submit if configured to do so
            self.on_send_clicked()
        else:
            self.send_button.setDisabled(True)
            self.text_input.setPlaceholderText('Press and hold SPACE to record...')

    def on_text_changed(self):
        if len(self.text_input.toPlainText().strip()):
            self.send_button.setDisabled(False)
        else:
            self.text_input.setPlaceholderText('Press and hold SPACE to record...')
            self.send_button.setDisabled(True)

    def on_send_clicked(self):
        query = self.text_input.toPlainText().strip()
        if query:
            self.text_input.setText('')
            self.text_input.setPlaceholderText('Executing Task...')
            self.text_input.setDisabled(True)
            self.agent_thread = AgentThread(self.agent, query)
            self.agent_thread.finished.connect(self.on_agent_finished)
            self.agent_thread.start()
        else:
            self.send_button.setDisabled(True)

    def on_agent_finished(self, content:str):
        self.text_input.setPlaceholderText("Press and hold SPACE to record...")
        self.text_input.setDisabled(False)
        print(content)

    def update_style(self, widget:QWidget, property_name:str, new_value:str):
        """Update a specific CSS property without removing others."""
        style = widget.styleSheet()
        
        # Check if the property exists
        if f"{property_name}:" in style:
            # Replace the existing property
            updated_style = re.sub(f"{property_name}:.*?;", f"{property_name}: {new_value};", style)
        else:
            # Append new property
            updated_style = style + f"\n{property_name}: {new_value};"

        widget.setStyleSheet(updated_style)
        
def launch_app(agent:ComputerAgent=None, speech:Speech=None):
    import ctypes
    myappid = u'mycompany.myproduct.subproduct.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QApplication([])
    app.setWindowIcon(QIcon('./ui/assets/icon.png'))
    window = ChatUI(agent=agent, speech=speech)
    window.show()
    app.exec()

