import os
import random
from tiktokvoice import tts
from utils import sprint, strip_special_chars

def get_random_voice():
    VOICES = [
        # ENGLISH VOICES
        'en_au_001',                  # English AU - Female
        'en_au_002',                  # English AU - Male
        'en_uk_001',                  # English UK - Male 1
        'en_uk_003',                  # English UK - Male 2
        'en_us_001',                  # English US - Female (Int. 1)
        'en_us_002',                  # English US - Female (Int. 2)
        'en_us_006',                  # English US - Male 1
        'en_us_007',                  # English US - Male 2
        'en_us_009',                  # English US - Male 3
        'en_us_010',                  # English US - Male 4
    ]
    return random.choice([voice for voice in VOICES])

def save_text_as_mp3(dir, things_to_say):
    if not os.path.exists(dir + "/audio/"):
        os.makedirs(dir + "/audio/")
        os.makedirs(dir + "/audio/post/")
        os.makedirs(dir + "/audio/comments/")
    for i in range(len(things_to_say)):
        if i == 0:
            post_dir = dir + "/audio/post/post.mp3"
            if os.path.exists(post_dir):
                sprint("Post.mp3 exists, skipping...")
                continue
            tts(strip_special_chars(things_to_say[i]), get_random_voice(), post_dir, False)
        else:
            for j in range(len(things_to_say[i])):
                comment_dir = dir + "/audio/comments/" + f"comment-{i-1}_{j}.mp3"
                if os.path.exists(comment_dir):
                    sprint(f"comment-{i-1}_{j}.mp3 exists, skipping...")
                    continue
                tts(strip_special_chars(things_to_say[i][j]), get_random_voice(), comment_dir, False)