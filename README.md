# sharez
Small Python script utilizing slop, ffmpeg, and transfer.sh to replicate "ShareX-esque" video recording functionality on Linux


### Dependencies:
`slop`, `ffmpeg`, `curl`, `xclip`

`pip install keyboard`

This script must be run as root, or else the keyboard shortcut to stop recording will not function.

### Usage:
Either manually trigger the script with `sudo python capture.py`, or create a keyboard shortcut that runs that command.

The video will stop recording and begin uploading when you press the backslash (`\`) key, and the URL will be copied to the clipboard as soon as it finishes.

### Disclaimer:

This is an ugly, messy hackjob and I have not been sober for any part of its creation
