from openai import OpenAI
import time
from pygame import mixer
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path='Keys.env')

# Set your OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')

# Initialize the client and mixer
client = OpenAI(api_key=api_key, default_headers={"OpenAI-Beta": "assistants=v2"})
mixer.init()

assistant_id = "asst_LUL1wtigL2g5yB9opwodDaL1"
thread_id = "thread_lMzjNk8EhUU1B4aM2bhhlje4"

# Retrieve the assistant and thread
assistant = client.beta.assistants.retrieve(assistant_id)
thread = client.beta.threads.retrieve(thread_id)

def ask_question_memory(question):
    global thread
    client.beta.threads.messages.create(thread.id, role="user", content=question)
    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)

    while (run_status := client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)).status != 'completed':
        if run_status.status == 'failed':
            return "The run failed."
        time.sleep(1)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value

def generate_tts(sentence, speech_file_path):
    response = client.audio.speech.create(model="tts-1", voice="echo", input=sentence)
    response.stream_to_file(speech_file_path)
    return str(speech_file_path)

def play_sound(file_path):
    mixer.music.load(file_path)
    mixer.music.play()

def TTS(text):
    speech_file_path = generate_tts(text, "speech.mp3")
    play_sound(speech_file_path)
    while mixer.music.get_busy():
        time.sleep(1)
    mixer.music.unload()
    os.remove(speech_file_path)
    return "done"
