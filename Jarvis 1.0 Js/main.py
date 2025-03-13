from flask import Flask, render_template, jsonify, request
import threading
import time
import os,sys
import datetime
import pyttsx3
import speech_recognition
import requests
import pyautogui
from bs4 import BeautifulSoup
import random
import webbrowser
import speedtest
import pyjokes
from plyer import notification
from pygame import mixer

app = Flask(__name__, static_folder='static')

# Global variables to track state
busy = False
last_response = "Click here to speak"
listening_active = False
processing_thread = None

# Initialize text-to-speech engine
engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 170)

def speak(audio):
    global last_response
    last_response = audio
    engine.say(audio)
    engine.runAndWait()

def takeCommand():
    r = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:
        print("Listening.....")
        r.pause_threshold = 1
        r.energy_threshold = 300
        audio = r.listen(source, 0, 4)

    try:
        print("Understanding..")
        query = r.recognize_google(audio, language='en-in')
        print(f"User Said: {query}\n")
        return query.lower()
    except Exception as e:
        print("Say that again")
        return "none"

def alarm(query):
    timehere = open("Alarmtext.txt","a")
    timehere.write(query)
    timehere.close()
    os.startfile("alarm.py")

def process_command(query):
    global busy, last_response, listening_active
    
    busy = True
    
    try:
        if "wake up" in query:
            speak("I am awake and ready to assist you")
            
        elif "go to sleep" in query or "stop listening" in query:
            speak("Stopping continuous listening mode")
            listening_active = False
            
        elif "finally sleep" in query:
            speak("Going to sleep, sir")
            listening_active = False
            sys.exit()
            
        elif "hello" in query:
            speak("Hello, how are you?")
            
        elif "how are you" in query:
            speak("I'm doing well, thank you for asking")
            
        elif "joke" in query:
            joke = pyjokes.get_joke()
            speak(joke)
            
        elif "translate" in query:
            from Translator import translategl
            query = query.replace("jarvis","")
            query = query.replace("translate","")
            translategl(query)

        elif "play a game" in query:
            from game import game_play
            game_play()

        elif "open" in query:   
            query = query.replace("open","")
            query = query.replace("jarvis","")
            pyautogui.press("super")
            pyautogui.typewrite(query)
            pyautogui.sleep(2)
            pyautogui.press("enter")  

        elif "volume up" in query:
            from keyboard import volumeup
            speak("Turning volume up, sir")
            volumeup()
            
        elif "volume down" in query:
            from keyboard import volumedown
            speak("Turning volume down, sir")
            volumedown()

        elif "google" in query:
            from SearchNow import searchGoogle
            searchGoogle(query)
            
        elif "youtube" in query:
            from SearchNow import searchYoutube
            searchYoutube(query)
            
        elif "wikipedia" in query:
            from SearchNow import searchWikipedia
            searchWikipedia(query)
            
        elif "news" in query:
            from NewsRead import latestnews
            latestnews()

        elif "vedar" in query:
            city = "Gandhinagar"
            from whether import fetch_weather
            fetch_weather(city)
            
        elif "temperature" in query:
            search = "temperature in Gandhinagar"
            url = f"https://www.google.com/search?q={search}"
            r = requests.get(url)
            data = BeautifulSoup(r.text, "html.parser")
            temp = data.find("div", class_ = "BNeawe").text
            speak(f"current{search} is {temp}")

        elif "set an alarm" in query:
            print("input time example:- 10 and 10 and 10")
            speak("Set the time")
            a = input("Please tell the time :- ")
            alarm(a)
            speak("Done, sir")

        elif "time" in query:
            strTime = datetime.datetime.now().strftime("%H:%M")    
            speak(f"Sir, {strTime} is the time")
            
        elif "schedule my day" in query:
            tasks = [] #Empty list 
            speak("Do you want to clear old tasks (Plz speak YES or NO)")
            query = takeCommand().lower()
            if "yes" in query:
                file = open("tasks.txt","w")
                file.write(f"")
                file.close()
                no_tasks = int(input("Enter the no. of tasks :- "))
                i = 0
                for i in range(no_tasks):
                    tasks.append(input("Enter the task :- "))
                    file = open("tasks.txt","a")
                    file.write(f"{i}. {tasks[i]}\n")
                    file.close()
            elif "no" in query:
                i = 0
                no_tasks = int(input("Enter the no. of tasks :- "))
                for i in range(no_tasks):
                    tasks.append(input("Enter the task :- "))
                    file = open("tasks.txt","a")
                    file.write(f"{i}. {tasks[i]}\n")
                    file.close()

        elif "show my schedule" in query:
            file = open("tasks.txt","r")
            content = file.read()
            file.close()
            mixer.init()
            mixer.music.load("notification.wav")
            mixer.music.play()
            notification.notify(
                title = "My schedule :-",
                message = content,
                timeout = 15
            )
            
        elif "remember that" in query:
            rememberMessage = query.replace("remember that","")
            rememberMessage = query.replace("jarvis","")
            speak("You told me to remember that"+rememberMessage)
            remember = open("Remember.txt","a")
            remember.write(rememberMessage)
            remember.close()
            
        elif "what do you remember" in query:
            remember = open("Remember.txt","r")
            speak("You told me to remember that" + remember.read())

        elif "internet speed" in query:
            wifi = speedtest.Speedtest()
            upload_net = wifi.upload()/1048576         #Megabyte = 1024*1024 Bytes
            download_net = wifi.download()/1048576
            print("Wifi download speed is ",download_net)
            print("Wifi Upload Speed is", upload_net)
            speak(f"Wifi download speed is {download_net}")
            speak(f"Wifi Upload speed is {upload_net}")

        elif "shut down the system" in query:
            speak("Are You sure you want to shutdown")
            shutdown = input("Do you wish to shutdown your computer? (yes/no)")
            if shutdown == "yes":
                os.system("shutdown /s /t 1")
            elif shutdown == "no":
                exit
               
        elif "screenshot" in query:
            import pyautogui
            im = pyautogui.screenshot()
            im.save("ss2.jpg")

        elif "click my photo" in query:
            pyautogui.press("super")
            pyautogui.typewrite("camera")
            pyautogui.press("enter")
            pyautogui.sleep(2)
            speak("SMILE")
            pyautogui.press(" ")
            
        else:
            speak("I'm not sure how to help with that yet")
    
    except Exception as e:
        print(f"Error processing command: {e}")
        speak("I encountered an error while processing your request")
    
    finally:
        busy = False

