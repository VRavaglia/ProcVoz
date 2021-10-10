import speech_recognition as speech_recognition
from gtts import gTTS
from playsound import playsound

def ouvir_microfone():
    microfone = sr.Recognizer()
    with sr.Microphone() as source:
        microfone.adjust_for_ambient_noise(source)
        audio = microfone.listen(source)
    
    try:
        posicao = microfone.recognize_google(audio, language='pt-BR')

    except sr.UnknownValueError:
        print ("Nao entendi")
    return posicao

def criar_audio(texto):
    tts = gTTS(texto, lang='pt-br')
    tts.save('audios/cpu_move.wav')
    playsound('audios/cpu_move.wav')

