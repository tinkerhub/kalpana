import re
import random

def split_into_sentences(text: str) -> list:
    sentences = re.split('(\n\n)', text)
    return sentences

def wait_response():
    responses = ["hold on!", "Checking...", "ippo parayam"]
    return random.choice(responses)