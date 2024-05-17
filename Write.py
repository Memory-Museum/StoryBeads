import time
import pygame
import serial
import pyaudio
import wave
import os

# Define serial port (adjust as needed)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# Tag and known tag parameters
tagLen = 16
idLen = 13
kTags = 5
known_tags_file = "known_tags.txt"  # File to store known tags
tag_audio_map = {}  # Dictionary to map tag IDs to audio filenames

# Audio recording parameters
form_1 = pyaudio.paInt16  # 16-bit resolution
chans = 1  # 1 channel
samp_rate = 44100  # 44.1kHz sampling rate
chunk = 4096  # 2^12 samples for buffer
record_secs = 10  # seconds to record


def load_known_tags():
    """Load known tags mapping from file."""
    if os.path.exists(known_tags_file):
        with open(known_tags_file, "r") as file:
            for line in file:
                tag_id, audio_file = line.strip().split(":")
                tag_audio_map[tag_id] = audio_file


def save_known_tags():
    """Save known tags mapping to file."""
    with open(known_tags_file, "w") as file:
        for tag_id, audio_file in tag_audio_map.items():
            file.write(f"{tag_id}:{audio_file}\n")


def record_audio(filename):
    """Records audio and saves to a new file with timestamp."""
    audio = pyaudio.PyAudio()
    stream = audio.open(format=form_1, rate=samp_rate, channels=chans, input=True, frames_per_buffer=chunk)
    print("Recording...")
    frames = []
    for _ in range(0, int((samp_rate / chunk) * record_secs)):
        data = stream.read(chunk)
        frames.append(data)
    print("Finished recording")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    wavefile = wave.open(filename, 'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()
    return filename


def update_tag_audio_map(tag_id, filename):
    """Updates the tag-audio mapping dictionary and saves it to a file."""
    tag_audio_map[tag_id] = filename
    save_known_tags()


def play_audio(filename):
    """Plays audio from a given file."""
    pygame.mixer.init()  # Initialize pygame mixer if not already
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)  # Wait for playback to finish
    print("End of Audio file")



pygame.init()

# Load known tags mapping from file
load_known_tags()

while True:
    new_tag = ""
    if ser.in_waiting == tagLen:  # Check for full tag in buffer
        data = ser.read(tagLen)
        for char in data:
            if char not in (2, 13, 10, 3):  # Filter start/end characters
                new_tag += chr(char)

    if new_tag:
        if new_tag in tag_audio_map:
            # Known tag handling: Play audio
            print(f"Tag {new_tag} recognized. Playing audio...")
            play_audio(tag_audio_map[new_tag])
        else:
            # Unknown tag handling: Record audio and update mapping
            print(f"Tag {new_tag} unrecognized. Recording audio...")
            recorded_filename = record_audio(f"unknown_tag_{int(time.time())}.wav")
            update_tag_audio_map(new_tag, recorded_filename)
