# Making the necessary imports
import os
import site

# Windows gpu security bypass
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

# Importing the ai related libraries
import socket

import numpy as np
import speech_recognition as sr
from faster_whisper import WhisperModel

# Setting up the network connection to the limo
UDP_IP = "172.20.10.2"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Loading Faster-Whisper...")
model = WhisperModel("medium.en", device="cuda", compute_type="float16")
recognizer = sr.Recognizer()

recognizer.dynamic_energy_threshold = False  # To turn off auto-volume
recognizer.energy_threshold = 500            # Hardcoding sensitivity
recognizer.pause_threshold = 1.0             # Wait time before transcribing

with sr.Microphone() as source:
    print("Adjusting for background noise. Please wait for 1 second...")
    recognizer.adjust_for_ambient_noise(source, duration=1.0)
    print("\nReady! You can send in commands now.")

    while True:
        try:
            # Shortened phrase_time_limit so the robot reacts faster
            audio_data = recognizer.listen(
                source, timeout=1.0, phrase_time_limit=3.0)

            wav_bytes = audio_data.get_wav_data(
                convert_rate=16000, convert_width=2)
            audio_np = np.frombuffer(
                wav_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            # Increasing speed
            segments, _ = model.transcribe(
                audio_np, beam_size=1, vad_filter=True)
            transcription = "".join([s.text for s in segments]).strip()

            if transcription:
                print(f" Heard: '{transcription}'")

                # Transmit the text to the robot over Wi-Fi
                try:
                    sock.sendto(transcription.encode(
                        'utf-8'), (UDP_IP, UDP_PORT))
                    print(f"Sent to {UDP_IP}:{UDP_PORT}")
                except Exception as udp_err:
                    print(f"UDP Send Error: {udp_err}")

        except sr.WaitTimeoutError:
            pass  # Keep listening and waiting for commands
        except KeyboardInterrupt:
            print("\nShutting down microphone.")
            break
        except Exception as e:
            print(f"Error: {e}")
