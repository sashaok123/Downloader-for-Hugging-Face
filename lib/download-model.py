import os
import sys
import subprocess
import importlib.util
import concurrent.futures
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import win32com.client
import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_shortcut(current_dir):
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    bat_file = os.path.join(current_dir, "Downloader for Hugging Face.bat")
    icon_file = os.path.join(current_dir, "huggingface_logo.ico")

    wsh = win32com.client.Dispatch("WScript.Shell")
    shortcut = wsh.CreateShortcut(os.path.join(parent_dir, "Downloader for Hugging Face.lnk"))
    shortcut.TargetPath = bat_file
    shortcut.IconLocation = icon_file
    shortcut.save()


def install_required_packages(packages):
    def install_package(package):
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    for package in packages:
        if importlib.util.find_spec(package) is None:
            print(f"Installing {package}...")
            install_package(package)



def download_file(url, output_folder):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    file_name = url.split("/")[-1]
    output_path = output_folder / file_name

    with tqdm(total=total_size, unit='iB', unit_scale=True, desc=file_name) as progress_bar:
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))

clear_console()
def get_download_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    download_links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and any(href.endswith(ext) for ext in (".ckpt", ".safetensors", ".yaml", ".bin", ".pt")):
            download_links.append("https://huggingface.co" + href.replace("/blob", "/resolve"))

    return download_links

clear_console()
def main():
    current_dir = os.path.abspath(os.getcwd())
    create_shortcut(current_dir)
    install_required_packages(['pywin32','beautifulsoup4', 'requests', 'tqdm'])

    clear_console()

    url = input("Please enter the URL of the model on Hugging Face (e.g. https://huggingface.co/runwayml/stable-diffusion-v1-5): ").strip()

    model_name = url.split('/')[-1]
    tree_url = url + "/tree/main"

    download_links = get_download_links(tree_url)

    if not download_links:
        print("No valid model files found. Please check the URL and try again.")
        return

    print("\nAvailable model files:")
    unique_download_links = list(set(download_links))
    for i, link in enumerate(unique_download_links, 1):
        file_name = link.split('/')[-1]
        file_base, file_ext = os.path.splitext(file_name)
        print(f"{i}: {file_base}{file_ext}")

    selected_files = input("\nEnter the numbers of the files you want to download (separated by spaces): ").split(' ')

    parent_folder = Path(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
    output_folder = parent_folder / "Downloaded models" / model_name
    output_folder.mkdir(parents=True, exist_ok=True)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(download_file, unique_download_links[int(num) - 1], output_folder) for num in selected_files]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error occurred while downloading a file: {e}")

if __name__ == "__main__":
    main()
