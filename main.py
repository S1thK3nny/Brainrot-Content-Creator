import asyncio
from reddit_converter import screenshot_and_convert
from tts_saver import save_text_as_mp3
from convert_to_mp4 import to_video

things_to_say = []

async def main() -> None:
    dir = await screenshot_and_convert("https://www.reddit.com/r/AskReddit/comments/18va8xf/what_was_your_biggest_fuckup_this_year/", things_to_say)
    save_text_as_mp3(dir, things_to_say)
    to_video(dir)

if __name__ == '__main__':
    asyncio.run(main()) 