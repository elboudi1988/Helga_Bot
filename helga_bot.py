import openai
import speech_recognition as sr
from gtts import gTTS
from pygame import mixer
import tempfile
import os
from geopy.geocoders import Nominatim
import requests
from dotenv import load_dotenv
import os

load_dotenv() 

openai.api_key = "CHATGPT_API"
mixer.init()
todo_liste = []



def wetter_abrufen_wttr(stadt):
    url = f"https://wttr.in/{stadt}?format=%C+%t+%w+%h"
    response = requests.get(url)

    if response.status_code == 200:
        wetterbericht = response.text
        return f"Das Wetter in {stadt} ist {wetterbericht}."
    else:
        return "Es tut mir leid, ich konnte das Wetter für diese Stadt nicht abrufen."


def aktueller_standort():
    geolocator = Nominatim(user_agent="HelgaBot")
    standort = geolocator.geocode("me")

    if standort:
        return standort.address.split(",")[0]
    else:
        return None
def todo_hinzufuegen(aufgabe):
    todo_liste.append(aufgabe)
    sprechen(f"Aufgabe '{aufgabe}' zur To-Do-Liste hinzugefügt.")

def todo_entfernen(aufgabe):
    if aufgabe in todo_liste:
        todo_liste.remove(aufgabe)
        sprechen(f"Aufgabe '{aufgabe}' von der To-Do-Liste entfernt.")
    else:
        sprechen(f"Aufgabe '{aufgabe}' nicht in der To-Do-Liste gefunden.")

def todo_anzeigen():
    if not todo_liste:
        sprechen("Ihre To-Do-Liste ist leer.")
    else:
        sprechen("Ihre To-Do-Liste enthält die folgenden Aufgaben:")
        for aufgabe in todo_liste:
            sprechen(aufgabe)

def sprechen(text):
    if not mixer.get_init():
        mixer.init()

    tts = gTTS(text, lang='de', tld='com', slow=False)
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts.save(f"{fp.name}.mp3")
        mixer.music.load(f"{fp.name}.mp3")
        mixer.music.play()
        while mixer.music.get_busy():
            pass
        os.remove(f"{fp.name}.mp3")


def zuhoeren():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Ich höre zu...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        stimme = r.recognize_google(audio, language='de-DE')
        if 'Helga' in stimme:
            print(f"Du hast gesagt: {stimme.replace('Helga', '')}")
            return stimme.replace('Helga', '')
        else:
            return None
    except Exception as e:
        print("Entschuldigung, ich habe das nicht verstanden. Bitte wiederholen.")
        return None

def chat_gpt(text):
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Übersetzen Sie den folgenden deutschen Text in eine kohärente Antwort auf Deutsch: {text}",
            temperature=0.8,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            language_model="language_de",
        )
        antwort = response.choices[0].text.strip()
        return antwort
    except Exception as e:
        print(f"Fehler beim Abrufen der Antwort von GPT-3: {e}")
        return "Entschuldigung, es gab ein Problem bei der Verarbeitung Ihrer Anfrage."

def helga_bot():
    sprechen("Hallo, ich bin Helga, Ihr persönlicher Sprachassistent. Bitte rufen Sie mich mit meinem Namen auf, um mit mir zu interagieren.")
    verstanden = False
    while True:
        anfrage = zuhoeren()
        if not verstanden and anfrage == "":
            sprechen("Entschuldigung, ich habe das nicht verstanden. Bitte wiederholen.")
            verstanden = True
        elif anfrage != "":
            verstanden = False
            if "Helga" in anfrage:
                anfrage = anfrage.replace("Helga", "").strip()

                if "wie geht es dir" in anfrage.lower() or "wie geht's dir" in anfrage.lower() :
                    sprechen("Mir geht es gut, danke! Wie kann ich Ihnen helfen?")
                    if "Helga" in anfrage:
                        if "Wetter" in anfrage.lower() or "wie ist das Wetter" in anfrage.lower():
                            stadt = aktueller_standort()
                            if stadt is not None:
                                wetterbericht = wetter_abrufen_wttr(stadt)
                                sprechen(wetterbericht)
                            else:
                                sprechen("Entschuldigung, ich konnte Ihren Standort nicht ermitteln.")
                elif "aufgabe hinzufügen" in anfrage.lower():
                    todo_hinzufuegen(anfrage)
                elif "aufgabe entfernen" in anfrage.lower():
                    todo_entfernen(anfrage)
                elif "ansehen" in anfrage.lower() or "anzeigen" in anfrage.lower():
                    todo_anzeigen()
                else:
                    sprechen("Entschuldigung, ich habe das nicht verstanden. Bitte wiederholen.")

