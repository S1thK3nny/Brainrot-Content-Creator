import os
import httpx
import random
from utils import sprint, title_to_folder_name
from playwright.async_api import async_playwright, Page

link_7days = "https://streamscharts.com/clips?language="
link_today = "https://streamscharts.com/clips?time=today&language="

async def choose_random_clip(page: Page, language: str):
    page.set_default_timeout(3000)
    await page.goto(link_7days + language)
    sprint("No url given, choosing random clip!")

    # Get all divs under the specified parent
    locator = page.locator('xpath=/html/body/main/div[5]/div/div[2]/div[1]/div[1]/div[3]//div')
    test = await locator.element_handles()
    sprint(f"Found {len(test)} clips, choosing a random one now.")

    # Select a random div and click it
    random_div = random.choice(test)
    await random_div.click()

    await page.wait_for_load_state()
    newURL = page.url

    return newURL

async def createDir(page: Page):
    page.set_default_timeout(3000)
    try:
        iframe = page.frame_locator('.ratio_container-inner')
        element1 = iframe.locator('xpath=/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[4]/div/div[1]/div[2]/div/div/div[2]/div/p[1]/a[1]')
        streamer = await element1.inner_text()

        element2 = iframe.locator('xpath=/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[4]/div/div[1]/div[2]/div/div/div[2]/div/div/p/a')
        title = await element2.inner_text()
        sprint(f"Streamer: {streamer}\tTitle: {title}")

        dir = os.path.join(os.getcwd(), "FINISHED", "Twitch", title_to_folder_name(title + " - " + streamer))
        os.makedirs(dir, exist_ok=True)
        return dir

    except Exception as e:
        sprint(f"An error occurred: {e}")
        return None

async def initialize_scraping(page: Page, clip_url: str, language: str):
    while True:
        if clip_url is None:
            clip_url = await choose_random_clip(page, language)

        sprint(f"Chosen Clip: {clip_url}")
        await page.goto(clip_url)

        dir = await createDir(page)

        if dir is None:
            return None
        
        if os.path.exists(dir + "/final_video_with_subtitles.mp4"):
                sprint(f"{dir} exists already, choosing another post...")
                clip_url = None  # Reset clip_url to choose another post
        else:
            links = page.locator("xpath=/html/body/main/div[5]/div/div[3]/div/div[2]/div[1]/div/a")
            sprint(f"Grabbed the dl link, downloading now...")
            response = httpx.get(await links.get_attribute('href'))
            with open(os.path.join(dir, 'clip.mp4'), 'wb') as f:
                f.write(response.content)
            break  # Break the loop once a valid post is found
    return dir

async def start_browser_instance_twitch(clip_url: str, language: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        dir = await initialize_scraping(page, clip_url, language)

        if dir is None:
            # Restart the browser instance
            await browser.close()
            return await start_browser_instance_twitch(clip_url, language)

        await browser.close()
    return dir