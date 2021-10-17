# Batalha Naval Comandada por Voz

Repositório para o trabalho da disciplina de Processamento de Voz (EEL816) ministrada no período letivo de 2021.1 na Universidade Federal do Rio de Janeiro (UFRJ).

## Requisitos

O jogo desenvolvido utiliza a API [Speech-to-Text](https://cloud.google.com/speech-to-text) e [Text-to-Speech](https://cloud.google.com/text-to-speech) do Google Cloud. Dessa maneira, é necessário uma chave API Google Cloud para a correta execução do jogo, em formato de arquivo json, que é especificado com a variável CREDENTIALS_FILE_NAME em "credentials.py". Além disso, o jogo utiliza algumas bibliotecas de Python. Para instalação das dependências, o usuário deve executar os seguintes comandos:

    pip install -r requisitos.txt
    pipwin install pyaudio

## Execução

Para executar o jogo, basta executar o seguinte comando:

    python jogo.py

