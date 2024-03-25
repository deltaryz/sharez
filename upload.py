import subprocess


def transfersh(filepath, filename, tshurl):
    """
    Uploads a file to transfer.sh and returns both a preview URL and an inline URL.

    Args:
        filepath (string): Path of the file
        filename (string): Filename
        tshurl (string): URL of transfer.sh server

    Returns:
        string: Transfer.sh preview URL which displays embed, download button, and QR code
        string: Inline URL which directly links raw file
    """
    print("\nOK, now uploading...\n")

    # Make sure we have a slash
    if not tshurl.endswith("/"):
        tshurl += "/"

    # TODO: Change to http.client so we dont have this dependency
    commandcurl = ("curl "
                   f"--upload-file \"{filepath}\"/{filename} "
                   f"{tshurl}"
                   )

    try:
        # Run curl, uploading video to transfer.sh
        preview_link = subprocess.check_output(
            commandcurl, text=True, shell=True)

        # inline link for seamless sharing
        inline_link = preview_link.replace(tshurl, tshurl + "inline/")

        # Important stuff is done
        print("\nDone uploading!")

        return preview_link, inline_link
    except subprocess.CalledProcessError as e:
        print()
        print(e)
        return None, None
