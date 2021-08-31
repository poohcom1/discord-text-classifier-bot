

def parse_mention(mention: str) -> int:
    return int(''.join(chr for chr in mention if chr.isdigit()))
