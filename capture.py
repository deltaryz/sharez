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

region = subprocess.check_output("slop", text=True, shell=True)
coords = region.strip().split("+",1)

size = coords[0].split("x")
offset = coords[1].split("+")

ttime = strftime("%Y-%m-%d %H.%M.%S", localtime())

path = os.path.abspath(os.path.dirname(__file__))

command = ( "ffmpeg "
            f"-video_size {coords[0]} " 
            "-framerate 60 "
            "-f x11grab "
            "-show_region 1 "
            f"-i :0.0+{offset[0]},{offset[1]} "
            "-c:v libvpx -b:v 2M "
            f"-y \"{path}/{ttime}.webm\""
          )

ffmpeg = subprocess.Popen(command, shell=True)

locationX = int(offset[0])
locationY = int(offset[1]) + int(size[1])

screen_width, screen_height = sg.Window.get_screen_size()

if locationY > screen_height - 50:
    locationY = int(offset[1]) - 30

event = sg.Window('Capture',
        [[sg.B('Stop')]],
        size=(50,30),
        margins=(0,0),
        keep_on_top=True,
        no_titlebar=True,
        location=(locationX,locationY)
        )

event.read(close=True)

os.kill(ffmpeg.pid, signal.SIGINT)

ffmpeg.wait()

commandcurl = ( "curl "
                f"--upload-file \"{path}/{ttime}.webm\" "
                "https://transfer.sh"
              )

link = subprocess.check_output(commandcurl, text=True, shell=True)
print(link)
os.system(f"echo \"{link}\" | xclip -i -selection clipboard")
