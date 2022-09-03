# sharez
Small Python script utilizing slop, ffmpeg, and transfer.sh to replicate "ShareX-esque" video recording functionality on Linux


### Dependencies:
`slop`, `ffmpeg`, `curl`, `xclip`, `tk`

`pip install pysimplegui`

### Usage:
Either manually trigger the script with `python capture.py`, or create a keyboard shortcut that runs that command. 

Click and drag to select the region to record, and the recording will immediately begin.

There will be an OK button below or above the recording region, when pressed it will immediately stop recording and upload the video to transfer.sh, and then copy a shareable URL to the clipboard.

Commandline Flags:
* `--rm` - remove the video file after script runs
* `--no-upload` - do not upload to transfer.sh
* `--path=/home/example` - path to save video
