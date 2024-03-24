# sharez
# made with <3 by deltaryz
# check out my music at deltaryz.com

from time import localtime, strftime
from playsound import playsound
import threading
import time
import os
import sys
import json
import signal
import PySimpleGUI as sg
import subprocess
import webbrowser
import re

print(
    "\n"
    "                       sharez\n"
    "              made with <3 by deltaryz\n"
    "                    deltaryz.com\n")


# DO NOT EDIT THIS VALUE
# Config located at ~/.config/sharez
configVersion = 1.2

# TODO: gif option
# TODO: Option for whether File, Path, or URL should be copied to clipboard

# TODO: Wayland support
# https://github.com/emersion/slurp
# https://github.com/ammen99/wf-recorder


# Directories
scriptPath = os.path.abspath(os.path.dirname(__file__))
configPath = os.path.expanduser("~/.config/sharez/config.json")

# Default settings, will be overridden by config & command flags
currentSettings = {
    "configversion": configVersion,
    "filetype": "mp4",
    "bitrate": "10",
    "framerate": "60",
    "audio": "default",
    "playsfx": True,
    "save": True,
    "savepath": os.path.expanduser("~/Videos"),
    "copypath": False,
    "copyfile": True,
    "preview": False,
    "tshurl": "https://transfer.sh",
    "upload": False,
    "copyurl": True,
    "openinbrowser": False,
}

# Check if we have a config
if not os.path.exists(configPath):
    # No config file has been created yet, populate with defaults
    print("No config found, creating...")

    # Make folder
    os.makedirs(os.path.expanduser("~/.config/sharez"), exist_ok=True)

    # Make file
    with open(configPath, 'w') as json_file:
        json.dump(currentSettings, json_file)
else:
    # We do have a config, load it
    print("Loading user config...\n")

    with open(configPath, 'r') as json_file:
        # Check if we need to update the config
        temp = json.load(json_file)
        if "configversion" not in temp:
            temp["configversion"] = "0"  # force update
        if temp["configversion"] < currentSettings["configversion"]:
            # Yes, config needs updating
            print(
                f"Config outdated ({temp['configversion']}). Updating to {currentSettings['configversion']}...")
            newVersion = currentSettings["configversion"]
            if newVersion >= 1.1 and temp['configversion'] < 1.1:
                # Patch audio device
                print("1.0 -> 1.1 audio device default patch applied")
                temp['audio'] = "default"
            # Load all existing options
            for setting in temp:
                currentSettings[setting] = temp[setting]
            currentSettings["configversion"] = newVersion
            # Write everything back into config
            with open(configPath, 'w') as json_file:
                json.dump(currentSettings, json_file)
        else:
            # No updating needed, just load it
            currentSettings = temp

# Use a separate dict so command overrides don't get mixed in the config
savedSettings = currentSettings.copy()

# Keep track of which settings have been overridden
overriddenSettings = currentSettings.copy()
for setting in overriddenSettings:
    # We will set this true when detecting command flags
    overriddenSettings[setting] = False

# print(currentSettings)
# print()

# Get screen size
screen_width, screen_height = sg.Window.get_screen_size()

# Sound effects
recordStart = scriptPath + "/sfx/BEGIN.wav"
recordFinish = scriptPath + "/sfx/END.wav"
encodingFinished = scriptPath + "/sfx/ENCODE.wav"
uploadFinished = scriptPath + "/sfx/UPLOAD.wav"


def sfx(sound, sync):
    # Play Sound Effect
    # sound = filename
    # sync = true to make program wait for sound to play before proceeding
    if currentSettings['playsfx']:
        if sync:
            playsound(sound)
        else:
            threading.Thread(target=playsound, args=(
                sound,), daemon=True).start()


print("Detecting audio devices...")
# Figure out audio device names
cmd = ("pactl list sources | grep 'Description'")
names = ""
try:
    names = subprocess.check_output(cmd, text=True, shell=True)
except subprocess.CalledProcessError as e:
    print(e)
# Split the string into lines
lines = names.strip().split('\n')
new_lines = [line.replace('Description: ', '').strip() for line in lines]

# Figure out audio device pulse IDs
cmd2 = ("pactl list short sources")
nums = ""
try:
    nums = subprocess.check_output(cmd2, text=True, shell=True)
except subprocess.CalledProcessError as e:
    print(e)
