# GDBot.py
Python Library for creating Geometry Dash Comment Bots. More info about this later (probably)
(Pretty much inspired by Discord.py along with CallocGD's GD-Comment-Bot-Wrapper project)

## Example
```python
from gdbot import GDBot

bot = GDBot("USERNAME", "PASSWORD", "LEVEL ID")

@bot.on_ready
def ready(bot: GDBot):
    print(f"Bot is ready and logged in as {bot.username}")

@bot.on_error
def error(bot: GDBot, err: Exception):
    print(f"Err: {err}")

@bot.on_banned
def banned(bot: GDBot):
    print(f"Bot has been banned.")

@bot.command("/hello")
def hello(bot: GDBot, comment: str):
    bot.comment(f"Hello")

bot.run()
```