import argparse
import asyncio

from reddit.reddit_converter import start_browser_instance_reddit
from reddit.tts_saver import save_text_as_mp3
from reddit.convert_to_mp4 import to_video

from twitch.clip_scraper import start_browser_instance_twitch
from twitch.clip_editing import initialize_editing

from utils import save_text, write_to_info_file
from uploader import upload_tiktok

things_to_say = []

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process Reddit or Streamscharts content.')
    parser.add_argument('-m', '--mode', type=str, default='Reddit', choices=['Reddit', 'Twitch'], help="Choose the mod, depending on what kind of video you need. Default is Reddit")
    parser.add_argument('-l', '--link', type=str, default=None, help='URL of the Reddit post or Streamscharts clip. If not provided, a random one will be selected.')
    parser.add_argument("-o", '--open', action='store_true', help='Whether you want to open the video after it is done saving or not. False by default.')

    parser.add_argument('-sub', '--subreddit', type=str, default=None, help='Provide a subreddit to get a random post from it (this is overwritten by LINK). If not provided, a random subreddit will be selected.\nExample: "https://www.reddit.com/r/AskReddit/"')
    parser.add_argument("-lang", '--language', type=str, default='en', help='The language of the Twitch clip you want. Default is en')

    # parser.add_argument("-t", '--tiktok', action='store_true', help='Automatically upload it to TikTok as long as the cookies are present in resources/cookies/')
    # parser.add_argument("-y", '--youtube', action='store_true', help='Automatically upload it to YouTube as long as the cookies are present in resources/cookies/')
    return parser.parse_args()

async def handle_reddit(args) -> None:
    dir = await start_browser_instance_reddit(args.link, args.subreddit, things_to_say)
    save_text_as_mp3(dir, things_to_say)

    title = things_to_say[0] + " #shorts #askreddit #reels #redditrecap #tiktok"
    write_to_info_file(dir, title)
    to_video(dir, args.open)
    save_text(dir, things_to_say)

async def handle_twitch(args) -> None:
    dir = await start_browser_instance_twitch(args.link, args.language)
    initialize_editing(dir, args.open, args.language)



async def main() -> None:
    args = parse_arguments()
    
    modes = {
        'Reddit': handle_reddit,
        'Twitch': handle_twitch
    }

    await modes[args.mode](args)

    # if args.tiktok:
    #    upload_tiktok(dir + "/result.mp4", title)

if __name__ == '__main__':
    asyncio.run(main())