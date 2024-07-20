def download_file(url, output_filename):
    """
    Receives a downloadable url as 'url' and downloads that audio in
    our system as 'output_filename'.
    """
    import requests

    r = requests.get(url)

    with open(output_filename, 'wb') as outfile:
        outfile.write(r.content)

    return True