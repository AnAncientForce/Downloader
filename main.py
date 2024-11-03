from tkinter import filedialog
from colorama import *
from rich.console import Console

import os
import sys
import signal
import requests
import subprocess
import time
import pyautogui
import pygetwindow
import pyperclip

current_directory = os.path.dirname(os.path.realpath(__file__))
console = Console()
SAVE_DIR = os.path.join(current_directory, 'Videos')

class Downloader:
    def __init__(self, idm=False, silent=False):
        self.idm = idm
        self.silent = silent

    def create_directory(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)


    def choose_download_type(self):

        self.create_directory(SAVE_DIR)

        x = input(f'(1: .m3u8, 2: .mp4) Please type {Fore.RED}1{Style.RESET_ALL} or {Fore.RED}2{Style.RESET_ALL} and press enter. > ')
        if x == '1':
            self.m3u8()
        elif x == '2':
            self.mp4()
        else:
            print(f'{Fore.RED}Cancel Operation{Style.RESET_ALL}')


    def m3u8(self):
        print('Please provide the .m3u8 file using the file picker')

        
        file_path = filedialog.askopenfilename(
            title="Select a File",
            filetypes=[(".m3u8 file", "*.m3u8")]
        )

        if not file_path:
            print(f'{Fore.RED}Cancel Operation{Style.RESET_ALL}')
            return

        print(f'{Fore.GREEN}>{Style.RESET_ALL}{file_path}')

        if '.m3u8' in file_path:
            print(f'{Fore.GREEN}.m3u8{Style.RESET_ALL}')

            URL = None

            with open(file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("http"):
                        print(f'Found {line}')
                        URL = line
                        break
           
            x = input('What should the file be called? > ')

            save_location = os.path.join(SAVE_DIR, x) + '.mp4'

            if os.path.exists(f'{save_location}'):
                print(f'{Fore.RED}File already at location{Style.RESET_ALL}')
                return

            with console.status("[bold green]Preparing...") as status:
                print(f'{Fore.GREEN}Saving to {save_location}{Style.RESET_ALL}')
                subprocess.run(f'ffmpeg -i "{URL}" -c copy "{save_location}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.on_success()

        
        
        
    def mp4(self):
        print(f'{Fore.GREEN}.mp4{Style.RESET_ALL}')

        url = input(f'Please specify the {Fore.RED}EXACT{Style.RESET_ALL} URL to the .mp4 > ')

        self.download(url, verify=False)
        
        self.on_success()
    


    def download(self, url, verify=False, optional_filename=None):

        filename = os.path.basename(url)

        if optional_filename:
            filename = optional_filename
        
        if verify:
            referer = self.activate_window(command=url)
            if referer:
                url = referer
            else:
                print(f'{Fore.RED}Could not capture referer{Style.RESET_ALL}')

        start_time = time.time()

        if self.idm:
            subprocess.run([r"C:\Program Files (x86)\Internet Download Manager\IDMan.exe", '/d', url, '/p', os.path.join(current_directory, "Videos")])
        else:
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()

                with open(os.path.join('Videos', filename), "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")

        end_time = time.time()
        time_elapsed = round(end_time - start_time)
        print(f'{Fore.GREEN}Successfully downloaded {filename}, took {time_elapsed}s {Style.RESET_ALL}')
    

    def activate_window(self, command=None):
        print(f'{Fore.RED}A referer may be required{Style.RESET_ALL}')
        pyperclip.copy(command.strip())
        w = 0.5
        try:
            windows = pygetwindow.getWindowsWithTitle('librewolf')
            if windows:
                window = windows[0]
                window.activate()
                time.sleep(w)
                pyautogui.hotkey('ctrl', 'l')  
                time.sleep(w)
                pyautogui.hotkey('ctrl', 'v')  
                time.sleep(w)
                pyautogui.press('enter')
                print(f'{Fore.RED}Verify you are human by completing the action below{Style.RESET_ALL}')
                input('Once you have verified, press Enter ')
                time.sleep(w)
                window.activate()
                pyautogui.hotkey('alt', 'left')
                time.sleep(w)
                pyautogui.hotkey('ctrl', 'l')
                time.sleep(w)
                pyautogui.hotkey('ctrl', 'c')  
                print('Copying text from URL')
                time.sleep(w)
                window.minimize()
                print(f'{Fore.GREEN}{pyperclip.paste()}{Style.RESET_ALL}')
                return pyperclip.paste()
        except pygetwindow.PyGetWindowException as e:
            print(f"An error occurred: {e}")
        print("Window not found")
        return False
    
    def on_success(self):
        print(f'{Fore.GREEN}Check your "Videos" folder in the same directory as this script to access your videos!{Style.RESET_ALL}')
        if not self.silent:
            play_audio(os.path.join('sfx', 'bank_se03#20.wav'))


def play_audio(sound_path) -> None:
    if os.path.exists(sound_path):
        subprocess.Popen(['ffplay', '-nodisp', '-autoexit', sound_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main() -> None:
    idm = False
    silent = False

    for arg in sys.argv[1:]:
        if '--idm' in arg:
            print(f'{Fore.GREEN}idm{Style.RESET_ALL}')
            idm = True
        if '-s' in arg:
            print(f'{Fore.GREEN}silent{Style.RESET_ALL}')
            silent = True
           
    downloader = Downloader(idm=idm, silent=silent)
    downloader.choose_download_type()

if __name__ == '__main__':
    main()


def on_exit():
    print(f'{Fore.RED}Cancel Operation{Style.RESET_ALL}')
    sys.exit(0)

signal.signal(signal.SIGINT, on_exit)