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
model = genai.GenerativeModel('gemini-pro')


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:  # Prevent bot responding to itself
        return

    # Mention-based interaction
    if client.user.mentioned_in(message):
        user_query = message.content.split(f"<@{client.user.id}> ")[1]
        response = await call_gemini(user_query)
        await message.channel.send(response)  # Handle image responses if needed

    # ... (Thread-based interaction code - more complex!) ...


async def call_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text


if __name__ == "__main__":
    log = logging.basicConfig(level=logging.DEBUG)

    with open("config.yaml", "r") as yml:
        config = load(yml, Loader=Loader)
    client.run(config["discord_bot_token"])
