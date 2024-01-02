import os
import random
from utils import sprint
from playwright.async_api import async_playwright, Page

async def get_posts_and_dir(page: Page):
    posts = page.locator("shreddit-post")
    op = await posts.get_attribute("author")
    datetime = (await posts.locator("time").get_attribute("datetime")).replace(":", "_")
    dir = os.getcwd() + "/" + op + " - " + datetime
    return posts, dir

async def capturePost(page: Page, things_to_say) -> None:
    page_title = await page.inner_text("h1")  # Grabs the title of the post
    things_to_say.append(page_title)
    posts, dir = await get_posts_and_dir(page)
    await posts.first.screenshot(path=os.path.join(dir + "/images/post", "post.png"))
    return dir

async def captureComments(page: Page, dir, things_to_say) -> None:
    comments = page.locator("shreddit-comment")
    count = await comments.count()
    print("\n--------------------------------------------------")
    sprint(f"Grabbed {count} comments, filtering now...")

    file_num = 0  # Use file_num instead of i to match it up with the audio files
    for i in range(count):
        comment = []
        comment_depth = await comments.nth(i).get_attribute("depth")
        sprint(f"Comment {i} has a depth of {comment_depth}")

        # The int casting is incredibly important!
        if int(comment_depth) == 0:
            paragraphs = await comments.nth(i).locator('p').all()
            for p in paragraphs:
                text = (await p.inner_text()).strip()  # Strip whitespace
                # Check if the stripped text is not empty
                if text:
                    comment.append(text)
                else:
                    continue
            if comment:  # Check if the comment list is not empty
                things_to_say.append(comment)
                await comments.nth(i).screenshot(path=os.path.join(dir + "/images/comments/", f"comment-{file_num}.png"))
                file_num += 1
        else:
            sprint("Comment " + str(i) + " is not a top comment!")

    print("--------------------------------------------------\n")

async def capture(page, url: str, things_to_say) -> None:
    await page.goto(url)
    dir = await capturePost(page, things_to_say)
    await captureComments(page, dir, things_to_say)
    return dir



# Needs a rewrite, works for now.
async def choose_random_askreddit_post(page):
    subreddit_url = "https://www.reddit.com/r/askreddit/"
    await page.goto(subreddit_url)
    locator = page.locator("shreddit-post")
    posts = await locator.element_handles()
    random_post = random.choice(posts)
    post_url = await random_post.get_attribute("content-href")
    return post_url

async def screenshot_and_convert(page, reddit_url=None, things_to_say=None) -> None:
    while True:
        if reddit_url is None:
            reddit_url = await choose_random_askreddit_post(page)
        sprint(f"Chosen Reddit URL: {reddit_url}")
        await page.goto(reddit_url)

        _, dir = await get_posts_and_dir(page)
        if os.path.exists(dir + "/result.mp4"):
            sprint(f"{dir} exists already, choosing another post...")
            reddit_url = None  # Reset reddit_url to choose another post
        else:
            dir = await capture(page, reddit_url, things_to_say)
            break  # Break the loop once a valid post is found

    return dir

async def start_browser_instance(reddit_url, things_to_say):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        dir = await screenshot_and_convert(page, reddit_url, things_to_say)
        await browser.close()
    return dir