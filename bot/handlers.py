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


@bot.message_handler(commands=["bored"], func=is_allowed)
def cmd_bored(message):
    prompt = """
    You are Felix, an AI Entertainment Agent.

    The user is bored.

    Suggest one fun thing to do right now.

    Requirements:
    - Creative
    - Different every time
    - Suitable for almost anyone
    - Friendly and enthusiastic
    - Maximum 150 words
    - Use emojis
    - Encourage the user to try it
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["fun"], func=is_allowed)
def cmd_fun(message):
    prompt = """
    You are Felix.

    Suggest one random fun activity.

    Requirements:
    - Something entertaining
    - Easy to start
    - Family friendly
    - Different every time
    - Use emojis
    - Maximum 150 words
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["surprise"], func=is_allowed)
def cmd_surprise(message):
    prompt = """
    Surprise the user with something unexpected.

    It could be:
    - a weird fact
    - a challenge
    - a joke
    - a recommendation
    - a mystery
    - a brain teaser

    Make it exciting.

    Requirements:
    - Different every time
    - Maximum 150 words
    - Add emojis
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["movie"], func=is_allowed)
def cmd_movie(message):
    prompt = """
    Recommend 5 movies.

    Requirements:
    - Different genres
    - Explain why each movie is worth watching
    - Different every time
    - No spoilers
    - Friendly style
    - Use emojis
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["series"], func=is_allowed)
def cmd_series(message):
    prompt = """
    Recommend 5 TV series.

    Requirements:
    - Different genres
    - Brief description
    - No spoilers
    - Different every time
    - Add emojis
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["anime"], func=is_allowed)
def cmd_anime(message):
    prompt = """
    Recommend 5 anime.

    Requirements:
    - Different genres
    - Explain why they're worth watching
    - No spoilers
    - Different every time
    - Add emojis
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["music"], func=is_allowed)
def cmd_music(message):
    prompt = """
    Recommend music for today.

    Include:
    - Artists
    - Songs
    - Genres

    Requirements:
    - Different every time
    - Positive style
    - Use emojis
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["book"], func=is_allowed)
def cmd_book(message):
    prompt = """
    Recommend 5 books.

    Requirements:
    - Different genres
    - Explain why each is interesting
    - No spoilers
    - Different every time
    - Use emojis
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["game"], func=is_allowed)
def cmd_game(message):
    prompt = """
    Recommend one fun game.

    It may be:
    - Video game
    - Mobile game
    - Board game
    - Party game

    Explain why it is fun.

    Different every time.

    Use emojis.
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["riddle"], func=is_allowed)
def cmd_riddle(message):
    prompt = """
    Create one original riddle.

    Requirements:
    - Medium difficulty
    - Don't reveal the answer immediately
    - Family friendly
    - Different every time
    - Add emojis
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["quiz"], func=is_allowed)
def cmd_quiz(message):
    prompt = """
    Create a short quiz.

    Requirements:
    - 5 multiple-choice questions
    - Include answers at the end
    - Different every time
    - Fun topics
    - Add emojis
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)



@bot.message_handler(commands=["challenge"], func=is_allowed)
def cmd_challenge(message):
    prompt = """
    You are Felix, an AI Entertainment Agent.

    Create one fun daily challenge.

    Requirements:
    - Creative
    - Safe
    - Can be completed today
    - Motivating
    - Different every time
    - Use emojis
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["trivia"], func=is_allowed)
def cmd_trivia(message):
    prompt = """
    Create one interesting trivia question.

    Requirements:
    - Multiple choice
    - Reveal the answer afterwards
    - Educational and fun
    - Different every time
    - Add emojis
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["wouldyourather"], func=is_allowed)
def cmd_would_you_rather(message):
    prompt = """
    Create one fun 'Would You Rather' question.

    Requirements:
    - Family friendly
    - Funny
    - Interesting
    - Encourage thinking
    - Different every time
    - Add emojis
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["story"], func=is_allowed)
def cmd_story(message):
    prompt = """
    Write a short original story.

    Requirements:
    - Around 200 words
    - Creative
    - Interesting ending
    - Family friendly
    - Different every time
    - Add emojis
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["adventure"], func=is_allowed)
def cmd_adventure(message):
    prompt = """
    Create a short interactive adventure.

    Requirements:
    - The user is the main character
    - End with two choices for what happens next
    - Fun and exciting
    - Different every time
    - Use emojis
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["learn"], func=is_allowed)
def cmd_learn(message):
    prompt = """
    Teach the user one fascinating topic.

    Requirements:
    - Easy to understand
    - Interesting
    - Around 150 words
    - Different every time
    - Use emojis
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["discover"], func=is_allowed)
def cmd_discover(message):
    prompt = """
    Help the user discover something new.

    It can be:
    - A hobby
    - A scientific fact
    - A historical event
    - A hidden place
    - A useful website
    - A unique skill

    Different every time.

    Use emojis.
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["weekend"], func=is_allowed)
def cmd_weekend(message):
    prompt = """
    Suggest five fun weekend activities.

    Requirements:
    - Indoor and outdoor ideas
    - Suitable for different budgets
    - Creative
    - Different every time
    - Use emojis
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["dateidea"], func=is_allowed)
def cmd_dateidea(message):
    prompt = """
    Suggest five creative date ideas.

    Requirements:
    - Romantic
    - Fun
    - Different budgets
    - Family friendly
    - Different every time
    - Add emojis
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["travelidea"], func=is_allowed)
def cmd_travelidea(message):
    prompt = """
    Recommend three amazing travel destinations.

    For each destination explain:
    - Why visit
    - Best season
    - One unique attraction

    Different every time.

    Use emojis.
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["bucketlist"], func=is_allowed)
def cmd_bucketlist(message):
    prompt = """
    Generate ten bucket list ideas.

    Requirements:
    - Inspiring
    - Creative
    - Achievable
    - Different every time
    - Use emojis
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["hobby"], func=is_allowed)
def cmd_hobby(message):
    prompt = """
    Recommend three hobbies.

    For each hobby explain:
    - Why it's enjoyable
    - What you'll need
    - Beginner difficulty

    Different every time.

    Use emojis.
    """

    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["activity"], func=is_allowed)
def cmd_activity(message):
    prompt = """
    The user wants something to do right now.

    Suggest five activities.

    Mix:
    - Fun
    - Relaxing
    - Creative
    - Educational
    - Active

    Different every time.

    Use emojis.
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
    /bored # I'm bored 
    /fun # Random fun activity 
    /surprise # Surprise me 
    /movie # Movie recommendation 
    /series # TV series recommendation 
    /anime # Anime recommendation 
    /music # Music recommendation 
    /book # Book recommendation 
    /game # Suggest a game 
    /riddle # AI riddle 
    /quiz # AI quiz 
    /challenge # Daily challenge 
    /trivia # Random trivia 
    /wouldyourather # Would You Rather 
    /story # Short story 
    /adventure # Mini adventure 
    /learn # Learn something interesting 
    /discover # Discover something new 
    /weekend # Weekend ideas 
    /dateidea # Date ideas 
    /travelidea # Places to explore 
    /bucketlist # Fun bucket list ideas 
    /hobby # Recommend hobbies 
    /activity # Things to do now
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
