import re

def split_into_sentences(text: str) -> list:
    sentences = re.split('(\n\n)', text)
    return sentences
