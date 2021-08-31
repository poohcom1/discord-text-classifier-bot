import re


def message_standardize(message: str) -> str:
    message = re.sub(
        "((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)", '', message)

    message = re.sub("[^\x00-\x7F]+", '', message)
    return message


if __name__ == '__main__':
    print(message_standardize(input("Before: ")))
