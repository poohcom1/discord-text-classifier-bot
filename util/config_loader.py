cfg = open('bot.cfg')

values = {}

for line in cfg.readlines():
    if line.strip() == '' or line.strip()[0] == '#':
        continue
    key_value = line.split('=')
    values[key_value[0].strip()] = key_value[1].strip()

    if __name__ == '__main__':
        print(key_value[0].strip(), '→', '"' +
              values[key_value[0].strip()] + '"')


def get(key: str) -> str:
    return values.get(key)


def get_int(key: str) -> int:
    return int(get(key))
