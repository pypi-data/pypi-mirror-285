import requests
import zipfile
import os
import webbrowser


def ui_download(
    url="https://github.com/ccipd/MRQy/blob/radqy/UserInterface.zip?raw=true",
    local_filename="UserInterface.zip",
):
    # Make a GET request to fetch the raw HTML content
    with requests.get(url, stream=True) as response:
        response.raise_for_status()  # Check if the request was successful
        with open(local_filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    print(f"File downloaded and saved as {local_filename}")


def ui_unzip(zip_file="UserInterface.zip", output_folder="UserInterface"):

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(output_folder)
    print(f"File unzipped to {output_folder}")

# index.html
def ui_run(ui_folder="UserInterface"):
    # first check if the directory exists: UserInterface
    if not os.path.exists(ui_folder):
        ui_download()
        ui_unzip()

    url = f"file://{os.path.abspath(os.path.join(ui_folder, 'index.html'))}"
    webbrowser.open(url)
    print(f"Opening {url} in browser")   


# ui_download()
# ui_unzip()
# ui_run()
