import socket
import mimetypes
import http.client


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

    # remove slash at end
    if tshurl.endswith('/'):
        tshurl = tshurl[:-1]

    # remove https://
    tsh_host = tshurl.split('//')[-1]

    # guess file's MIME type
    content_type, _ = mimetypes.guess_type(filename)
    if content_type is None:
        content_type = 'application/octet-stream'

    # Read file
    with open(filepath + "/" + filename, 'rb') as file:
        file_data = file.read()

    # Set headers
    headers = {
        'Content-Type': content_type,
        'Content-Length': str(len(file_data))
    }

    connection = http.client.HTTPSConnection(tsh_host)

    try:
        connection.request('PUT', f'/{filename}',
                           body=file_data, headers=headers)
        response = connection.getresponse()
        if response.status == 200:
            # It worked! :)
            preview_link = response.read().decode('utf-8')
            inline_link = preview_link.replace(tshurl, tshurl + "/inline")
            print(f"Done uploading!")
            return preview_link, inline_link
        else:
            print(response)
            return None, None
    except socket.gaierror as e:
        # bad URL
        print(e)
        return None, None
    finally:
        connection.close()