# Truncate
# Define the regular expression pattern to match numbers at the beginning of a string
pattern = r'^\s*(\d+)'
# Extract numbers from each line and store them in a list
numbers_list = []
for line in nums.split('\n'):
    match = re.findall(pattern, line)
    if match:
        numbers_list.append(match[0])

# there's a lot of redundant crap down here... i struggled a little with the implementation here.
# TODO: clean this

audioDevices = dict(zip(numbers_list, new_lines))

audioDeviceList = {}
audioDeviceNames = []
for key in audioDevices:
    audioDeviceList[key] = f"{key}: {audioDevices[key]}"
    audioDeviceNames.append(audioDeviceList[key])

if len(audioDeviceNames) == 0:
    print("\nNo audio devices detected - do you have pactl?")

audioDeviceList["default"] = "ALSA Default"
audioDeviceList["disabled"] = "Disabled"
audioDeviceNames.append("ALSA Default")
audioDeviceNames.append("Disabled")

# Check if our autoloaded audio device still exists
if currentSettings['audio'] not in audioDeviceList:
    badDevice = currentSettings['audio']
    currentSettings['audio'] = 'default'  # set to default so it doesnt error
    # Shove that back into config
    with open(configPath, 'w') as json_file:
        print(
            f"Audio device {badDevice} not detected, resetting to default.\n")
        json.dump(currentSettings, json_file)
        savedSettings = currentSettings.copy()

print()

# Get current time for video filename
filename = strftime("%Y-%m-%d_%H.%M.%S", localtime()) + \
    "." + currentSettings['filetype']


def str2bool(v):
    return str(v).lower() in ("yes", "true", "1")


# Check arguments
for arg in sys.argv:
    if "--preview=" in arg:  # Preview video in VLC before uploading
        overriddenSettings['preview'] = True
        currentSettings['preview'] = str2bool(arg.split("=", 1)[1])
    if "--browser=" in arg:  # Show transfer.sh URL in browser
        overriddenSettings['openinbrowser'] = True
        currentSettings['openinbrowser'] = str2bool(arg.split("=", 1)[1])
    if "--save=" in arg:  # Remove video after script runs
        overriddenSettings['save'] = True
        print(str2bool(arg.split("=", 1)[1]))
        currentSettings['save'] = str2bool(arg.split("=", 1)[1])
    if "--tshurl=" in arg:  # Custom transfer.sh url
        argurl = arg.split("=", 1)[1]
        overriddenSettings['tshurl'] = True
        currentSettings['tshurl'] = argurl
    if "--upload=" in arg:  # Don't upload to transfer.sh
        overriddenSettings['upload'] = True
        currentSettings['upload'] = str2bool(arg.split("=", 1)[1])
    if "--copy-url=" in arg:  # Copy URL to clipboard
        overriddenSettings['copyurl'] = True
        currentSettings['copyurl'] = str2bool(arg.split("=", 1)[1])
    if "--copy-path=" in arg:  # Copy file path to clipboard
        overriddenSettings['copypath'] = True
        currentSettings['copypath'] = str2bool(arg.split("=", 1)[1])
    if "--copy-file=" in arg:  # Copy file to clipboard
        overriddenSettings['copyfile'] = True
        currentSettings['copyfile'] = str2bool(arg.split("=", 1)[1])
    if "--audio=" in arg:  # Don't record audio
        overriddenSettings['audio'] = True
        _, currentSettings['audio'] = arg.split("=", 1)
    if "--soundfx=" in arg:  # Don't play sounds
        overriddenSettings['playsfx'] = True
        currentSettings['playsfx'] = str2bool(arg.split("=", 1)[1])
    if "--path=" in arg:  # Change path to save video
        argpath = arg.split("=", 1)[1]
        if argpath.endswith("/"):
            # Remove / from end of path
            argpath = argpath[:-1]
        overriddenSettings['savepath'] = True
        currentSettings['savepath'] = argpath

    if "--filename=" in arg:  # change filename of video (extension optional)
        _, filename = arg.split("=", 1)
        if filename.endswith('.webm'):
            overriddenSettings['filetype'] = True
            currentSettings['filetype'] = "webm"
        elif filename.endswith('.mp4'):
            overriddenSettings['filetype'] = True
            currentSettings['filetype'] = "mp4"
        else:  # make sure we have an extension
            filename += "." + currentSettings['filetype']
    if "--framerate=" in arg:  # set recording framerate
        overriddenSettings['framerate'] = True
        _, framerate = arg.split("=", 1)
        currentSettings['framerate'] = framerate

