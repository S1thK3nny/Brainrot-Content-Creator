import os
from playwright.async_api import async_playwright, Browser, Page

async def capturePost(page: Page, things_to_say) -> None:
    page_title = await page.inner_text("h1")  # Grabs the title of the post
    things_to_say.append(page_title)

    posts = page.locator("shreddit-post")
    op = await posts.get_attribute("author")
    datetime = (await posts.locator("time").get_attribute("datetime")).replace(":", "_")
    dir = os.getcwd() + "/" + op + " - " + datetime
    await posts.first.screenshot(path=os.path.join(dir + "/images/post", "post.png"))
    return dir

async def captureComments(page: Page, dir, things_to_say) -> None:
    comments = page.locator("shreddit-comment")
    count = await comments.count()
    print(f"Grabbed {count} comments, filtering now...\n--------------------------------------------------")

    file_num = 0  # Use file_num instead of i to match it up with the audio files
    for i in range(count):
        comment = []
        comment_depth = await comments.nth(i).get_attribute("depth")
        print(f"Comment {i} has a depth of {comment_depth}")

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
                file_num += 1
                await comments.nth(i).screenshot(path=os.path.join(dir + "/images/comments/", f"comment-{file_num}.png"))
        else:
            print("Comment " + str(i) + " is not a top comment!")

    print("--------------------------------------------------")

async def capture(browser: Browser, url: str, things_to_say) -> None:
    page = await browser.new_page()
    await page.goto(url)
    
    dir = await capturePost(page, things_to_say)
    await captureComments(page, dir, things_to_say)
    return dir

async def screenshot_and_convert(reddit_url, things_to_say) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        dir = await capture(browser, reddit_url, things_to_say)
        await browser.close()
    return dir