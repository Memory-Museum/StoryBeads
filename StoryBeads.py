import time
import pygame
import serial
import pyaudio
import wave
import os
import threading
import queue

# Define serial port (adjust as needed)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# Tag and known tag parameters
tagLen = 16
idLen = 13
kTags = 5 #Number of known tags to handle 
known_tags_file = "known_tags.txt"  # File to store known tags
tag_audio_map = {}  # Dictionary to map tag IDs to lists of audio filenames

# Audio recording parameters
form_1 = pyaudio.paInt16  # 16-bit resolution
chans = 1  # 1 channel
samp_rate = 44100  # 44.1kHz sampling rate
chunk = 4096  # Buffer size for audio recording
record_secs = 10  # seconds to record

# Dictionary to store the last scan times and counts for tags
last_scan = {}

# Event queue for handling tag scan events
event_queue = queue.Queue()

def load_known_tags():
    """Load known tags mapping from file."""
    if os.path.exists(known_tags_file):
        with open(known_tags_file, "r") as file:  #If the file exists, open the file in read mode
            for line in file:
                tag_id, audio_files_str = line.strip().split(":") 
                tag_audio_map[tag_id] = audio_files_str.split(",")

def save_known_tags():
    """Save known tags mapping to file."""
    with open(known_tags_file, "w") as file:
        for tag_id, audio_files in tag_audio_map.items():
            audio_files_str = ",".join(audio_files)
            file.write(f"{tag_id}:{audio_files_str}\n")

def record_audio(filename):
    """Records audio and saves to a file."""
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
    if tag_id not in tag_audio_map:
        tag_audio_map[tag_id] = []
    tag_audio_map[tag_id].append(filename)
    save_known_tags()

def play_audio(filename):
    """Plays audio from a given file."""
    pygame.mixer.init()  # Initialize pygame mixer if not already
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        print("Playing...")
        time.sleep(0.1)  # Wait for playback to finish
    print("End of Audio file")

def tag_scanner():
    """Thread function to scan for tags and put them in the event queue."""
    while True:
        new_tag = ""
        if ser.in_waiting >= tagLen:  # Check if there is enough data in the buffer
            data = ser.read(tagLen) #Read the tag's data
            for char in data:
                if char not in (2, 13, 10, 3):  # Filter start/end characters
                    new_tag += chr(char) #Add the character to the new tag
        
        if new_tag:
           

def handle_tag_event(new_tag):
    """Handles events related to tag scans."""
    current_time = time.time()
    scan_count = 0

    if new_tag in tag_audio_map:  # Check if known tag
        last_scan_time, _ = last_scan.get(new_tag, (0, 0))
        print(f"{last_scan_time}, seconds passed: {(current_time - last_scan_time)}")
        
        if last_scan_time and ((current_time - last_scan_time) < 10):  # Scanned within 10 seconds
            print(f"Tag {new_tag} scanned twice within 10 seconds. Playing and recording new audio.")
            if pygame.mixer.music.get_busy():
                while pygame.mixer.music.get_busy():

                    recorded_filename = record_audio(f"{new_tag}_additional_{int(time.time())}.wav")
                    update_tag_audio_map(new_tag, recorded_filename)
        
        else:
            print(f"Tag {new_tag} recognized. Playing audio...")
            for audio_file in tag_audio_map[new_tag]:
                play_audio(audio_file)  # Play existing audio
            

        last_scan[new_tag] = (current_time, scan_count)  # Update last scan time and count
    else:
        # Unknown tag handling: Record audio and update mapping
        print(f"Tag {new_tag} unrecognized. Recording audio...")
        recorded_filename = record_audio(f"unknown_tag_{int(time.time())}.wav")
        update_tag_audio_map(new_tag, recorded_filename)
        play_audio(recorded_filename)
        last_scan[new_tag] = (current_time, 1)  # Initialize last scan time and count

def main():
  