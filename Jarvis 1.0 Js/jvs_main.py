from flask import Flask, render_template, jsonify, request
import os
import datetime
import pyttsx3
import speech_recognition as sr
import webbrowser
import subprocess
import threading
import pyautogui
import requests
from bs4 import BeautifulSoup
import random
import speedtest
import pyjokes
from plyer import notification
from pygame import mixer

app = Flask(__name__, template_folder='templates', static_folder='static')

engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 170)


class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1
        self.recognizer.energy_threshold = 300

    def speak(self, text):
        print(f"Assistant: {text}")
        engine.say(text)
        engine.runAndWait()
        return text

    def take_command(self):
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            print("Understanding...")
            query = self.recognizer.recognize_google(audio, language='en-in')
            print(f"You Said: {query}\n")
            return query.lower()
        except sr.WaitTimeoutError:
            return "timeout"
        except sr.UnknownValueError:
            return "none"
        except Exception as e:
            print(f"Error: {str(e)}")
            return "error"

    def process_commands(self, query):
        if query in ["none", "error"]:
            return ["Sorry, I didn't catch that. Please try again."]
        if query == "timeout":
            return ["I didn't hear anything. Please try again."]
        
        commands = query.split(" and ")  # Allow multiple commands separated by "and"
        responses = []
        
        for cmd in commands:
            cmd = cmd.strip()
            
            if "time" in cmd:
                time_str = datetime.datetime.now().strftime("%I:%M %p")
                responses.append(f"The current time is {time_str}")
            elif "date" in cmd:
                date_str = datetime.datetime.now().strftime("%B %d, %Y")
                responses.append(f"Today's date is {date_str}")
            elif "search for" in cmd or "google" in cmd:
                search_term = cmd.replace("search for", "").replace("google", "").strip()
                webbrowser.open(f"https://www.google.com/search?q={search_term}")
                responses.append(f"Searching for {search_term}")
            elif any(word in cmd for word in ["exit", "quit", "goodbye", "bye"]):
                responses.append("Goodbye! Click anywhere to speak again when you need me.")
            elif "i am fine" in cmd:
                responses.append("That's great, sir")
            elif "open" in cmd:
                app_name = cmd.replace("open", "").replace("jarvis", "").strip()
                pyautogui.press("super")
                pyautogui.typewrite(app_name)
                pyautogui.sleep(2)
                pyautogui.press("enter")
                responses.append(f"Opening {app_name}")
            elif "translate" in cmd:
                from Translator import translategl
                text_to_translate = cmd.replace("jarvis", "").replace("translate", "").strip()
                translategl(text_to_translate)
                responses.append(f"Translating: {text_to_translate}")
            elif "play a game" in cmd:
                from game import game_play
                game_play()
                responses.append("Starting a game")
            elif "hello" in cmd:
                responses.append("Hello sir, how are you?")
            elif "how r u" in cmd:
                responses.append("Perfect, sir")
            elif "thank u" in cmd:
                responses.append("You are welcome, sir")
            elif "tired" in cmd:
                responses.append("Playing your favourite songs, sir")
                song_choice = random.choice([1, 2, 3])
                if song_choice == 1:
                    webbrowser.open("https://www.youtube.com/watch?v=u2NAuswnTKs")
                elif song_choice == 2:
                    webbrowser.open("https://www.youtube.com/watch?v=DK_UsATwoxI")
                elif song_choice == 3:
                    webbrowser.open("https://www.youtube.com/watch?v=ImnYPjOd1Tw")
            elif "volume up" in cmd:
                from keyboard import volumeup
                volumeup()
                responses.append("Turning volume up, sir")
            elif "volume down" in cmd:
                from keyboard import volumedown
                volumedown()
                responses.append("Turning volume down, sir")
            elif "google" in cmd:
                from SearchNow import searchGoogle
                searchGoogle(cmd)
                responses.append(f"Searching Google for {cmd}")
            elif "youtube" in cmd:
                from SearchNow import searchYoutube
                searchYoutube(cmd)
                responses.append(f"Searching YouTube for {cmd}")
            elif "wikipedia" in cmd:
                from SearchNow import searchWikipedia
                searchWikipedia(cmd)
                responses.append(f"Searching Wikipedia for {cmd}")
            elif "news" in cmd:
                from NewsRead import latestnews
                latestnews()
                responses.append("Fetching the latest news")
            elif "temperature" in cmd or "weather" in cmd:
                search = "temperature in Gandhinagar"
                url = f"https://www.google.com/search?q={search}"
                r = requests.get(url)
                data = BeautifulSoup(r.text, "html.parser")
                temp = data.find("div", class_="BNeawe").text
                responses.append(f"Current {search} is {temp}")
            elif "set an alarm" in cmd:
                responses.append("Set the time")
                alarm_time = input("Please tell the time (e.g., 10:10:10): ")
                self.alarm(alarm_time)
                responses.append("Done, sir")
            elif "time" in cmd:
                current_time = datetime.datetime.now().strftime("%H:%M")
                responses.append(f"Sir, {current_time} is the time")
            elif "finally sleep" in cmd:
                responses.append("Going to sleep, sir")
                exit()
            elif "remember that" in cmd:
                remember_message = cmd.replace("remember that", "").replace("jarvis", "").strip()
                responses.append(f"You told me to remember that: {remember_message}")
                with open("Remember.txt", "a") as remember_file:
                    remember_file.write(remember_message + "\n")
            elif "what do you remember" in cmd:
                with open("Remember.txt", "r") as remember_file:
                    remembered_text = remember_file.read()
                    responses.append(f"You told me to remember that: {remembered_text}")
            elif "internet speed" in cmd:
                wifi = speedtest.Speedtest()
                upload_speed = wifi.upload() / 1048576  # Megabyte = 1024 * 1024 Bytes
                download_speed = wifi.download() / 1048576
                responses.append(f"Wifi download speed is {download_speed:.2f} Mbps")
                responses.append(f"Wifi upload speed is {upload_speed:.2f} Mbps")
            elif "shutdown the system" in cmd:
                responses.append("Are you sure you want to shutdown?")
                shutdown_confirmation = input("Do you wish to shutdown your computer? (yes/no): ")
                if shutdown_confirmation.lower() == "yes":
                    os.system("shutdown /s /t 1")
                else:
                    responses.append("Shutdown cancelled")
            elif "joke" in cmd:
                joke = pyjokes.get_joke()
                responses.append(joke)
            elif "screenshot" in cmd:
                screenshot = pyautogui.screenshot()
                screenshot.save("screenshot.png")
                responses.append("Screenshot saved as screenshot.png")
            elif "click my photo" in cmd:
                pyautogui.press("super")
                pyautogui.typewrite("camera")
                pyautogui.press("enter")
                pyautogui.sleep(2)
                responses.append("Smile!")
                pyautogui.press(" ")
            else:
                responses.append(f"I'm not sure how to help with '{cmd}'. Try asking me to search the web or tell you the time.")
        
        return responses


assistant = VoiceAssistant()

def process_voice_commands():
    query = assistant.take_command()
    responses = assistant.process_commands(query)
    for response in responses:
        assistant.speak(response)
    return responses

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_listening', methods=['POST'])
def start_listening():
    thread = threading.Thread(target=process_voice_commands)
    thread.daemon = True
    thread.start()
    return jsonify({'status': 'success', 'message': 'Listening started'})

@app.route('/process_text', methods=['POST'])
def process_text():
    data = request.json
    query = data.get('query', '')
    responses = assistant.process_commands(query)
    return jsonify({'status': 'success', 'responses': responses})

if __name__ == "__main__":
    app.run(debug=True)