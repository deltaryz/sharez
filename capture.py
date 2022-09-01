# Dependencies:
# slop, ffmpeg
# pip install keyboard 

# This script must be run as root, or else the keyboard shortcut to stop recording will not function.

# This is an ugly, messy hackjob and i have not been sober for any part of its creation
# but it works.

import subprocess
import keyboard
import signal
import os
import time
from time import localtime, strftime

region = subprocess.check_output("slop", text=True, shell=True)
print(region)
coords = region.strip().split("+",1)
print(coords)

offset = coords[1].split("+")

ttime = strftime("%Y-%m-%d %H.%M.%S", localtime())
print(ttime)

path = os.path.abspath(os.path.dirname(__file__))
print(path)

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

keyboard.on_press_key("\\", lambda _:os.kill(ffmpeg.pid, signal.SIGINT))

ffmpeg.wait()

commandcurl = ( "curl "
                f"--upload-file \"{ttime}.webm\" "
                "https://transfer.sh"
              )

link = subprocess.check_output(commandcurl, text=True, shell=True)
print(link)
os.system(f"echo \"{link}\" | xclip -i -selection clipboard")
