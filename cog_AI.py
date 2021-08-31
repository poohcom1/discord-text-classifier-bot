import os
import random
import util.regex
import util.config_loader as cfg
from util.cli_util import progress
from load_model import load_model, predict
import discord
from discord.ext import commands

# Options
data_dir = cfg.get('data_dir_name')
train_dir = os.path.join(data_dir, cfg.get('train_dir_name'))
test_dir = os.path.join(data_dir, cfg.get('test_dir_name'))

# Functions
short_sentence_model, class_names = load_model('model1')
long_sentence_model, _ = load_model('model2')


def message_filter(message: str) -> bool:
    if not message[0].isalnum():
        return False

    return True


async def retrieve_messages(channel: discord.TextChannel):
    print('Retrieving from', channel.name + '...')
    messages = await channel.history(limit=None).flatten()
    for i, message in enumerate(messages):
        save_message(message)
        progress(i + 1, len(messages))


def save_message(message: discord.Message):
    # Ignore bots
    if message.author.bot or message.content.strip() == '' or not message_filter(message.content):
        return

    id = str(message.id)
    user_id = str(message.author.id)
    filename = id + '.txt'
    dir = train_dir if random.random() > float(
        cfg.get('test_percentage')) else test_dir

    # Create folder if user folder doesn't exist
    if user_id not in os.listdir(dir):
        os.mkdir(os.path.join(dir, user_id))

    # Skip if file already exists
    if filename in os.listdir(os.path.join(dir, user_id)):
        return

    try:
        file = open(os.path.join(dir, user_id, filename), 'w', encoding='utf8')
        file.write(util.regex.message_standardize(message.content))
        file.close()
    except:
        pass


class AI(commands.Cog):
    def __init__(self, client):
        self.client = client

        if data_dir not in os.listdir():
            os.mkdir(data_dir)

        if cfg.get('train_dir_name') not in os.listdir(data_dir):
            os.mkdir(train_dir)

        if cfg.get('test_dir_name') not in os.listdir(data_dir):
            os.mkdir(test_dir)

    @commands.command(brief="🤔")
    async def who(self, ctx, arg):
        async with ctx.typing():
            user_id = ''
            if len(arg.split()) > 2:
                user_id = predict(arg, long_sentence_model, class_names)
            else:
                user_id = predict(arg, short_sentence_model, class_names)

            try:
                user = await self.client.fetch_user(user_id)

                await ctx.send("Sounds like something **@" + user.display_name + "** would say")
            except Exception as e:
                print(e)
                await ctx.send('idk lmao')

    @commands.command(brief="Refetch all messages into database")
    async def train(self, ctx):
        await ctx.send("Hacking everyone's account...")
        try:
            channels = self.client.get_all_channels()

            for channel in channels:
                if type(channel) is discord.TextChannel:
                    await retrieve_messages(channel)
        except:
            await ctx.send('Whoops I fucked up')
            return

        await ctx.send("Finished extracting data")

    @commands.command()
    async def users(self, ctx):
        async with ctx.typing():
            usernames = []
            for user_id in class_names:
                user = await self.client.fetch_user(user_id)
                usernames.append(user.display_name)

            await ctx.send(usernames)
