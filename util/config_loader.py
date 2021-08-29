cfg = open('bot.cfg')

values = {}

for lines in cfg.readlines():
    if lines.strip()[0] == '#':
        continue
    key_value = lines.split('=')
    values[key_value[0].strip()] = key_value[1].strip()

    if __name__ == '__main__':
        print(key_value[0].strip(), '→', '"' +
              values[key_value[0].strip()] + '"')


def get(key: str) -> str:
    return values.get(key)
