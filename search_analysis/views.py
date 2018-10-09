from django.shortcuts import render
import speech_recognition as sr

def get_data_from_form(request):
    voice_data = request.POST.get('voice_data', None)
    if request.POST:
        print('works!')
        voice_data = request.FILES.get('voice_data', None)
        print(type(voice_data))
    r = sr.Recognizer()
    if voice_data:
        data = sr.AudioFile(voice_data)
        with data as source:
            audio = r.record(source)
            r.recognize_google(audio)
            print(audio)
