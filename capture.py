# Dependencies:
# slop, ffmpeg, curl, xclip, tk
# pip install pysimplegui playsound

# I have not been sober for any part of the creation of this script

import subprocess
import PySimpleGUI as sg
import signal
import sys
import os
import time
import threading
from playsound import playsound
from time import localtime, strftime

# Get the current directory the script is running from
path = os.path.abspath(os.path.dirname(__file__))

# Sound effects
recordStart = path + "/BEGIN.wav"
recordFinish = path + "/END.wav"
encodingFinished = path + "/ENCODE.wav"
uploadFinished = path + "/UPLOAD.wav"

# sound = filename
# sync = true to make program wait for sound to play before proceeding


def sfx(sound, sync):
    if soundSetting:
        if sync:
            playsound(sound)
        else:
            threading.Thread(target=playsound, args=(
                sound,), daemon=True).start()


# Get current time for video filename
filename = strftime("%Y-%m-%d_%H.%M.%S", localtime()) + ".mp4"

# Check for arguments
rmSetting = False
uploadSetting = True
soundSetting = True
copySetting = True
openVLC = False
recordAudioSetting = True
framerateSetting = 60

for arg in sys.argv:
    if arg == "--vlc":  # Preview video in VLC before uploading
        openVLC = True
    if arg == "--rm":  # Remove video after script runs
        rmSetting = True
    if arg == "--no-upload":  # Don't upload to transfer.sh
        uploadSetting = False
    if arg == "--no-copy":  # Don't copy to clipboard
        copySetting = False
    if arg == "--no-soundfx":  # Don't play sounds
        soundSetting = False
    if arg == "--no-audio":  # Don't record audio
        recordAudioSetting = False
    if "--path=" in arg:  # Change path to save video
        _, path = arg.split("=", 1)
    if "--filename=" in arg:  # change filename of video
        _, filename = arg.split("=", 1)
        if ".webm" not in filename and ".mp4" not in filename:  # make sure we have an
            filename += ".mp4"
    if "--framerate=" in arg:  # set recording framerate
        _, framerate = arg.split("=", 1)
        framerateSetting = int(framerate)

print("Framerate: " + str(framerateSetting))

# Use slop to select a region
region = subprocess.check_output("slop", text=True, shell=True)

sfx(recordStart, True)

print(f"Region: {region}")

# Split strings to get separate numbers
coords = region.strip().split("+", 1)
size = coords[0].split("x")
offset = coords[1].split("+")

# Ensure width and height are even numbers
width = int(size[0]) // 2 * 2
height = int(size[1]) // 2 * 2

# Command flags for ffmpeg
command = ("ffmpeg "
           f"-video_size {width}x{height} "
           f"-framerate {framerateSetting} "
           "-f x11grab "
           "-show_region 1 "
           f"-i :0.0+{offset[0]},{offset[1]} "
           )

# only record audio if the user has that enabled
if recordAudioSetting:
    command += (
        "-f alsa "
        "-i default "
    )

if ".webm" in filename:
    command += (
        "-c:v libvpx -b:v 2M "
        "-c:a libvorbis -b:a 128k "
    )

if ".mp4" in filename:
    command += (
        "-c:v libx264 -b:v 2M "
        "-c:a aac -b:a 128k -preset ultrafast "
    )

command += (
    f"-y \"{path}/{filename}\""
)

print(f"Running command: {command}\n")

# Start ffmpeg
ffmpeg = subprocess.Popen(command, shell=True)

# Make sure the stop button is placed near the recording region
locationX = int(offset[0])
locationY = int(offset[1]) + int(size[1])

# Move stop button above region if it's near the bottom
screen_width, screen_height = sg.Window.get_screen_size()
if locationY > screen_height - 50:
    locationY = int(offset[1]) - 30

# Stop button window properties
event, values = sg.Window('Capture',
                          [[sg.OK(), sg.Cancel()]],
                          size=(120, 30),
                          margins=(0, 0),
                          keep_on_top=True,
                          no_titlebar=True,
                          location=(locationX, locationY)
                          ).read(close=True)

# Tell ffmpeg to stop
os.kill(ffmpeg.pid, signal.SIGINT)

# Wait for ffmpeg to finish up
ffmpeg.wait()

sfx(recordFinish, True)

# Only do this if the user pressed OK
if event == 'OK' and uploadSetting == True:
    sfx(encodingFinished, False)
    # Preview video in VLC before uploading
    if openVLC == True:
        os.system(f"vlc {path}/{filename}")
    print("\n\nOK, now uploading...\n\n")

    # Curl command flags
    commandcurl = ("curl "
                   f"--upload-file \"{path}/{filename}\" "
                   "https://transfer.sh"
                   )

    # Run curl, uploading video to transfer.sh
    link = subprocess.check_output(commandcurl, text=True, shell=True)

    # Important stuff is done
    print("\n\nDone uploading!")
    sfx(uploadFinished, True)

    # Copy the link to clipboard
    if copySetting == True:
        os.system(f"echo \"{link}\" | xclip -i -selection clipboard")
        print("Copied to clipboard!")

    print(f"\nLink: {link}")

print(f"Path: {path}/{filename}\n")

# Remove video file if command flag --rm is passed or the user pressed Cancel
if rmSetting == True or event == 'Cancel':
    print("Removing video...")
    os.system(f"rm \"{path}/{filename}\"")
