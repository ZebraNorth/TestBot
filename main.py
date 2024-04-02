import asyncio
import discord
import glob
import importlib
import inspect
import re
import sys
import typing
from testbot import receive_message, set_guild

# Test functions are async, take no parameters, and return None.
TestFunction = typing.Callable[[], typing.Coroutine[typing.Any, typing.Any, None]]

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.message_content = True

bot = discord.Bot(intents=intents, guild_subscriptions=True)


def find_tests() -> typing.List[TestFunction]:
    '''
    Find all the test functions.

    Test functions must be in the 'tests' directory and start with 'test_'.

    Returns a list of functions.
    '''

    functions: typing.List[TestFunction] = []
    paths = sorted(glob.glob('./tests/test*.py'))

    for path in paths:
        module_name = re.match('./tests/(.*)\\.py', path)

        if not module_name:
            continue

        module = importlib.import_module('tests.' + module_name.group(1))
        members = inspect.getmembers(module, inspect.isfunction)
        module_functions = [f[1] for f in members if f[0].startswith('test_')]

        functions.extend(module_functions)

    return functions


tests = find_tests()


@bot.event
async def on_message(message: discord.Message) -> None:
    '''
    Handle an incoming message.
    '''

    # Ignore messages from self.
    if message.author.id == message.guild.me:
        return

    receive_message(message)

    if message.content == '!test':
        set_guild(message.guild)
        failures = []

        for test in tests:
            try:
                await message.channel.send('Running test ' + test.__name__ + '...')
                await test()
            except asyncio.CancelledError:
                # Ignore cancelled tasks, the error is handled in expect().
                pass
            except Exception as e:
                failures.append(test.__name__ + ': ' + str(e))

        await message.channel.send('Completed ' + str(len(tests)) + ' tests with ' + str(len(failures)) + ' failures')

        if not len(failures):
            await message.channel.send('✅ SUCCESS')

        for failure in failures:
            await message.channel.send('❌ ' + failure)


if len(sys.argv) != 2:
    print('Usage: python -m main <token>')
    exit(1)

bot.run(sys.argv[1])
