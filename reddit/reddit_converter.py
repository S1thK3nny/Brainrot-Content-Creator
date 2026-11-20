import os
import random
import re
from utils import sprint
from playwright.async_api import async_playwright, Page

def get_random_subreddit():
    SUBREDDITS = [
        'https://www.reddit.com/r/askreddit/',
        'https://www.reddit.com/r/aww/',
        'https://www.reddit.com/r/funny/',
        'https://www.reddit.com/r/gaming/',
      #  'https://www.reddit.com/r/Jokes/',
        'https://www.reddit.com/r/memes/',
        'https://www.reddit.com/r/pics/',
        'https://www.reddit.com/r/Showerthoughts/',
        'https://www.reddit.com/r/todayilearned/',
        'https://www.reddit.com/r/popular/hot/?geo_filter=global'
    ]
    subreddit = random.choice([subreddit for subreddit in SUBREDDITS])
    sprint(f"Random Subreddit is {subreddit}")
    return subreddit

async def get_posts_and_dir(page: Page):
    posts = page.locator("shreddit-post")
    op = await posts.get_attribute("author")
    datetime = (await posts.locator("time").get_attribute("datetime")).replace(":", "_")
    out_dir = os.getcwd() + "/FINISHED/Reddit/" + op + " - " + datetime
    return posts, out_dir

async def capturePost(page: Page, things_to_say) -> None:
    page_title = await page.inner_text("h1")  # Grabs the title of the post
    things_to_say.append(page_title)
    posts, out_dir = await get_posts_and_dir(page)
    await posts.first.screenshot(path=os.path.join(out_dir + "/images/post", "post.png"))
    return out_dir

# TODO: Account for 0 comments
async def captureComments(page: Page, out_dir, things_to_say) -> None:
    comments = page.locator("shreddit-comment")
    count = await comments.count()
    print("\n--------------------------------------------------")
    sprint(f"Grabbed {count} comments, filtering now...")

    file_num = 0  # Use file_num instead of i to match it up with the audio files
    for i in range(count):
        comment = []
        comment_depth = await comments.nth(i).get_attribute("depth")
        author = await comments.nth(i).get_attribute("author")
        sprint(f"Comment {i} has a depth of {comment_depth}")

        # The int casting is incredibly important!
        if int(comment_depth) == 0 and not author=="AutoModerator":
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
                await comments.nth(i).screenshot(path=os.path.join(out_dir + "/images/comments/", f"comment-{file_num}.png"))
                file_num += 1
        else:
            sprint("Comment " + str(i) + " is not a top comment!")

    print("--------------------------------------------------\n")

async def capture(page, url: str, things_to_say) -> None:
    await page.goto(url)
    out_dir = await capturePost(page, things_to_say)
    await captureComments(page, out_dir, things_to_say)
    return out_dir



# Needs a rewrite, works for now.
async def choose_random_reddit_post(page: Page, subreddit: str):
    while True:
        if subreddit is None:
            subreddit = get_random_subreddit()
        await page.goto(subreddit)
        locator = page.locator("shreddit-post")
        posts = await locator.element_handles()
        random_post = random.choice(posts)
        post_url = await random_post.get_attribute("permalink")
        author = await random_post.get_attribute("author")

        sprint(author)
        
        if not re.findall(r'(?i)mod', author):
            return "https://www.reddit.com" + post_url

async def screenshot_and_convert(page: Page, reddit_url=None, subreddit=None, things_to_say=None) -> None:
    while True:
        if reddit_url is None:
            reddit_url = await choose_random_reddit_post(page, subreddit)
        sprint(f"Chosen Reddit URL: {reddit_url}")
        await page.goto(reddit_url)

        _, out_dir = await get_posts_and_dir(page)
        if os.path.exists(out_dir + "/result.mp4"):
            sprint(f"{out_dir} exists already, choosing another post...")
            reddit_url = None  # Reset reddit_url to choose another post
        else:
            out_dir = await capture(page, reddit_url, things_to_say)
            break  # Break the loop once a valid post is found

    return out_dir

async def start_browser_instance_reddit(reddit_url, subreddit, things_to_say):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ua = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/69.0.3497.100 Safari/537.36"
        )
        page = await browser.new_page(user_agent=ua)
        out_dir = await screenshot_and_convert(page, reddit_url, subreddit, things_to_say)
        await browser.close()
    return out_dir