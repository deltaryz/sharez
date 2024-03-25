import subprocess
import re


def refresh_devices():
    """
    Creates dictionaries/lists for keeping track of audio device objects
    """

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

    # Figure out short device names
    cmd3 = ("pactl list sources | grep 'Name'")
    shortNames = ""
    try:
        shortNames = subprocess.check_output(cmd3, text=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(e)
    # Split the string into lines
    shortLines = shortNames.strip().split('\n')
    new_shortLines = [line.replace('Name: ', '').strip()
                      for line in shortLines]

    audioDevices = dict(zip(numbers_list, new_lines))

    # Put everything in an object together with fields for ID, short name, long name
    audioDeviceList = {}
    audioDeviceShortNames = {}
    audioDeviceNames = []
    index = 0
    for key in audioDevices:
        audioDeviceList[key] = f"{key}: {audioDevices[key]}"
        audioDeviceNames.append(audioDeviceList[key])
        audioDeviceShortNames[key] = new_shortLines[index]
        index = index + 1

    if len(audioDeviceNames) == 0:
        print("\nNo audio devices detected - do you have pactl?")

    audioDeviceList["default"] = "ALSA Default"
    audioDeviceList["disabled"] = "Disabled"
    audioDeviceShortNames["default"] = "default"
    audioDeviceShortNames["disabled"] = "disabled"
    audioDeviceNames.append("ALSA Default")
    audioDeviceNames.append("Disabled")

    return audioDeviceList, audioDeviceShortNames, audioDeviceNames
