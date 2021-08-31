import os
from typing import List
from collections import Counter
import util.config_loader as cfg
from util.discord_util import parse_mention
from discord.ext import commands

# Options
data_dir = cfg.get('data_dir_name')
train_dir = os.path.join(data_dir, cfg.get('train_dir_name'))
test_dir = os.path.join(data_dir, cfg.get('test_dir_name'))

exclude_dir = os.path.join(data_dir, cfg.get('exclude_word_dir_name'))


def get_excluded_words() -> List[str]:
    with open(exclude_dir, 'r') as fp:
        return fp.read().splitlines()


class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client

        if cfg.get('exclude_word_dir_name') not in os.listdir(data_dir):
            with open(exclude_dir, 'w'):
                pass

    @commands.command(brief="Shows the top words the user types")
    async def words(self, ctx, *args):
        count = 10
        user_id = ctx.message.author.id
        detailed = False

        try:
            for arg in args:
                if arg.isdigit():
                    count = int(arg)
                elif arg == 'detailed':
                    detailed = True
                elif arg.startswith('<') and arg.endswith('>'):
                    user_id = parse_mention(arg)
        except:
            await ctx.send("I fucked up somewhere idk")
            return

        exclude_list = get_excluded_words()
        word_list = []

        async with ctx.typing():

            user_id = str(user_id)

            for dir in [train_dir, test_dir]:
                user_dir = os.path.join(dir, user_id)
                for file in os.listdir(user_dir):
                    file_dir = os.path.join(user_dir, file)
                    with open(file_dir, 'r') as file:
                        for line in file.readlines():
                            word_list += line.split()

            counter = Counter(word_list)

            top_words = counter.most_common(count + len(exclude_list))

            msg = "**%s**'s Top %d word list:\n" % ((await self.client.fetch_user(user_id)).display_name, count)
            i = 0
            for word_tuple in top_words:
                word = word_tuple[0]
                if i >= count:
                    break
                if word.lower() not in exclude_list:
                    msg += "%d. %s" % (i + 1, word)
                    if detailed:
                        msg += "\t(x%s)" % word_tuple[1]
                    msg += '\n'
                    i += 1

            await ctx.send(msg)

    @commands.command(brief="Add word to excluded word list")
    async def exclude(self, ctx, *words):
        added_words = ""
        for word in words:
            word = word.lower()
            with open(exclude_dir, 'a+') as fp:
                if word in fp.readlines():
                    continue
                else:
                    fp.write(word + '\n')
                    added_words += "'%s', " % (word)
        await ctx.send("Added %s to exclusion list" % (added_words[0:len(added_words)-2]))

    @commands.command(brief="Remove word from excluded word list")
    async def include(self, ctx, word: str):
        word = word.lower()
        word_list = get_excluded_words()

        if word not in word_list:
            await ctx.send("Word not in list!")
            return

        word_list.remove(word)

        with open(exclude_dir, 'w') as fp:
            fp.writelines(word_list)

        await ctx.send("Removed '%s' from exclusion list" % (word))
