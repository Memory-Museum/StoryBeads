
import time
import pygame
import serial
import pyaudio
import wave
import os

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# Tag and known tag parameters
tagLen = 16
idLen = 13
kTags = 5

# Audio recording parameters
form_1 = pyaudio.paInt16  # 16-bit resolution
chans = 1  # 1 channel
samp_rate = 44100  # 44.1kHz sampling rate
chunk = 4096  # 2^12 samples for buffer
record_secs = 10  # seconds to record

def play_audio(filename):
    """Plays audio from a given file."""
    pygame.mixer.init()  # Initialize pygame mixer if not already
    pygame.mixer.music.load(filename)
    pygame.mixer.music.set_volume(1) # max volume
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        print("Playing...")
        time.sleep(0.1)  # Wait for playback to finish
    print("End of Audio file")

def read_TagID():
    tagLen = 16
    new_tag = ""
    
    if ser.in_waiting >= tagLen:  # Check if enough bytes are available in the buffer
        data = ser.read(tagLen)  # Read the tag data
        for char in data:
            # Filter out control characters (start = 2, newline = 10, carriage return = 13, end = 3)
            if char not in (2, 13, 10, 3):
                new_tag += chr(char)  # Build the tag ID as a string
    return new_tag

def record_audio(filename='/home/jobez/StoryBeads/audios'):
    """Records audio and saves to a file."""
    # play prerecording audio:
    play_audio('/home/jobez/StoryBeads/pre-recording_audio.wav')

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

def play_audio(filename):
    """Plays audio from a given file."""
    pygame.mixer.init()  # Initialize pygame mixer if not already
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        print("Playing...")
        time.sleep(0.1)  # Wait for playback to finish
    print("End of Audio file")

def blue_RFID():
    audio_path = '/home/jobez/StoryBeads/audios'
    audio_files = [f for f in os.listdir(audio_path) if os.path.isfile(os.path.join(audio_path, f)) and f[-4:]==".wav"]
            # if there are audio files, play the files available in the audio folder /home/jobez/StoryBeads/audios
    if len(audio_files) != 0: 
        for each_file in audio_files: 
            play_audio(each_file)
    else: 
        #  record starts
        record_audio()

def green_RFID():
    """ 1) replay all audio files in chronological order
        2) if no audio is found, a instruction audio is played and audio recording starts"""
    
    pass 

def red_RFID():

    """ Delete all existing audio files, if any on the path: /home/jobez/StoryBeads/audios """
    pass

def main():
    TagsIDs = {
    "blue": '050020767B28',
    "green":'0500207B316F',
    "red": '0500207B3866' }

    # welcoming audio with intructions 
    #play_audio('/home/jobez/StoryBeads/welcomeaudio.wav') 

    # Identify the unique ID of the tags  
    while True:
        new_tag = read_TagID()
        if new_tag == TagsIDs['blue']: 
            blue_RFID()

        elif new_tag  == TagsIDs['green']: 
            green_RFID()

        elif new_tag  == TagsIDs['red']: 
            red_RFID()

        else:  
            print("Invalid Tag, use one of the RFID tags provided")
            # add an audio here to indicate that they need to 

                     
if __name__=="__main__":
    main()
