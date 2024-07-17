import requests
from pytube import YouTube, Playlist, Channel
from pytube.exceptions import VideoUnavailable
from datetime import datetime
from moviepy.editor import VideoFileClip
import moviepy.video.fx.all as vfx
import os






def check_link_existence(url: str) -> bool:
    """
    Check the existence of a YouTube video, playlist, or channel based on the provided URL.

    Args:
        url (str): The URL of the YouTube video, playlist, or channel.

    Returns:
        bool: True if the video, playlist, or channel exists, False otherwise.
    """
    try:
        if 'youtube.com/watch?v=' in url or 'youtu.be/' in url:
            # Attempt to create a YouTube object
            yt = YouTube(url)
            # Check if the video title is available, indicating existence
            return bool(yt.title)

        elif 'youtube.com/playlist?list=' in url:
            playlist = Playlist(url)
            # Check if the playlist is empty or if it's unavailable
            return bool(playlist.video_urls)

        elif 'youtube.com/channel/' in url:
            # We assume that if a channel link can be created, it exists
            Channel(url)
            return True

        else:
            return False

    except VideoUnavailable:
        return False




def check_link_type(url: str) -> str:
    """
    Check the type of the YouTube link (channel, video, or playlist).

    Args:
        - url (str): The YouTube URL to check.

    Returns:
        - str: The type of the link ('channel', 'video', 'playlist'), or 'unknown' if not recognized.
    """
    # Send a GET request to the URL to check if it exists
    response = requests.get(url)
    if response.status_code != 200:
        return 'unknown'  # URL doesn't exist

    # Check if it's a video link
    if 'watch?v=' in url:
        return 'video'

    # Check if it's a channel link
    if '/channel/' in url:
        return 'channel'

    # Check if it's a playlist link
    if 'list=' in url:
        return 'playlist'

    return 'unknown'


def check_link(url: str) -> tuple:
    """
    Check the existence and type of a YouTube link.

    Args:
        - url (str): The YouTube URL to check.

    Returns:
        - tuple: A tuple containing the type of the link ('channel', 'video', 'playlist', or 'unknown')
                 and a boolean indicating if the link exists.
    """
    link_type = check_link_type(url)
    exists = check_link_existence(url)
    return (link_type, exists)

def print_green_(text)->None:
    text = str(text)
    print("\033[92m" + text + "\033[0m")

def print_red_(text):
    text = str(text)
    print("\033[91m" + text + "\033[0m")

def print_colored_(text, hex_color):
    """
    Print the text in the specified color.
    
    :param text: The text to be printed.
    :param color: The color in which the text should be printed.
                  Options: 'green', 'red', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'black', 'gray', 
                           'lightgray', 'darkgray', 'lightblue', 'lightgreen', 'lightcyan', 'lightred', 'pink'
                  Optionally, the color can be specified as a hexadecimal string.
                  Optional: False
    """
    text = str(text)
    color_codes = {
        "green": "0;255;0",
        "red": "255;0;0",
        "yellow": "255;255;0",
        "blue": "0;0;255",
        "magenta": "255;0;255",
        "cyan": "0;255;255",
        "white": "255;255;255",
        "black": "0;0;0",
        "gray": "128;128;128",
        "lightgray": "211;211;211",
        "darkgray": "169;169;169",
        "lightblue": "173;216;230",
        "lightgreen": "144;238;144",
        "lightcyan": "224;255;255",
        "lightred": "255;182;193",
        "pink": "255;192;203",
    }

    if hex_color.lower() in color_codes:
        color = color_codes[hex_color.lower()]
    else:
        try:
            if hex_color[0] == "#":
                hex_color = hex_color[1:]
            if len(hex_color) != 6:
                raise ValueError("Hex color must be 6 characters long.")
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            color = f"{r};{g};{b}"
        except ValueError as e:
            print(f"Error: {e}")
            return

    print(f"\033[38;2;{color}m{text}\033[0m")
def return_colored_(text, hex_color):
    """
    Print the text in the specified color.
    
    :param text: The text to be printed.
    :param color: The color in which the text should be printed.
                  Options: 'green', 'red', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'black', 'gray', 
                           'lightgray', 'darkgray', 'lightblue', 'lightgreen', 'lightcyan', 'lightred', 'pink'
                  Optionally, the color can be specified as a hexadecimal string.
                  Optional: False
    """
    text = str(text)
    color_codes = {
        "green": "0;255;0",
        "red": "255;0;0",
        "yellow": "255;255;0",
        "blue": "0;0;255",
        "magenta": "255;0;255",
        "cyan": "0;255;255",
        "white": "255;255;255",
        "black": "0;0;0",
        "gray": "128;128;128",
        "lightgray": "211;211;211",
        "darkgray": "169;169;169",
        "lightblue": "173;216;230",
        "lightgreen": "144;238;144",
        "lightcyan": "224;255;255",
        "lightred": "255;182;193",
        "pink": "255;192;203",
    }

    if hex_color.lower() in color_codes:
        color = color_codes[hex_color.lower()]
    else:
        try:
            if hex_color[0] == "#":
                hex_color = hex_color[1:]
            if len(hex_color) != 6:
                raise ValueError("Hex color must be 6 characters long.")
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            color = f"{r};{g};{b}"
        except ValueError as e:
            print(f"Error: {e}")
            return

    return(f"\033[38;2;{color}m{text}\033[0m")

