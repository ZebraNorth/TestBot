import asyncio
import discord
import glob
import importlib
import inspect
import logging
import re
import sys
import time
import typing
from testbot import find_bot, get_bot, member_update, receive_message, set_bot, set_default_channel, set_guild

# Test functions are async, take no parameters, and return None.
TestFunction = typing.Callable[[], typing.Coroutine[typing.Any, typing.Any, None]]

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.message_content = True

bot = discord.Bot(intents=intents, guild_subscriptions=True)

log = logging.getLogger('testbot')
tests = []


def find_tests() -> typing.List[TestFunction]:
    '''
    Find all the test functions.

    Test functions must be in the 'tests' directory and start with 'test_'.

    Returns a list of functions.
    '''

    functions: typing.List[TestFunction] = []
    paths = sorted(glob.glob('./tests/test*.py'))

    for path in paths:
        module_name_match = re.match('./tests/(.*)\\.py', path)

        if not module_name_match:
            continue

        module_name = module_name_match.group(1)

        module = importlib.import_module('tests.' + module_name)
        members = inspect.getmembers(module, inspect.isfunction)
        module_functions = [f[1] for f in members if f[0].startswith('test_')]

        for function in module_functions:
            function.__name__ = module_name + '.' + function.__name__

        functions.extend(module_functions)

    return functions


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member) -> None:
    member_update(after)


@bot.event
async def on_message(message: discord.Message) -> None:
    '''
    Handle an incoming message.
    '''

    # Process messages from the bot under test.
    if find_bot() and message.author.id == get_bot().id:
        receive_message(message)

    # Process the command to run the test suite.
    if message.content.startswith('!test'):
        if find_bot():
            await message.author.send('A test is already in progress')
            return

        if message.guild is None:
            await message.author.send('This command cannot be used in DM')
            return

        if not isinstance(message.channel, discord.TextChannel):
            await message.author.send('This command can only be used in a text channel')
            return

        # Find the bot to test.
        bot_name = 'HexCorp Mxtress AI Dev'
        bot_under_test = discord.utils.get(message.guild.members, display_name=bot_name)

        if bot_under_test is None:
            log.error('Failed to find bot ' + bot_name)
            await message.author.send('Cannot find bot to test: ' + bot_name)
            return

        set_bot(bot_under_test)
        set_guild(message.guild)
        set_default_channel(message.channel)

        failures = []
        regex = '.*' + message.content[6:].strip() + '.*'

        filtered_tests = [t for t in tests if re.match(regex, t.__name__)]
        start_time = time.time()

        for test in filtered_tests:
            try:
                log.info('Running ' + test.__name__ + '...')
                await message.channel.send('Running ' + test.__name__ + '...')
                await test()
            except asyncio.CancelledError:
                # Ignore cancelled tasks, the error is handled in expect().
                pass
            except Exception as e:
                failures.append({'name': test.__name__, 'description': str(e)})

        total = str(len(filtered_tests))
        description = 'Completed **' + total + '** tests with **' + str(len(failures)) + '** failures'
        colour = discord.Color.red() if len(failures) else discord.Color.green()

        if len(failures):
            description += '\n\n❌ **FAILURE**'
        else:
            description += '\n\n✅ **SUCCESS**'

        embed = discord.Embed(title='Test Result', description=description, color=colour)

        for failure in failures:
            embed.add_field(name='❌ ' + failure['name'], value=failure['description'], inline=False)

        duration = time.time() - start_time
        embed.set_footer(text=f'Test suite completed in {duration:.2f} seconds')

        await message.channel.send(embed=embed)

        set_bot(None)
        set_guild(None)


def configure_log() -> None:
    '''
    Set up the logger.
    '''

    log_handler = logging.StreamHandler()
    log_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

    log_handler.setFormatter(formatter)

    log.addHandler(log_handler)

    log.setLevel(logging.DEBUG)


if len(sys.argv) != 2:
    print('Usage: python -m main <token>')
    exit(1)

configure_log()

tests = find_tests()

log.debug('Found tests: ' + ', '.join([t.__name__ for t in tests]))

bot.run(sys.argv[1])
