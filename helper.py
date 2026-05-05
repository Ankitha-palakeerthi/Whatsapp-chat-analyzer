from collections import Counter
import emoji
import pandas as pd

def fetch_stats(df):

    messages = df.shape[0]

    words = []
    for msg in df["message"]:
        words.extend(msg.split())

    media = df[df["message"] == "<Media omitted>"].shape[0]

    links = 0
    for msg in df["message"]:
        if "http" in msg:
            links += 1

    return {
        "messages": messages,
        "words": len(words),
        "media": media,
        "links": links
    }


def most_busy_users(df):

    return df["user"].value_counts().to_dict()


def common_words(df):

    words = []

    for msg in df["message"]:
        for word in msg.lower().split():
            words.append(word)

    return dict(Counter(words).most_common(10))


def emoji_helper(df):

    emojis = []

    for msg in df["message"]:
        for char in msg:
            if char in emoji.EMOJI_DATA:
                emojis.append(char)

    return dict(Counter(emojis).most_common(10))


def monthly_timeline(df):

    months = []

    for date in df["date"]:
        months.append(date[:5])

    return dict(Counter(months))
