import os
import site
import socket

import numpy as np
import speech_recognition as sr
from faster_whisper import WhisperModel

# laptop_sim_mic.py

# Bypassing gpu security
try:
    for site_package in site.getsitepackages():
        cublas_path = os.path.join(site_package, "nvidia", "cublas", "bin")
        cudnn_path = os.path.join(site_package, "nvidia", "cudnn", "bin")

        if os.path.exists(cublas_path):
            # Force Windows to trust this folder
            os.add_dll_directory(cublas_path)
            os.environ["PATH"] = cublas_path + \
                os.pathsep + os.environ.get("PATH", "")

        if os.path.exists(cudnn_path):
            # Force Windows to trust this folder
            os.add_dll_directory(cudnn_path)
            os.environ["PATH"] = cudnn_path + \
                os.pathsep + os.environ.get("PATH", "")
except Exception as e:
    print(f"Warning: GPU Path hack failed: {e}")


# Setting up the network connection (Keeping for now even though we're using the file add and delete method)
UDP_IP = "172.23.224.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Loading Faster-Whisper...")
model = WhisperModel("medium.en", device="cuda", compute_type="float16")
recognizer = sr.Recognizer()

recognizer.dynamic_energy_threshold = False  # To turn off auto-volume
recognizer.energy_threshold = 400            # Hardcoding sensitivity
recognizer.pause_threshold = 1.0             # Wait time before transcribing

with sr.Microphone() as source:
    print("Adjusting for background noise. Please wait for 1 second...")
    recognizer.adjust_for_ambient_noise(source, duration=1.0)
    print("\nReady! You can send in commands now.")

    while True:
        try:
            # Shortened phrase time limit so the robot reacts faster
            audio_data = recognizer.listen(
                source, timeout=1.0, phrase_time_limit=3.0)

            wav_bytes = audio_data.get_wav_data(
                convert_rate=16000, convert_width=2)
            audio_np = np.frombuffer(
                wav_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            segments, _ = model.transcribe(
                audio_np, beam_size=1, vad_filter=True)
            transcription = "".join([s.text for s in segments]).strip()

            if transcription:
                print(f" Heard: '{transcription}'")
                # Path to the shared folder
                file_path = r"C:\ros_clone_location\FINAL_PROJECT\final-project-mecanum_3\shared_command.txt"
                try:
                    with open(file_path, "w") as f:
                        f.write(transcription)
                except Exception as file_err:
                    print(f"File Write Error: {file_err}")

        except sr.WaitTimeoutError:
            pass  # Keep listening and waiting for commands
        except KeyboardInterrupt:
            print("\nShutting down microphone.")
            break
        except Exception as e:
            print(f"Error: {e}")