def continuous_listening():
    global busy, listening_active
    
    while listening_active:
        if not busy:
            query = takeCommand()
            if query != "none":
                process_command(query)
        time.sleep(0.1)  # Small delay to prevent CPU overuse

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_listening', methods=['POST'])
def start_listening():
    global busy, processing_thread, listening_active
    
    if busy:
        return jsonify({"status": "error", "message": "Assistant is busy"})
    
    listening_active = True
    
    if processing_thread is None or not processing_thread.is_alive():
        processing_thread = threading.Thread(target=continuous_listening)
        processing_thread.daemon = True
        processing_thread.start()
        speak("Continuous listening mode activated")
    
    return jsonify({"status": "success", "message": "Continuous listening started"})

@app.route('/stop_listening', methods=['POST'])
def stop_listening():
    global listening_active
    
    listening_active = False
    speak("Continuous listening mode deactivated")
    
    return jsonify({"status": "success", "message": "Continuous listening stopped"})

@app.route('/check_status')
def check_status():
    global busy, last_response, listening_active
    return jsonify({
        "status": "success",
        "busy": busy,
        "last_response": last_response,
        "listening_active": listening_active
    })

if __name__ == "__main__":
    # Welcome message on server start
    print("JARVIS Web Assistant is running")
    app.run(debug=True, port=5000)