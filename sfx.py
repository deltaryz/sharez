import gi
import os
from urllib.request import pathname2url

scriptPath = os.path.abspath(os.path.dirname(__file__))

sounds = {
    'activate': scriptPath + "/sfx/ACTIVATE.wav",
    'recordStart': scriptPath + "/sfx/BEGIN.wav",
    'recordFinish': scriptPath + "/sfx/END.wav",
    'encodingFinished': scriptPath + "/sfx/ENCODE.wav",
    'uploadFinished': scriptPath + "/sfx/UPLOAD.wav",
    'uploadFailed': scriptPath + "/sfx/FAIL.wav",
}


def playSfx(sound: str, sync=True, volume=1.0):
    """
    Play sound effect using GStreamer

    Args:
        sound (string): Sound effect name
        sync (boolean, optional): Pause program and wait for sound to play
        volume (double, optional): Sound volume
    """

    # import gstreamer
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    Gst.init(None)
    playbin = Gst.ElementFactory.make('playbin', 'playbin')

    # make sure path exists
    path = os.path.abspath(sounds[sound])
    if not os.path.exists(path):
        raise RuntimeError(f"Sound effect path does not exist\n{path}")

    # set parameters
    playbin.props.uri = 'file://' + pathname2url(path)
    playbin.props.volume = volume

    # play sound
    set_result = playbin.set_state(Gst.State.PLAYING)
    if set_result != Gst.StateChangeReturn.ASYNC:
        raise RuntimeError(
            "playbin.set_state returned " + repr(set_result))

    # wait for sound to finish if sync=True
    if sync:
        bus = playbin.get_bus()
        try:
            bus.poll(Gst.MessageType.EOS, Gst.CLOCK_TIME_NONE)
        finally:
            playbin.set_state(Gst.State.NULL)