def print_info_(text):
    """
    Print the text in blue and underlined.
    """
    text = str(text)
    print("\033[1;34;4m" + text + "\033[0m")
def print_debug_(text):
    """
    Print the text in cyan and underlined.
    """
    text = str(text)
    print("\033[1;36;4m" + text + "\033[0m")

def nice_print_(text):
    '''
    print the text in green and with a timestamp.
    '''
    text = str(text)
    print(f"\033[1;32;4m[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: {text}\033[0m")

def print_system_(text):
    '''
    print the text in underlined purple.
    '''
    text = str(text)
    print(f"\033[4;35;1mSystem:\033[0m {text}")


unsuported_characters = {
    "|": "",
    "/": "-",
    "\\": "-",
    ":": "-",
    "*": "",
    "?": "",
    '"': "'",
    "<": "",
    ">": "",
    "\n": "",
    "\t": "",
    "\x0b": "",  # Vertical tab
    "\x0c": "",  # Form feed
    "\r": "",   # Carriage return
    "\0": "",   # Null character
    "\x08": "", # Backspace
    "\x0e": "", # Shift Out
    "\x0f": "", # Shift In
}


def cuntinueYtv(url, output, resolution, pace, logging) -> bool:
    try:
        try:    
            yt = YouTube(url=url)
            stream = yt.streams.filter(resolution=resolution).first()
            filename = f"Kurumii.py-{yt.title}_{resolution}{'_[temp]' if pace else ''}.mp4".replace(" ","_").replace("|","")
            filename = filename.replace(" ", "_")\
                           .replace("|", "")\
                           .replace("/", "-")\
                           .replace("\\", "-")\
                           .replace(":", "-")\
                           .replace("*", "")\
                           .replace("?", "")\
                           .replace('"', "'")\
                           .replace("<", "")\
                           .replace(">", "")\
                           .replace("\n", "")\
                           .replace("\t", "")\
                           .replace("\x0b", "")\
                           .replace("\x0c", "")\
                           .replace("\r", "")\
                           .replace("\0", "")\
                           .replace("\x08", "")\
                           .replace("\x0e", "")\
                           .replace("\x0f", "")

            output_path = output+f"\\{filename}"
            filename_edit = f"Kurumii.py-{yt.title}_{resolution}_x{pace}.mp4".replace(" ","_").replace("|","")
            filename_edit = filename_edit.replace(" ", "_")\
                           .replace("|", "")\
                           .replace("/", "-")\
                           .replace("\\", "-")\
                           .replace(":", "-")\
                           .replace("*", "")\
                           .replace("?", "")\
                           .replace('"', "'")\
                           .replace("<", "")\
                           .replace(">", "")\
                           .replace("\n", "")\
                           .replace("\t", "")\
                           .replace("\x0b", "")\
                           .replace("\x0c", "")\
                           .replace("\r", "")\
                           .replace("\0", "")\
                           .replace("\x08", "")\
                           .replace("\x0e", "")\
                           .replace("\x0f", "")
            if logging == True:
                nice_print_(f"Downloading: '{yt.title}' [{yt.watch_url}]")
            stream.download(filename=filename, output_path=output)
            if logging == True:
                print_info_("Done")
                if pace:
                    print_system_("Download comleted")
        except Exception as e:
            if logging == True:
                print_red_(e)
            return(False)
        if not pace:
            return(True,filename)
        else:
            if logging == True:
                print_info_(f"Applying pace change of x{pace}...")
            input_file = f"{output}\\{filename}"
            output_filepath = f"{output}\\{filename_edit}"
            speed = pace
            clip = VideoFileClip(input_file, verbose=False)
            clip = clip.set_fps(clip.fps * speed)
            final = clip.fx(vfx.speedx, speed)

            # Save video clip
            final.write_videofile(output_filepath)
            os.remove(path=f"{output}\\{filename}")
            if logging == True:
                print_info_("Done")
                print_system_("Download completed")
            return(True, filename_edit)
    except Exception as e:
        if logging == True:
            print_red_(e)
        return(False)






