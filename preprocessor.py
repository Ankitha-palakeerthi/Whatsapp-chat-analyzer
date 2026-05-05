import re
import pandas as pd

def preprocess(data):

    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({
        "user_message": messages,
        "date": dates
    })

    users = []
    messages = []

    for msg in df['user_message']:
        entry = re.split(r'(\w+?):\s', msg)

        if len(entry) > 2:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append("group_notification")
            messages.append(msg)

    df["user"] = users
    df["message"] = messages

    return df