# print("Effective config after processing flags:")
# print(currentSettings)
# print()

# Create the output folder if it does not exist
if not os.path.exists(currentSettings['savepath']):
    print(f"Path {currentSettings['savepath']} does not exist, creating...")
    os.makedirs(currentSettings['savepath'])

print(f"Filename:                {filename}")
print(f"Directory:               {currentSettings['savepath']}")
print(f"Format:                  {currentSettings['filetype']}")
print("Bitrate:                 " + currentSettings['bitrate'])
print("Framerate:               " + currentSettings['framerate'])
print("Audio device:            " + audioDeviceList[currentSettings['audio']])
print()

# Use slop to select a region
region = subprocess.check_output("slop", text=True, shell=True)

sfx(recordStart, True)

print(f"Screen size:             {screen_width}x{screen_height}")
print(f"Region:                  {region}")

# Split strings to get separate numbers
coords = region.strip().split("+", 1)
size = coords[0].split("x")
offset = coords[1].split("+")

print(f"Size (before trimming):  {size[0]}x{size[1]}")

# fit within screen size
width = min(int(size[0]), screen_width - int(offset[0]))
height = min(int(size[1]), screen_height - int(offset[1]))

# Round width and height to even numbers
width = width // 2 * 2
height = height // 2 * 2

print(f"Size  (after trimming):  {width}x{height}")

# Command flags for ffmpeg
command = ("ffmpeg "
           f"-video_size {width}x{height} "
           f"-framerate {currentSettings['framerate']} "
           "-f x11grab -thread_queue_size 512 "
           "-show_region 1 "
           f"-i :0.0+{offset[0]},{offset[1]} "
           )

# only record audio if the user has that enabled
if currentSettings['audio'] != "disabled":
    if currentSettings['audio'] == "default":
        command += (
            "-f alsa -thread_queue_size 512 "
            "-i default "
        )
    else:
        # use pulseaudio device ID from `pactl list short sources`
        command += (
            "-f pulse -thread_queue_size 512 "
            f"-i {currentSettings['audio']} "
        )


if currentSettings['filetype'] == "webm":
    command += (
        f"-c:v libvpx -b:v {currentSettings['bitrate']}M "
        "-c:a libvorbis -b:a 128k "
    )

if currentSettings['filetype'] == "mp4":
    command += (
        f"-c:v libx264 -b:v {currentSettings['bitrate']}M "
        "-c:a aac -b:a 128k -preset ultrafast "
    )

command += (
    f"-y \"{currentSettings['savepath']}/{filename}\""
)

print(f"\nRunning command:         {command}\n\n-- -- -- -- --\n")

# Start ffmpeg
ffmpeg = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)

# Make sure the toolbar is placed near the recording region
locationX = int(offset[0]) - 3
locationY = int(offset[1]) + int(size[1]) + 10

# Move toolbar above region if it's near the bottom
if locationY > screen_height - 50:
    locationY = int(offset[1]) - 40

# If it's now less than 0 just put it in the corner lol
# TODO: Intelligently handle this on both axes
if locationY < 0:
    locationY = 0

sg.theme_background_color('#333333')

# Toolbar window properties
# TODO: Second duration indicator
event, values = sg.Window('Capture',
                          [[sg.Button("", key="OK", expand_x=True, image_source=scriptPath + "/img/done.png", image_subsample=3, button_color=('#3BFF62')),
                            sg.Button("", key="X", image_source=scriptPath + "/img/close.png",
                                      image_subsample=3, pad=(4, 4), button_color='#FF3232'),
                            sg.Text(text=f"{currentSettings['filetype']}", background_color='#2d2d2d',
                                    expand_x=True, justification='center', text_color='#929292'),
                            sg.Button("", key="Cfg", image_source=scriptPath +
                                      "/img/settings.png", image_subsample=3, button_color='#474747'),
                            ]],
                          size=(160, 30),
                          margins=(0, 0),
                          keep_on_top=True,
                          no_titlebar=True,
                          location=(locationX, locationY)
                          ).read(close=True)

# TODO: command flag to hide options button

# Tell ffmpeg to stop
os.killpg(os.getpgid(ffmpeg.pid), signal.SIGINT)

# Wait for ffmpeg to finish up
ffmpeg.wait()

print("\n-- -- -- -- --")

