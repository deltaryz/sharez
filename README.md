# sharez
Small Python script utilizing slop, ffmpeg, and transfer.sh to replicate "ShareX-esque" video recording functionality on Linux


### Dependencies:
`slop`, `ffmpeg`, `curl`, `xclip`, `tk`

`pip install pysimplegui`

### Usage:
Either manually trigger the script with `python capture.py`, or create a keyboard shortcut that runs that command. Append `--rm` to remove the local copy of the video after uploading.

You may then click and drag to select the region to record, at which point the recording will immediately begin.

There will be a stop button below or above the recording region, which will then immediately upload the video to transfer.sh and copy a shareable URL to the clipboard.

### Disclaimer:

This is an ugly, messy hackjob and I have not been sober for any part of its creation
