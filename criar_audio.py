import os
from google.cloud import texttospeech_v1
from gtts import gTTS
from playsound import playsound
from credentials import CREDENTIALS_FILE_NAME


def criar_audio(texto):

    # Set credentials environment variable and initialize text to speech client.
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE_NAME
    cliente = texttospeech_v1.TextToSpeechClient()

    # Specify voice and configuration parameters for Google TTS.
    voz = texttospeech_v1.VoiceSelectionParams(
        language_code='pt-BR',
        name='pt-BR-Wavenet-A'
    )
    audio_config = texttospeech_v1.AudioConfig(
        audio_encoding=texttospeech_v1.AudioEncoding.MP3
    )

    # Synthetize sentence recording.
    resposta = cliente.synthesize_speech(
        request={"input": texttospeech_v1.SynthesisInput(text=texto), "voice": voz, "audio_config": audio_config}
    )

    # If another audio was previously created, modify its permissions to avoid PermissionDenied error.
    if os.path.isfile("voz.mp3"):
        os.chmod("voz.mp3", 0o777)
    # Save audio file.
    with open("voz.mp3", "wb") as saida:
        saida.write(resposta.audio_content)
    playsound("voz.mp3")
    os.remove("voz.mp3")