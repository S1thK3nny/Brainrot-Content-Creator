import asyncio
from reddit_converter import start_browser_instance
from tts_saver import save_text_as_mp3
from convert_to_mp4 import to_video

things_to_say = []

async def main() -> None:
    # dir = await start_browser_instance("https://www.reddit.com/r/AskReddit/comments/18w4yp1/how_have_you_almost_died/", things_to_say)
    dir = await start_browser_instance(None, things_to_say)
    save_text_as_mp3(dir, things_to_say)
    to_video(dir)

if __name__ == '__main__':
    asyncio.run(main()) 