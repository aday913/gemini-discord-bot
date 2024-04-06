import logging

import discord
import google.generativeai as genai
from yaml import Loader, load

log = logging.getLogger(__name__)

# Discord client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# Gemini client
def get_gemini(api_key):
    return genai.configure(api_key=api_key)


with open("config.yaml", "r") as yml:
    config = load(yml, Loader=Loader)
gemini = get_gemini(config["gemini_api_key"])
model = genai.GenerativeModel("gemini-pro")


@client.event
async def on_ready():
    log.info(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:  # Prevent bot responding to itself
        return

    # Mention-based interaction
    if client.user.mentioned_in(message):
        user_query = message.content.split(f"<@{client.user.id}> ")[1] 
        user_query = user_query + '. Limit your response to less than 1900 characters.'
        log.info(
            f"Gemini bot mentioned, got prompt from user {message.author}:\n {user_query}"
        )
        response = await call_gemini(user_query)
        await message.channel.send(response)

async def call_gemini(prompt):
    response = model.generate_content(prompt)
    log.info(f"Got the following candidates from Gemini:\n {response.candidates}")
    return response.text

@client.event
async def on_thread_create(thread):
    log.info(f'Thread {thread.name} created at {thread.created_at}')
    await thread.join()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    log = logging.getLogger(__name__)

    with open("config.yaml", "r") as yml:
        config = load(yml, Loader=Loader)
    client.run(config["discord_bot_token"])
