import os
import random
from datetime import datetime
from bot.clients import bot, BOT_INFO, store
from bot.config import COMMIT_SHA, HF_SPACE_ID, HOSTING_LABEL, MODEL, RATE_LIMIT
from bot.ai import ask_ai
from bot.helpers import is_allowed, keep_typing, send_reply, should_respond
from bot.history import clear_history
from bot.preferences import get_provider, set_provider
from bot.rate_limit import is_rate_limited

# Verbose console logging for local dev and teaching. Enabled by
# BOT_VERBOSE_LOG=1 (run_local.py sets this automatically). Prints one
# line per inbound/outbound message so kids and teachers can see the
# conversation flow in their terminal while the bot is running.
VERBOSE_LOG = os.environ.get("BOT_VERBOSE_LOG", "").strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)


def _log(message, direction: str, text: str) -> None:
    """Print a one-line trace of a message in verbose mode.

    direction is "in" (user → bot) or "out" (bot → user). Text is
    truncated to 500 characters so long AI replies don't flood the
    terminal. Newlines are collapsed for single-line readability.
    """
    if not VERBOSE_LOG:
        return
    user = message.from_user
    user_name = (
        f"@{user.username}" if user.username else (user.first_name or f"user:{user.id}")
    )
    bot_name = f"@{BOT_INFO.username}"
    snippet = (text or "").replace("\n", " ").replace("\r", " ")
    if len(snippet) > 500:
        snippet = snippet[:500] + "..."
    if direction == "in":
        sender, receiver = user_name, bot_name
    else:
        sender, receiver = bot_name, user_name
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {sender} → {receiver}: {snippet}", flush=True)

@bot.message_handler(commands=["start"], func=is_allowed)
def cmd_start(message):
    prompt = f"""
    Generate a unique welcome message for a Telegram AI assistant named Felix.
    Greet the user {message.from_user.first_name}.
    Mention that the bot can answer questions, write code and help with learning.
    Mention /help.
    Keep it under 100 words.
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["fact"], func=is_allowed)
def cmd_fact(message):
    prompt = """
    Give one random interesting fact.
    It can be about science, technology, history, nature or space.
    Make it surprising and concise.
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)
   

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)
    
@bot.message_handler(commands=["joke"], func=is_allowed)
def cmd_joke(message):
    prompt = """
    Tell one random funny joke.

    Requirements:
    - Family friendly
    - Short and funny
    - No offensive content
    - Different every time
    - Add one fitting emoji
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

    @bot.message_handler(commands=["quote"], func=is_allowed)
    def cmd_joke(message):
     prompt = """
     Create one original motivational quote.

    Requirements:
    - Inspiring
    - Short
    - Positive
    - Different every time
    - Add one suitable emoji
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)


    @bot.message_handler(commands=["compliment"], func=is_allowed)
    def cmd_joke(message):
     prompt = """
      Give a friendly compliment.

    Requirements:
    - Positive and uplifting
    - Family friendly
    - Short
    - Different every time
    - Add one suitable emoji
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["roll"], func=is_allowed)
def cmd_roll(message):
    result = random.randint(1, 6)

    bot.send_message(
        message.chat.id,
        f"🎲 You rolled: {result}"
    )

@bot.message_handler(commands=["roast"], func=is_allowed)
def cmd_roast(message):
    name = (
        message.text.split(maxsplit=1)[1]
        if " " in message.text
        else "you"
    )

    prompt = f"""
    Write a short, playful, friendly roast of {name}.

    Requirements:
    - Funny
    - Family friendly
    - No insults, hate, or offensive content
    - Maximum 3 sentences
    - Add one fitting emoji
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["remember"], func=is_allowed)
def cmd_remember(message):
    note = message.text.split(maxsplit=1)[1].strip() if " " in message.text else ""

    if not note:
        bot.send_message(
            message.chat.id,
            "📝 Usage:\n/remember something important"
        )
        return

    store.set(f"note:{message.from_user.id}", note)

    prompt = f"""
    The user asked the bot to remember this:

    "{note}"

    Generate a short friendly response.

    Requirements:
    - Confirm the memory was saved
    - Briefly mention what was remembered
    - Sound natural and conversational
    - Use one emoji
    - Maximum 2 sentences
    - Different every time
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["recall"], func=is_allowed)
def cmd_recall(message):
    note = store.get(f"note:{message.from_user.id}")

    if not note:
        bot.send_message(
            message.chat.id,
            "🤔 I don't remember anything yet. Use /remember first."
        )
        return

    prompt = f"""
    The bot previously remembered:

    "{note}"

    Generate a friendly response telling the user what is remembered.

    Requirements:
    - Mention the memory
    - Natural conversational style
    - One emoji
    - Maximum 3 sentences
    - Different every time
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["forget"], func=is_allowed)
def cmd_forget(message):
    key = f"memories:{message.from_user.id}"

    memories = store.lrange(key, 0, -1)

    if not memories:
        bot.send_message(
            message.chat.id,
            "🤔 I don't have any memories stored."
        )
        return

    store.delete(key)

    prompt = f"""
    The user had {len(memories)} saved memories.

    Generate a friendly response confirming all memories were forgotten.

    Requirements:
    - Friendly
    - One emoji
    - Maximum 2 sentences
    - Different every time
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)
    

@bot.message_handler(commands=["help"], func=is_allowed)
def cmd_help(message):

    available_commands = """
    /start
    /help
    /reset
    /clear
    /about
    /fact
    /joke
    /quote
    /compliment
    /roll
    /roast <name>
    /remember
    /recall
    /forget
    """

    prompt = f"""
    You are FelixBot.

    Explain these commands in a friendly way:

    {available_commands}

    Keep the answer organized with emojis.
    End by encouraging the user to ask a question.
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)
    
