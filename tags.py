from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
    print("Place your RFID tag near the reader...")
    uid, text = reader.read()  # Read the UID and any data on the tag
    print(f"UID: {uid}")
finally:
    # Clean up GPIO pins after reading
    reader.cleanup()
