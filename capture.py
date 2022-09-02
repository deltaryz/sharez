# Dependencies:
# slop, ffmpeg, curl, xclip, tk
# pip install pysimplegui

# This is an ugly, messy hackjob and i have not been sober for any part of its creation
# but it works.

import subprocess
import PySimpleGUI as sg
import signal
import os
import time
from time import localtime, strftime

# Use slop to select a region
region = subprocess.check_output("slop", text=True, shell=True)

# Split strings to get separate numbers
coords = region.strip().split("+",1)
size = coords[0].split("x")
offset = coords[1].split("+")

# Get current time for video filename
ttime = strftime("%Y-%m-%d %H.%M.%S", localtime())

# Get the current directory the script is running from
path = os.path.abspath(os.path.dirname(__file__))

# Command flags for ffmpeg
command = ( "ffmpeg "
            f"-video_size {coords[0]} " 
            "-framerate 60 "
            "-f x11grab "
            "-show_region 1 "
            f"-i :0.0+{offset[0]},{offset[1]} "
            "-c:v libvpx -b:v 2M "
            f"-y \"{path}/{ttime}.webm\"" # Video is saved next to the script
          )

# Actually start ffmpeg
ffmpeg = subprocess.Popen(command, shell=True)

# Make sure the stop button is placed near the recording region
screen_width, screen_height = sg.Window.get_screen_size()
locationX = int(offset[0])
locationY = int(offset[1]) + int(size[1])

# Move stop button above region if it's near the bottom
if locationY > screen_height - 50:
    locationY = int(offset[1]) - 30

# Stop button window properties
event = sg.Window('Capture',
        [[sg.B('Stop')]],
        size=(50,30),
        margins=(0,0),
        keep_on_top=True,
        no_titlebar=True,
        location=(locationX,locationY)
        )

# Close window when the stop button is pressed
event.read(close=True)

# Tell ffmpeg to stop
os.kill(ffmpeg.pid, signal.SIGINT)

# Wait for ffmpeg to finish up
ffmpeg.wait()

# Curl command flags
commandcurl = ( "curl "
                f"--upload-file \"{path}/{ttime}.webm\" "
                "https://transfer.sh"
              )

# Run curl, uploading video to transfer.sh
link = subprocess.check_output(commandcurl, text=True, shell=True)

# Copy the link to clipboard and print
print(link)
os.system(f"echo \"{link}\" | xclip -i -selection clipboard")
