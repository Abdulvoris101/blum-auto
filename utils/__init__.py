import re
from urllib.parse import urlparse


def getProxies():
    proxies = []

    with open("apps/common/src/proxies.txt", 'r') as file:
        for line in file:
            proxies.append(line.strip())

    return proxies



# Extract inline buttons
def extractInlineButtonsFromText(text):
    text_parts = re.split(r'\./', text)
    text_parts = text_parts[1:]
    text_parts = list(map(lambda part: re.sub(r'\n', '', part), text_parts))

    buttons = []

    for text in text_parts:
        button_kb = text.split('-')
        buttons.append({"name": button_kb[0], "callback_url": button_kb[1]})

    return buttons


def containsAnyWord(text, word_list):
    if text is not None:
        lowercase_text = text.lower()
        for word in word_list:
            if word.lower() in lowercase_text:
                return True

    return False

