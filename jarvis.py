import ast
from RealtimeSTT import AudioToTextRecorder
import assist
import time
import tools
import os
import json
import numpy as np
from pyAudioAnalysis import audioBasicIO as aIO
from pyAudioAnalysis import MidTermFeatures as aF
from pydub import AudioSegment
from dotenv import load_dotenv
import wave

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

def generate_code_from_description(description):
    prompt = f"Generate Python code that {description}. Wrap the code in <code> tags."
    response = assist.ask_question_memory(prompt)
    start_index = response.find('<code>') + len('<code>')
    end_index = response.find('</code>')
    code_content = response[start_index:end_index].strip()

    if code_content.startswith('```') and code_content.endswith('```'):
        code_content = code_content[3:-3].strip()
    return code_content

def update_code(description, filename):
    new_code = generate_code_from_description(description)
    with open(filename, 'w') as file:
        file.write(new_code)
    return f"Code updated in {filename}"

def create_file(description, filename):
    if not os.path.exists(filename):
        new_code = generate_code_from_description(description)
        with open(filename, 'w') as file:
            file.write(new_code)
        return f"File {filename} created successfully with functionality: {description}"
    else:
        return f"File {filename} already exists. Please choose a different name."

def check_syntax_errors(code):
    errors = []
    try:
        ast.parse(code)
    except SyntaxError as e:
        lines = code.split('\n')
        while True:
            try:
                ast.parse('\n'.join(lines))
                break
            except SyntaxError as e:
                errors.append(f"Line {e.lineno}: {e.msg}")
                lines.pop(e.lineno - 1)
    return errors

def suggest_fixes_for_errors(errors, code):
    error_messages = "\n".join(errors)
    prompt = f"The following Python code has errors:\n\n{code}\n\nThe errors are:\n{error_messages}\n\nPlease provide a corrected version of the code. Wrap the code in <code> tags."
    response = assist.ask_question_memory(prompt)
    start_index = response.find('<code>') + len('<code>')
    end_index = response.find('</code>')
    fixed_code = response[start_index:end_index].strip()

    if fixed_code.startswith('```') and fixed_code.endswith('```'):
        fixed_code = fixed_code[3:-3].strip()
    return fixed_code

def check_and_fix_file(filename, recorder):
    with open(filename, 'r') as file:
        code = file.read()
    errors = check_syntax_errors(code)
    if errors:
        error_messages = "\n".join(errors)
        assist.TTS(f"Errors found in {filename}:\n{error_messages}")
        assist.TTS("Do you want to fix these errors?")
        confirmation = recorder.text().strip().lower()
        if "yes" in confirmation or "yeah" in confirmation or "sure" in confirmation:
            fixed_code = suggest_fixes_for_errors(errors, code)
            with open(filename, 'w') as file:
                file.write(fixed_code)
            return f"Errors in {filename} have been fixed."
        else:
            return f"Errors in {filename} were not fixed."
    else:
        return f"No errors found in {filename}."

def check_and_fix_project(recorder):
    results = []
    for filename in os.listdir():
        if filename.endswith(".py"):
            result = check_and_fix_file(filename, recorder)
            results.append(result)
    return "\n".join(results)

def save_audio_to_wav(audio_data, filename, sample_rate):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 2 bytes per sample
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())

def main():
    load_environment()

    recorder = AudioToTextRecorder(spinner=False, model="tiny.en", language="en", post_speech_silence_duration=0.5, silero_sensitivity=0.3)
    hot_words = ["jarvis"]
    skip_hot_word_check = False
    print("Say something...")

    while True:
        current_text = recorder.text()
        print(current_text)
        if any(hot_word in current_text.lower() for hot_word in hot_words) or skip_hot_word_check:
            if current_text:
                print("User: " + current_text)
                recorder.stop()
                current_text = current_text + " "

                # Save audio data to wav file
                save_audio_to_wav(recorder.audio, "current_speaker.wav", recorder.sample_rate)

                # Recognize speaker
                speaker_name = recognize_speaker("current_speaker.wav")

                if not speaker_name:
                    assist.TTS("I don't recognize your voice. What is your name?")
                    speaker_name = recorder.text().strip()
                    enroll_speaker(speaker_name, "current_speaker.wav")
                    assist.TTS(f"Nice to meet you, {speaker_name}!")

                if "update" in current_text.lower() and "code" in current_text.lower():
                    assist.TTS("Please describe what the code should do.")
                    description = recorder.text()
                    assist.TTS("Which file should I update?")
                    filename = recorder.text().strip()
                    result = update_code(description, filename)
                    assist.TTS(result)
                elif "create" in current_text.lower() and "file" in current_text.lower():
                    assist.TTS("Please describe what the code should do.")
                    description = recorder.text()
                    assist.TTS("What should be the name of the new file?")
                    filename = recorder.text().strip()
                    result = create_file(description, filename)
                    assist.TTS(result)
                elif "check" in current_text.lower() and "errors" in current_text.lower():
                    if "project" in current_text.lower():
                        results = check_and_fix_project(recorder)
                    else:
                        assist.TTS("Which file should I check?")
                        filename = recorder.text().strip()
                        results = check_and_fix_file(filename, recorder)
                    assist.TTS(results)
                else:
                    response = assist.ask_question_memory(current_text)
                    print(response)
                    speech = response.split('#')[0]
                    assist.TTS(speech)
                    skip_hot_word_check = True if "?" in response else False
                    if len(response.split('#')) > 1:
                        command = response.split('#')[1]
                        tools.parse_command(command)

                recorder.start()

if __name__ == '__main__':
    main()
