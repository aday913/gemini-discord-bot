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

thread_conversation_history = {}


@client.event
async def on_ready():
    log.info(f"Logged in as {client.user}")


@client.event
async def on_thread_create(thread):
    log.info(f"Thread {thread.name} with id {thread.id} created at {thread.created_at}")
    thread_conversation_history[thread.id] = []


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:  # Prevent bot responding to itself
        return

    # Mention-based interaction
    if not client.user.mentioned_in(message):
        return

    # Instantiate a "none" thread id for now
    thread_id = None

    # Format the user's question to ask for markdown, separate large blocks, etc.
    user_query = format_user_query(message)

    # If the message comes from a thread, we need to grab the ai chat history
    if message.channel.type in [
        discord.ChannelType.public_thread,
        discord.ChannelType.private_thread,
    ]:

        # TODO: use previous messages from the thread to build history rather than keeping it saved?
        # previous_messages = [i.content async for i in message.channel.history(limit=100)
        # log.info(f'Previous messages: {previous_messages}')

        user_query = await handle_thread_message(message, user_query)
        thread_id = message.channel.id

    # Get gemini's response
    response = await call_gemini(user_query, thread_id)

    # If the message isn't too big we just send it. Otherwise, parse it accordingly
    if len(response) < 1900:
        await message.channel.send(response)
        return
    else:
        await send_large_message(response, message)
        return


def format_user_query(message):
    user_query = message.content.split(f"<@{client.user.id}> ")[1]
    user_query = (
        user_query
        + ". Format your response to be in markdown. \
        If your resposne is longer than 1900 characters, \
        please separate each ~1200 character blocks with a newline character"
    )
    log.info(
        f"Gemini bot mentioned, got prompt from user {message.author}:\n {user_query}"
    )
    return user_query


async def handle_thread_message(message, user_query: str):
    thread_id = message.channel.id
    if thread_id not in list(thread_conversation_history.keys()):
        log.info(f"Thread ID {thread_id} not found in history, adding")
        thread_conversation_history[thread_id] = []
    formatted_message = {"role": "user", "parts": [user_query]}
    thread_conversation_history[thread_id].append(formatted_message)
    return thread_conversation_history[thread_id]


async def send_large_message(gemini_response, message):
    temp_message = ""
    split_response = gemini_response.split("\n")
    for i in range(len(split_response)):
        temp_message = temp_message + f"{split_response[i]}\n"
        if len(temp_message) > 1500:
            await message.channel.send(temp_message)
            temp_message = ""
    if temp_message != "":
        await message.channel.send(temp_message)
    return


async def call_gemini(prompt, thread_id):
    log.info(f"Using the following prompt when calling gemini api: {prompt}")
    response = model.generate_content(prompt)
    log.info(f"Got the following candidates from Gemini:\n {response.candidates}")
    first_candidate = response.candidates[0]
    if thread_id:
        thread_conversation_history[thread_id].append(first_candidate.content)
    return response.text


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    log = logging.getLogger(__name__)

    with open("config.yaml", "r") as yml:
        config = load(yml, Loader=Loader)
    client.run(config["discord_bot_token"])