@bot.message_handler(commands=["clear"], func=is_allowed)
def cmd_clear(message):
    user_id = message.from_user.id

    clear_history(user_id)

    prompt = """
    The user cleared the current conversation history.

    Generate a friendly response.

    Requirements:
    - Confirm the chat history was cleared
    - Explain that future messages start a fresh conversation
    - Friendly AI assistant tone
    - One emoji
    - Maximum 2 sentences
    - Different every time
    """

    try:
        reply = ask_ai(user_id, prompt)
    except Exception:
        reply = "🧹 Chat history cleared. Let's start a fresh conversation!"

    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["reset"], func=is_allowed)
def cmd_reset(message):
    user_id = message.from_user.id

    clear_history(user_id)

    try:
        store.delete(f"note:{user_id}")
        store.delete(f"memories:{user_id}")
    except Exception:
        pass

    prompt = """
    The user completely reset the assistant.

    Generate a friendly response.

    Requirements:
    - Confirm all conversation history was cleared
    - Confirm saved memories were removed
    - Encourage the user to start fresh
    - Use one emoji
    - Maximum 3 sentences
    - Different every time
    """

    try:
        reply = ask_ai(user_id, prompt)
    except Exception:
        reply = "✨ Everything has been reset. We're starting with a clean slate!"

    bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=["about"], func=is_allowed)
def cmd_about(message):

    provider = (
        get_provider(message.from_user.id)
        if HF_SPACE_ID
        else "main"
    )

    prompt = f"""
    Introduce yourself as FelixBot.

    Technical information:
    Model: {MODEL}
    Provider: {provider}
    Hosting: {HOSTING_LABEL}

    Explain:
    - who you are
    - what you can do
    - your personality
    - your capabilities

    Be engaging and professional.
    Use emojis.
    """

    reply = ask_ai(message.from_user.id, prompt)

    if COMMIT_SHA:
        reply += f"\n\n🔧 Version: {COMMIT_SHA}"

    bot.send_message(message.chat.id, reply)

    @bot.message_handler(commands=["model"], func=is_allowed)
    def cmd_model(message):
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) == 1:
            current = get_provider(message.from_user.id)
            bot.send_message(
                message.chat.id,
                f"Current provider: {current}\n\n"
                "Options:\n"
                "/model main — Cerebras (fast, multilingual, with memory)\n"
                "/model hf — ArmGPT (Armenian only, slow, no memory)",
            )
            return
        choice = parts[1].strip().lower()
        if choice not in ("main", "hf"):
            bot.send_message(
                message.chat.id, "Invalid choice. Use: /model main or /model hf"
            )
            return
        if not set_provider(message.from_user.id, choice):
            bot.send_message(
                message.chat.id, "Could not save preference. Try again later."
            )
            return
        if choice == "hf":
            bot.send_message(
                message.chat.id,
                "Switched to hf (ArmGPT).\n\n"
                "Note: this is a tiny base completion model trained only on Armenian text. "
                "It will continue whatever you write rather than answer questions, "
                "and it does not understand English. Replies take ~30-60s and there is no memory.",
            )
        else:
            bot.send_message(message.chat.id, "Switched to Main Provider.")


@bot.message_handler(content_types=["text"], func=is_allowed)
def handle_message(message):
    if not should_respond(message):
        return
    text = (message.text or "").replace(f"@{BOT_INFO.username}", "").strip()
    if not text:
        # Edited messages, forwards, or stickers-with-empty-caption can
        # arrive with no usable text. Don't burn rate-limit / AI calls on them.
        return
    _log(message, "in", text)
    if is_rate_limited(message.from_user.id):
        limit_msg = f"You've reached the daily limit of {RATE_LIMIT} messages. Try again tomorrow."
        bot.send_message(message.chat.id, limit_msg)
        _log(message, "out", f"[rate limited] {limit_msg}")
        return
    try:
        with keep_typing(message.chat.id):
            reply = ask_ai(message.from_user.id, text)
        send_reply(message, reply)
        _log(message, "out", reply)
    except Exception as e:
        print(f"Error in handle_message: {e}")
        bot.send_message(message.chat.id, "Something went wrong. Please try again.")
        _log(message, "out", f"[error] {e}")
