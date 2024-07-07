# jarvis.py

from RealtimeSTT import AudioToTextRecorder
import assist
import tools
import core.speech_recognition as sr_core
import core.code_management as cm

def main():
    sr_core.load_environment()

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
                sr_core.save_audio_to_wav(recorder.audio, "current_speaker.wav", recorder.sample_rate)

                # Recognize speaker
                speaker_name = sr_core.recognize_speaker("current_speaker.wav")

                if not speaker_name:
                    assist.TTS("I don't recognize your voice. What is your name?")
                    speaker_name = recorder.text().strip()
                    sr_core.enroll_speaker(speaker_name, "current_speaker.wav")
                    assist.TTS(f"Nice to meet you, {speaker_name}!")

                if "update" in current_text.lower() and "code" in current_text.lower():
                    assist.TTS("Please describe what the code should do.")
                    description = recorder.text()
                    assist.TTS("Which file should I update?")
                    filename = recorder.text().strip()
                    result = cm.update_code(description, filename)
                    assist.TTS(result)
                elif "create" in current_text.lower() and "file" in current_text.lower():
                    assist.TTS("Please describe what the code should do.")
                    description = recorder.text()
                    assist.TTS("What should be the name of the new file?")
                    filename = recorder.text().strip()
                    result = cm.create_file(description, filename)
                    assist.TTS(result)
                elif "check" in current_text.lower() and "errors" in current_text.lower():
                    if "project" in current_text.lower():
                        results = cm.check_and_fix_project(recorder)
                    else:
                        assist.TTS("Which file should I check?")
                        filename = recorder.text().strip()
                        results = cm.check_and_fix_file(filename, recorder)
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
