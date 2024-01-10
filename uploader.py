from tiktok_uploader.upload import upload_video
import os
from utils import check_file_exists, sprint

def upload_tiktok(video, title):
    print("\n--------------------------------------------------")
    sprint("Uploading video...now!")
    cookies_dir = os.getcwd() + "/resources/cookies/www.tiktok.com_cookies.txt"

    if not check_file_exists(video, "Video"):
        return
    if not check_file_exists(cookies_dir, "Cookies"):
        return
    
    upload_video(filename=video, description=title, cookies=cookies_dir)
    print("--------------------------------------------------\n")