def cuntinueYtpl(url, output, pace, resolution, logging) -> bool:
    try:
        pl = Playlist(url=url)
        if logging == True:
                print_system_(f"Downloading {len(pl)} videos...")
        for vids in pl:
            yt = YouTube(vids)
            stream = yt.streams.filter(resolution=resolution).first()
            filename = f"Kurumii.py-{yt.title}_{resolution}{'_[temp]' if pace else ''}.mp4".replace(" ","_")
            filename = filename.replace(" ", "_")\
                           .replace("|", "")\
                           .replace("/", "-")\
                           .replace("\\", "-")\
                           .replace(":", "-")\
                           .replace("*", "")\
                           .replace("?", "")\
                           .replace('"', "'")\
                           .replace("<", "")\
                           .replace(">", "")\
                           .replace("\n", "")\
                           .replace("\t", "")\
                           .replace("\x0b", "")\
                           .replace("\x0c", "")\
                           .replace("\r", "")\
                           .replace("\0", "")\
                           .replace("\x08", "")\
                           .replace("\x0e", "")\
                           .replace("\x0f", "")
            output_path = output+f"\\{filename}"
            filename_edit = f"Kurumii.py-{yt.title}_{resolution}_x{pace}.mp4".replace(" ","_")
            filename_edit = filename_edit.replace(" ", "_")\
                           .replace("|", "")\
                           .replace("/", "-")\
                           .replace("\\", "-")\
                           .replace(":", "-")\
                           .replace("*", "")\
                           .replace("?", "")\
                           .replace('"', "'")\
                           .replace("<", "")\
                           .replace(">", "")\
                           .replace("\n", "")\
                           .replace("\t", "")\
                           .replace("\x0b", "")\
                           .replace("\x0c", "")\
                           .replace("\r", "")\
                           .replace("\0", "")\
                           .replace("\x08", "")\
                           .replace("\x0e", "")\
                           .replace("\x0f", "")
            if logging == True:
                nice_print_(f"Downloading: '{yt.title} - [{yt.watch_url}]'")
            stream.download(output_path=output,filename=filename)
            if logging == True:
                print_info_("Done")
                if pace:
                    print_info_(f"Applying pace change of x{pace}...")
            if not pace:
                return(True,filename)
            else:
                input_file = f"{output}\\{filename}"
                output_filepath = f"{output}\\{filename_edit}"
                speed = pace
                clip = VideoFileClip(input_file, verbose=False)
                clip = clip.set_fps(clip.fps * speed)
                final = clip.fx(vfx.speedx, speed)
                final.write_videofile(output_filepath)
                os.remove(path=f"{output}\\{filename}")
                if logging == True:
                    print_info_("Done")
                return(True, filename_edit)
        print_system_("Download comleted")
        return(True)
            
            
            

    except Exception as e:
        if logging == True:
            print_red_(e)
        return(False)
    
def cuntinueYtch(url, output, pace, resolution, logging) -> bool:
    #lets write the code that scrapes the YouTube channel and asks for the pace of the video.
    #try:
        print_debug_("running")
        ch = Channel(url)
        print_debug_(ch.channel_name, ch.description)
        print(ch.videos)
        for vid in ch.videos:
            print(vid.title)
    # except:
    #     pass



def downloadYoutube(url: str, output: str, resolution:str="720p",pace=None, logging:bool=True) -> bool:
    """
    Download and change the pace of a YouTube video.

    Args:
        - url (str):
            - YouTube video link (single download)
            - YouTube playlist link (downloads the playlist)
            - YouTube channel link (channel scraping) [Not supported]

        - output (str):
            - The full path to the output folder

        - resolution (str):
            -The resolution of the downloaded video [default 720p]

        - pace (float) [optional]: 
            - pace > 1:
                - speed increases
            - pace == 1:
                - normal speed (not recommended)
            - pace < 1:
                - speed decreased
            - pace == None: [default]
                - normal speed

        - logging (bool):
            - If the module should log the proccess [default True]

        Note: If you enter an invalid pace value, it will be set to None.

    Returns:
        - bool: whether the download was successful (True) or not (False).
        - Nothing: if the program fails completely.
    """
    if pace:
        if pace == 1.0:
            pace = None
        try:
            pace = float(pace)
        except:
            pace = None
            print_red_("Invalid pace, continuing without playback-speed change")
    if not check_link_existence(url):
        print_colored_(text="Invalid link", hex_color="ff0000")
        return False
    
    else:
        ltype = check_link_type(url=url)
        if ltype == "channel":
            #result = cuntinueYtch(url=url, output=output, resolution=resolution, pace=pace,logging=logging)
            print_red_("Due to pytube not supporting channels, this function can not be used.")
            return(False)
           
        elif ltype == "video":
            result = cuntinueYtv(url=url, output=output, resolution=resolution, pace=pace,logging=logging)
            return(result)
         
        elif ltype == "playlist":
            result =  cuntinueYtpl(url=url, output=output, resolution=resolution, pace=pace,logging=logging)
            return(result)