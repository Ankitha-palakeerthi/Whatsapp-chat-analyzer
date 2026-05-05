import pandas as pd
import re

def analyze_chat(chat_text):

    messages = chat_text.split("\n")
    users = []
    msgs = []

    for message in messages:
        entry = re.split(r" - ", message)
        if len(entry) > 1:
            user_msg = entry[1]
            user = user_msg.split(":")[0]
            msg = ":".join(user_msg.split(":")[1:])
            users.append(user)
            msgs.append(msg)

    df = pd.DataFrame({"user":users,"message":msgs})

    total_messages = df.shape[0]
    total_words = sum(df["message"].apply(lambda x: len(x.split())))
    media_messages = df[df["message"].str.contains("omitted",case=False)].shape[0]
    links_shared = df["message"].str.contains("http").sum()

    return total_messages,total_words,media_messages,links_shared