# Which button did the user press?
match event:
    case "Cfg":
        print("\nConfig panel opened.\nRemoving video...")
        sfx(recordFinish, True)
        os.system(f"rm \"{currentSettings['savepath']}/{filename}\"")

        # TODO: indicate anything overridden with flags using disabled=settingsOverrides["key"]
        # TODO: display command flags in GUI (to reduce clutter, use a ? mouseover)
        # TODO: split this panel into a function so we can re-run it if a validation fails

        window = sg.Window('Options', [
            [
                [sg.Text("\nCommandline flags will override these options.",
                         background_color="#222222", pad=(5, 10), expand_x=True, justification="center", text_color="#BFBFBF", size=(None, 3))]
            ],
            [
                sg.Text(
                    "\nUse 'Monitor of [Device]' to capture outputs,\n"
                    "i.e. your desktop speakers.\n\n"
                    "May require PipeWire.\n",
                    background_color="#444444", pad=((5, 5), (0, 10)), expand_x=True, text_color="#BFBFBF", justification="center", key="pavucontrol", enable_events=True)
            ],
            [  # Record audio
                [sg.Text("Record audio", justification="right", background_color="#333333", expand_x=True),
                 sg.Combo(audioDeviceNames, background_color="#FFFFFF", size=(25, None), default_value=audioDeviceList[savedSettings['audio']], readonly=True, key="audio")]
            ],
            [  # Path to save
                # TODO: Validate this and make sure it resolves
                # TODO: Browse button with file picker dialog
                [sg.Text("Local video path", justification="right", background_color="#333333", expand_x=True),
                 sg.InputText(key="savepath", size=(27, None), default_text=savedSettings['savepath'])]
            ],

            [sg.Column([
                [sg.Text("Filetype", justification="right", background_color="#333333"),
                 sg.Combo(['webm', 'mp4'], size=(6, None), default_value=savedSettings['filetype'], key='filetype', readonly=True)],
            ], pad=(0, 0)),
                sg.Stretch(background_color="#333333"), sg.Column([
                    [sg.Text("Bitrate (MB)", justification="right", background_color="#333333"),
                     sg.InputText(key="bitrate", size=(3, None), pad=(0, 0), default_text=savedSettings['bitrate'])]

                ])],

            [sg.Column([
                [sg.Text("Frame rate", justification="right", background_color="#333333"),
                 sg.InputText(key="framerate", size=(3, None), default_text=savedSettings['framerate'])]

            ], pad=(0, 0)),
                sg.Stretch(background_color="#333333"), sg.Column([
                    [sg.Text("Play sound effects", justification="right", background_color="#333333"),
                     sg.Checkbox("", default=savedSettings['playsfx'], pad=(0, 0), key="playsfx", background_color="#333333")]

                ])],

            [  # Copy file path to clipboard
                [sg.Text("Copy path to clipboard", justification="right", background_color="#333333", expand_x=True),
                 sg.Checkbox("", default=savedSettings['copypath'], key="copypath", background_color="#333333")]
            ],
            [  # Copy path to clipboard
                [sg.Text("Copy file to clipboard", justification="right", background_color="#333333", expand_x=True),
                 sg.Checkbox("", default=savedSettings['copyfile'], key="copyfile", background_color="#333333")]
            ],
            [  # Preview in VLC
                # TODO: Use system default for filetype
                [sg.Text("Preview in VLC", justification="right", background_color="#333333", expand_x=True),
                 sg.Checkbox("", default=savedSettings['preview'], key="preview", background_color="#333333")]
            ],
            [  # Upload to transfer.sh
                [sg.InputText(key="tshurl", size=(18, None), default_text=savedSettings['tshurl']),
                 sg.Text("Upload to transfer.sh", justification="right",
                         background_color="#333333", expand_x=True),
                 sg.Checkbox("", default=savedSettings['upload'], key="upload", background_color="#333333")]
            ],
            [  # Copy URL to clipboard after upload
                [sg.Text("Copy URL to clipboard", justification="right", background_color="#333333", expand_x=True),
                 sg.Checkbox("", default=savedSettings['copyurl'], key="copyurl", background_color="#333333")]
            ],
            [  # Open URL in browser
                [sg.Text("Open URL in browser", justification="right", background_color="#333333", expand_x=True),
                 sg.Checkbox("", default=savedSettings['openinbrowser'], key="openinbrowser", background_color="#333333")]
            ],
            [  # Save video file locally
                [sg.Text("Save video locally", justification="right", background_color="#333333", expand_x=True),
                 sg.Checkbox("", default=savedSettings['save'], key="save", background_color="#333333")]
            ],
            [
                [sg.Stretch(background_color="#2b2b2b"),
                 sg.Text("made with <3 by\ndeltaryz", enable_events=True, key="deltaryz", pad=((15, 15), (15, 0)), justification="center", text_color="#969696",
                         background_color="#333333"),
                 sg.Stretch(background_color="#2b2b2b")
                 ]
            ],
            [
                sg.Image(
                    source=scriptPath + "/img/logosmall.png", pad=((0, 0), (8, 0)), background_color="#333333", key='source', enable_events=True),
                sg.Stretch(background_color="#333333"),
                sg.Button("OK", button_color=(
                    "#BF40BF"), pad=((0, 0), (5, 6)))
            ]
        ],
            resizable=False,
            icon=scriptPath + "/img/icon.png",
            location=(69, 69)  # nice
        )

        while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED:
                print("Window closed, discarding changes.\n")
                break
            if event == 'OK':
                # TODO: Make sure to validate input & prompt user for invalid shit
                print()

                for value in values:
                    savedSettings[value] = values[value]

                    # special handling for the audio dropdown
                    if value == "audio":
                        for key in audioDeviceList:
                            # working in reverse, finding the key that matches the value
                            if audioDeviceList[key] == values[value]:
                                savedSettings[value] = key

                print()
                print(savedSettings)

                # Write everything back into config
                with open(configPath, 'w') as json_file:
                    json.dump(savedSettings, json_file)

                print("\nConfig written to file.\n")

                break
            elif event == 'deltaryz':
                webbrowser.open("https://deltaryz.com")
            elif event == 'source':
                webbrowser.open("https://github.com/deltaryz/sharez")
            elif event == 'pavucontrol':
                print("Opening pavucontrol...")
                os.system("pavucontrol &")

        window.close()

    case "OK":

        print()

        sfx(encodingFinished, True)

        # Copy path to clipboard
        if currentSettings['copypath'] == True:
            os.system(
                f"echo \"{currentSettings['savepath']}/{filename}\" | xclip -i -selection clipboard")
            print("Path copied to clipboard.")

        # Copy file to clipboard
        if currentSettings['copyfile']:
            os.system(
                f"echo \"file:///{currentSettings['savepath']}/{filename}\" | xclip -sel clip -t text/uri-list -i")
            print("File copied to clipboard.")

        # TODO: Use configurable media player instead of hardcoding VLC
        # Preview video in VLC
        if currentSettings['preview'] == True:
            os.system(f"vlc {currentSettings['savepath']}/{filename}")

        print(f"Path: {currentSettings['savepath']}/{filename}")

        if "https://transfer.sh" in currentSettings['tshurl']:
            print("\n==========\nNotice: https://transfer.sh has been temporarily(?) disabled as it appears to have gone offline.\nConsider self-hosting: https://github.com/dutchcoders/transfer.sh\n==========\n")
            currentSettings['upload'] = False

        if currentSettings['upload'] == True:
            print("\n\nOK, now uploading...\n\n")

            # make sure we have a slash at the end
            tshurl = currentSettings["tshurl"]
            if not tshurl.endswith("/"):
                tshurl += "/"

            # TODO: Do this with something built into python instead of curl
            # Curl command flags
            commandcurl = ("curl "
                           f"--upload-file \"{currentSettings['savepath']}/{filename}\" "
                           f"{tshurl}"
                           )

            link = ""
            try:
                # Run curl, uploading video to transfer.sh
                link = subprocess.check_output(
                    commandcurl, text=True, shell=True)

                # inline link for seamless sharing
                inline_link = link.replace(tshurl, tshurl + "inline/")

                # Important stuff is done
                print("\n\nDone uploading!")
                sfx(uploadFinished, True)

                # Copy the link to clipboard
                if currentSettings['copyurl'] == True:
                    os.system(
                        f"echo \"{inline_link}\" | xclip -i -selection clipboard")
                    print("URL copied to clipboard.")

                # Open link in browser
                if currentSettings['openinbrowser']:
                    webbrowser.open(link)

                print(f"\nLink: {inline_link}")
            except subprocess.CalledProcessError as e:
                print(e)

        if currentSettings['save'] == False:
            print("Removing video...")
            sfx(recordFinish, True)
            os.system(f"rm \"{currentSettings['savepath']}/{filename}\"")
    case _:
        print("\nCancelled.\nRemoving video...")
        sfx(recordFinish, True)
        os.system(f"rm \"{currentSettings['savepath']}/{filename}\"")

print()
