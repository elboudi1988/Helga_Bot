import speech_recognition as sr

r = sr.Recognizer()
with sr.Microphone() as source:
    print("Bitte sagen Sie etwas...")

    audio = r.listen(source)
    try:
        print("Sie haben gesagt:", r.recognize_google(audio, language="de-DE"))
    except sr.UnknownValueError:
        print("Entschuldigung, ich habe das nicht verstanden.")
    except sr.RequestError as e:
        print(f"Es gab ein Problem mit dem Google Speech Recognition Service: {e}")
