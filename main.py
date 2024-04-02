import logging

import discord
import google.generativeai as genai
from yaml import Loader, load

log = logging.getLogger(__name__)

# Discord client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


def get_gemini(api_key):
    # log.info('Attempting to connect to gemini api')
    return genai.configure(api_key=api_key)


@client.event
async def on_ready():
    gemini = get_gemini("")
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(m.name)
    print(f"Logged in as {client.user}")
    print(f"Gemini object: {gemini}")


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
    # ... (Implement your Gemini API request logic here) ...
    return gemini_response


if __name__ == "__main__":
    log = logging.basicConfig(level=logging.DEBUG)

    with open("config.yaml", "r") as yml:
        config = load(yml, Loader=Loader)
    client.run(config["discord_bot_token"])
