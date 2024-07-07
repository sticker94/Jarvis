# core/speech_recognition.py

import os
import json
import wave
import numpy as np
import speech_recognition as sr
from pyAudioAnalysis import audioBasicIO as aIO
from pyAudioAnalysis import MidTermFeatures as aF
from dotenv import load_dotenv

MEMORY_FILE = 'memory.json'
SPEAKER_PROFILES_FILE = 'speaker_profiles.json'

def load_environment():
    load_dotenv()

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, 'w') as file:
        json.dump(memory, file)

def get_memory(key, default=None):
    memory = load_memory()
    return memory.get(key, default)

def set_memory(key, value):
    memory = load_memory()
    memory[key] = value
    save_memory(memory)

def update_memory(key, value):
    memory = load_memory()
    memory[key] = value
    save_memory(memory)

def load_speaker_profiles():
    if os.path.exists(SPEAKER_PROFILES_FILE):
        with open(SPEAKER_PROFILES_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_speaker_profiles(profiles):
    with open(SPEAKER_PROFILES_FILE, 'w') as file:
        json.dump(profiles, file)

def extract_features(audio_file):
    [Fs, x] = aIO.read_audio_file(audio_file)
    mt, st, _ = aF.mid_feature_extraction(x, Fs, 1.0 * Fs, 1.0 * Fs, 0.050 * Fs, 0.025 * Fs)
    return np.mean(mt, axis=1)

def enroll_speaker(name, audio_file):
    speaker_profiles = load_speaker_profiles()
    features = extract_features(audio_file)
    speaker_profiles[name] = features.tolist()
    save_speaker_profiles(speaker_profiles)
    return f"Speaker {name} enrolled successfully."

def recognize_speaker(audio_file):
    speaker_profiles = load_speaker_profiles()
    features = extract_features(audio_file)

    best_match = None
    best_score = float('inf')

    for name, profile in speaker_profiles.items():
        profile = np.array(profile)
        score = np.linalg.norm(profile - features)
        if score < best_score:
            best_score = score
            best_match = name

    return best_match

def save_audio_to_wav(audio_data, filename, sample_rate):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 2 bytes per sample
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())
