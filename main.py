import os
import random
from util.cli_util import progress
import util.config_loader as cfg
import discord


# Options
data_dir = cfg.get('data_dir_name')
train_dir = os.path.join(data_dir, cfg.get('train_dir_name'))
test_dir = os.path.join(data_dir, cfg.get('test_dir_name'))


# Functions


async def retrieve_messages(channel: discord.TextChannel):
    print('Retrieving from', channel.name + '...')
    messages = await channel.history(limit=None).flatten()
    for i, message in enumerate(messages):
        save_message(message)
        progress(i + 1, len(messages))


def save_message(message: discord.Message):
    # Ignore bots
    if message.author.bot or message.content.strip() == '':
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
        file.write(message.content)
        file.close()
    except:
        pass


class MyClient(discord.Client):

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

        if data_dir not in os.listdir():
            os.mkdir(data_dir)

        if cfg.get('train_dir_name') not in os.listdir(data_dir):
            os.mkdir(train_dir)

        if cfg.get('test_dir_name') not in os.listdir(data_dir):
            os.mkdir(test_dir)

        channels = self.get_all_channels()

        for channel in channels:
            if type(channel) is discord.TextChannel:
                await retrieve_messages(channel)

        print("Finished extracting data")

    async def on_message(self, message):
        #print('Message from {0.author}: {0.content}'.format(message))
        pass


client = MyClient()
client.run(cfg.get('token'))
