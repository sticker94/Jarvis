import unittest
import os
import json
import wave
import numpy as np
from core import speech_recognition as sr

class TestSpeechRecognition(unittest.TestCase):

    def setUp(self):
        self.memory_file = 'test_memory.json'
        self.speaker_profiles_file = 'test_speaker_profiles.json'
        self.audio_file = 'test_audio.wav'
        sr.MEMORY_FILE = self.memory_file
        sr.SPEAKER_PROFILES_FILE = self.speaker_profiles_file
        self.create_test_audio_file()

    def tearDown(self):
        if os.path.exists(self.memory_file):
            os.remove(self.memory_file)
        if os.path.exists(self.speaker_profiles_file):
            os.remove(self.speaker_profiles_file)
        if os.path.exists(self.audio_file):
            os.remove(self.audio_file)

    def create_test_audio_file(self):
        with wave.open(self.audio_file, 'wb') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 2 bytes per sample
            wf.setframerate(44100)  # Sample rate
            wf.writeframes(np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100)).astype(np.int16).tobytes())

    def test_load_memory(self):
        with open(self.memory_file, 'w') as file:
            json.dump({'key': 'value'}, file)
        memory = sr.load_memory()
        self.assertEqual(memory['key'], 'value')

    def test_save_memory(self):
        memory = {'key': 'value'}
        sr.save_memory(memory)
        with open(self.memory_file, 'r') as file:
            saved_memory = json.load(file)
        self.assertEqual(saved_memory['key'], 'value')

    def test_get_memory(self):
        with open(self.memory_file, 'w') as file:
            json.dump({'key': 'value'}, file)
        value = sr.get_memory('key')
        self.assertEqual(value, 'value')

    def test_set_memory(self):
        sr.set_memory('key', 'value')
        with open(self.memory_file, 'r') as file:
            memory = json.load(file)
        self.assertEqual(memory['key'], 'value')

    def test_update_memory(self):
        with open(self.memory_file, 'w') as file:
            json.dump({'key': 'old_value'}, file)
        sr.update_memory('key', 'new_value')
        with open(self.memory_file, 'r') as file:
            memory = json.load(file)
        self.assertEqual(memory['key'], 'new_value')

    def test_load_speaker_profiles(self):
        with open(self.speaker_profiles_file, 'w') as file:
            json.dump({'speaker': [0.1, 0.2]}, file)
        profiles = sr.load_speaker_profiles()
        self.assertEqual(profiles['speaker'], [0.1, 0.2])

    def test_save_speaker_profiles(self):
        profiles = {'speaker': [0.1, 0.2]}
        sr.save_speaker_profiles(profiles)
        with open(self.speaker_profiles_file, 'r') as file:
            saved_profiles = json.load(file)
        self.assertEqual(saved_profiles['speaker'], [0.1, 0.2])

    def test_enroll_speaker(self):
        sr.enroll_speaker('test_speaker', self.audio_file)
        profiles = sr.load_speaker_profiles()
        self.assertIn('test_speaker', profiles)

    def test_recognize_speaker(self):
        sr.enroll_speaker('test_speaker', self.audio_file)
        recognized_speaker = sr.recognize_speaker(self.audio_file)
        self.assertEqual(recognized_speaker, 'test_speaker')

if __name__ == '__main__':
    unittest.main()
