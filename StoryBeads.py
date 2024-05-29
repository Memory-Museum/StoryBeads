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
record_card_tag = "390097018F20"  # Special tag ID for the "record card"
delete_tag = "3900119A14A6"  # Tag ID for deletion
tag_audio_map = {}  # Dictionary to map tag IDs to audio filenames

# Audio recording parameters
form_1 = pyaudio.paInt16  # 16-bit resolution
chans = 1  # 1 channel
samp_rate = 44100  # 44.1kHz sampling rate
chunk = 4096  # 2^12 samples for buffer
record_secs = 10  # seconds to record

# Function to load known tags mapping from file
def load_known_tags():
    """Load known tags mapping from file."""
    if os.path.exists(known_tags_file):
        with open(known_tags_file, "r") as file:
            for line in file:
                if known_tags_file == "":
                    pass
                tag_id, audio_files = line.strip().split(":")
                tag_audio_map[tag_id] = audio_files.split(",")  # Multiple audio files

# Function to save known tags mapping to file
def save_known_tags():
    """Save known tags mapping to file."""
    with open(known_tags_file, "w") as file:
        for tag_id, audio_files in tag_audio_map.items():
            file.write(f"{tag_id}:{','.join(audio_files)}\n")

# Function to record audio and save to a new file with timestamp
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

# Function to update the tag-audio mapping dictionary and save it to a file
def update_tag_audio_map(tag_id, filename):
    if tag_id in tag_audio_map:
        tag_audio_map[tag_id] = tag_audio_map[tag_id] + [filename]  # Add the new file at the end of the list
    else:
        tag_audio_map[tag_id] = [filename]
    save_known_tags()


# Function to play audio from a given file
def play_audio(filename):
    """Plays audio from a given file."""
    pygame.mixer.init()  # Initialize pygame mixer if not already
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)  # Wait for playback to finish
    print("End of Audio file")

# Function to play all audio files associated with a tag
def play_all_audios(filenames):
    """Plays all audio files associated with a tag."""
    for filename in filenames:
        play_audio(filename)

# Function to print the contents of the tag_audio_map dictionary
def print_tag_audio_map():
    """Prints the contents of the tag_audio_map dictionary."""
    for tag_id, audio_files in tag_audio_map.items():
        print(f"Tag ID: {tag_id}")
        for audio_file in audio_files:
            print(f"  - {audio_file}")

# Function to delete audio files associated with a tag
def delete_tag_audio_files(tag_id):
    """Deletes audio files associated with a given tag."""
    if tag_id in tag_audio_map:
        for filename in tag_audio_map[tag_id]:
            os.remove(filename)
        del tag_audio_map[tag_id]
        save_known_tags()

def main():
    pygame.init()

    # Load known tags mapping from file
    load_known_tags()

    record_mode = False  # Flag to track if we're in "record mode"
    delete_mode = False  # Flag to track if we're in "delete mode"

    while True:
        new_tag = ""
        if ser.in_waiting == tagLen:  # Check for full tag in buffer
            data = ser.read(tagLen)
            for char in data:
                if char not in (2, 13, 10, 3):  # Filter start/end characters
                    new_tag += chr(char)

        if new_tag:
            if new_tag == record_card_tag: #Check if the scanned tag is a record card tag
                print("Record card scanned. Entering record mode...")
                record_mode = True
            elif new_tag == delete_tag:
                print("Delete tag scanned. Entering delete mode...")
                delete_mode = True
            elif new_tag in tag_audio_map and delete_mode:
                print(f"Tag {new_tag} recognized in delete mode. Deleting associated audio files...")
                delete_tag_audio_files(new_tag)
                delete_mode = False  # Exit delete mode after deleting
            elif new_tag in tag_audio_map:
                if record_mode:
                    # In record mode, record new audio for known tag
                    print(f"Tag {new_tag} recognized in record mode. Recording new audio...")
                    recorded_filename = record_audio(f"{new_tag}_additional_{int(time.time())}.wav")
                    update_tag_audio_map(new_tag, recorded_filename)
                    record_mode = False  # Exit record mode after recording
                else:
                    # Not in record mode, play all audios associated with the tag
                    print(f"Tag {new_tag} recognized. Playing audio...")
                    play_all_audios(tag_audio_map[new_tag])
            else:
                # Unknown tag handling: Record audio and update mapping
                print(f"Tag {new_tag} unrecognized. Recording audio...")
                recorded_filename = record_audio(f"unknown_tag_{int(time.time())}.wav")
                update_tag_audio_map(new_tag, recorded_filename)

            # Print the updated tag_audio_map
            print_tag_audio_map()

if __name__ == "__main__":
    main()