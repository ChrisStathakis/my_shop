from django.shortcuts import render
import speech_recognition as sr

def get_data_from_form(request):
    voice_data = request.POST.get('voice_data', None)
    r = sr.Recognizer()
    if voice_data:
        data = sr.AudioFile(voice_data)
        with data as source:
            audio = r.record(source)
            r.recognize_google(audio)

