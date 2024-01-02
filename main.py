import argparse
import asyncio
from reddit_converter import start_browser_instance
from tts_saver import save_text_as_mp3
from convert_to_mp4 import to_video
from utils import save_text, write_to_info_file
from uploader import upload_tiktok

things_to_say = []

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process Reddit content.')
    parser.add_argument('-l', '--link', type=str, default=None, help='URL of the Reddit post. If not provided, a random post will be selected.')
    parser.add_argument("-o", '--open', action='store_true', help='Whether you want to open the video after it is done saving or not. False by default.')
    parser.add_argument("-t", '--tiktok', action='store_true', help='Automatically upload it to TikTok as long as the cookies are present in resources/cookies/')
    parser.add_argument("-y", '--youtube', action='store_true', help='Automatically upload it to YouTube as long as the cookies are present in resources/cookies/')

    return parser.parse_args()

async def main() -> None:
    args = parse_arguments()
    dir, subreddit_url = await start_browser_instance(args.link, things_to_say)
    save_text_as_mp3(dir, things_to_say)

    title = things_to_say[0] + " " + subreddit_url.replace('https://www.reddit.com/', '') + " #shorts #askreddit #reels #redditrecap #tiktok"
    write_to_info_file(dir, title)
    to_video(dir, args.open)
    save_text(dir, things_to_say)

    if args.tiktok:
        upload_tiktok(dir + "/result.mp4", title)

if __name__ == '__main__':
    asyncio.run(main())