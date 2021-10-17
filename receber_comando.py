
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Código desenvolvido a partir do exemplo fornecido pela Google para o speech-to-text em stream, disponível em: https://github.com/googleapis/python-speech/blob/HEAD/samples/snippets/transcribe_streaming.py
"""

from __future__ import division

import re
import sys
import os

from google.cloud import speech

import pyaudio
from six.moves import queue
from credentials import CREDENTIALS_FILE_NAME


# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


# Obs: Essa classe não foi alterada do exemplo da Google.

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


def processar_respostas(responses):
    """Itera pelas respostas do servidor e as processa, chamando a função "identificar_comando". As respostas são processadas em loop até que um comando seja recebido.
    """
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        if result.is_final:

            # Gera uma lista com as alternativas de transcrição fornecidas.
            transcripts = [alt.transcript for alt in result.alternatives]

            #print(transcripts)

            # Recebe a letra e o número do comando a partir da lista de transcrições.
            comando = identificar_comando(transcripts)
            if comando:
                #print("Comando: {} {}".format(comando[0], comando[1]))

                # Se um comando foi identificado, ele é retornado
                return comando
            # Caso nenhum comando seja identificado nas transcrições, o loop continua.
            else:
                #print("Comando não identificado.")
                pass



def identificar_comando(transcripts):
    """ Recebe lista de possibilidades de transcrições da voz. Retorna a letra e o número do comando caso este seja seja encontrado. Se nenhum comando for identificado, retorna None.
    """

    # Define padrões de regex para as letras.
    padroes_busca_letra = {
        "A": re.compile(r"(?<!a-z)(a|à|á|há)(?!a-z)", re.I),
        "B": re.compile(r"(?<!a-z)(b|bê|be)(?!a-z)", re.I),
        "C": re.compile(r"(?<!a-z)(c|cê|se)(?!a-z)", re.I),
        "D": re.compile(r"(?<!a-z)(d|de|dê)(?!a-z)", re.I),
        "E": re.compile(r"(?<!a-z)(e|è|é)(?!a-z)", re.I),
        "F": re.compile(r"(?<!a-z)(f|efe)(?!a-z)", re.I),
        "G": re.compile(r"(?<!a-z)(g|gê)(?!a-z)", re.I),
        "H": re.compile(r"(?<!a-z)(h|agá)(?!a-z)", re.I)
    }

    # Define padrões de regex para os números.
    padroes_busca_numero = {
        "1": re.compile(r"1|(um|hum)"),
        "2": re.compile(r"2|(dois)"),
        "3": re.compile(r"3|(três)"),
        "4": re.compile(r"4|(quatro)"),
        "5": re.compile(r"5|(cinco)"),
        "6": re.compile(r"6|(seis)"),
        "7": re.compile(r"7|(sete)"),
        "8": re.compile(r"8|(oito)")
    }

    # Itera as transcrições em ordem, testando os matches pra cada uma. (É importante fazer dessa forma pois as transcrições estão em ordem de mais pra menos provável).
    for transcript in transcripts:
        # Itera os padrões de letra.
        for l_cand, padrao_l in padroes_busca_letra.items():
            l_match = padrao_l.search(transcript)
            #print("Transcript:", transcript)
            if l_match:
                # Letra encontrada na transcrição.
                letra = l_cand
                #print("Match: ", l_match.group(0))
                break
        else:
            # Letra não encontrada. Passa para a próxima transcrição.
            continue

        # Itera os padrões de número.
        for n_cand, padrao_n in padroes_busca_numero.items():
            n_match = padrao_n.search(transcript)
            if n_match:
                # Número encontrado na transcrição.
                numero = n_cand
                break
        else:
            # Número não encontrado. Passa para a próxima transcrição.
            continue

        # Se chegou aqui, letra e número foram encontrados na mesma transcrição. Um comando foi reconhecido.
        return letra, numero

    # Não foi reconhecido comando.
    return None


def receber_comando():

    # Define as credenciais pelo arquivo de json.
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE_NAME

    # Instancia o cliente para a voz.
    client = speech.SpeechClient()

    # Configurações do reconhecimento de voz.
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="pt-BR",
        max_alternatives=5, # São fornecidas até 5 alternativas para a transcrição, que serão processadas para se obter um comando.
        speech_contexts=[speech.SpeechContext(phrases=[
                        "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8",
                        "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8",
                        "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8",
                        "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8",
                        "E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8",
                        "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8",
                        "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8",
                        "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8",
                        ])], # Especifica o contexto, ou seja, as frases mais esperadas. No caso, são os comandos possíveis.
        model="command_and_search" # Especifica o modo de reconhecimento. No caso, é selecionado o mais apropriado para comandos curtos.
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        respostas = client.streaming_recognize(streaming_config, requests)

        return processar_respostas(respostas)
