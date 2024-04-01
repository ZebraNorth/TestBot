import asyncio
import discord
import typing

CheckFunction = typing.Callable[[asyncio.Future, discord.Message], typing.Coroutine[typing.Any, typing.Any, None]]
ExpectingType = typing.Callable[[discord.Message], typing.Coroutine[typing.Any, typing.Any, None]] | None

current_guild = None
current_expecting = None


def guild() -> discord.Guild:
    '''
    Get the current guild.

    Raises an exception if there is no current guild, ie the message was a DM.
    '''

    if current_guild is None:
        raise Exception('No current guild')

    return current_guild


def set_guild(new_guild: discord.Guild | None) -> None:
    '''
    Set the current guild.
    '''

    global current_guild
    current_guild = new_guild


def expecting() -> ExpectingType:
    '''
    Get the function that will process the next received message.
    '''

    return current_expecting


def set_expecting(new_expecting: ExpectingType) -> None:
    '''
    Set the function that will process the next received message.
    '''

    global current_expecting
    current_expecting = new_expecting


def channel(name: str) -> discord.abc.GuildChannel:
    '''
    Fetch a channel in the current guild.

    name: The name of the channel to fetch.

    Raises an Exception if the channel does not exist.
    '''

    g = guild()

    if g is None:
        raise Exception('Could not find channel ' + name + ': No current guild')

    for channel in g.channels:
        if channel.name == name:
            return channel

    raise Exception('Could not find channel ' + name)


def text_channel(name: str) -> discord.TextChannel:
    '''
    Fetch a text channel.
    '''
    c = channel(name)

    if not isinstance(c, discord.TextChannel):
        raise Exception('Channel #' + name + ' is not a text channel')

    return c


def voice_channel(name: str) -> discord.VoiceChannel:
    '''
    Fetch a voice channel.
    '''
    c = channel(name)

    if not isinstance(c, discord.VoiceChannel):
        raise Exception('Channel #' + name + ' is not a voice channel')

    return c


def text(value: str) -> CheckFunction:
    '''
    Expect a text message.

    value: The text expected to be received.

    Raises an Exception if the actual text does not match the expected text.
    '''

    async def check(future: asyncio.Future, message: discord.Message) -> None:
        if message.content != value:
            raise Exception('Expected: "' + value + '" Found: "' + message.content + '"')

        future.set_result(True)

    return check


def embed(description: str, *fields: dict) -> CheckFunction:
    '''
    Expect a message with an embed.

    Expected fields are dicts with the optional keys 'name' and 'value'.

    description: The expected description of the embed.
    fields: The expected fields of the embed.

    Raises an Exception if the actual embed does not match the expected embed.
    '''

    async def check(future: asyncio.Future, message: discord.Message) -> None:
        if len(message.embeds) == 0:
            raise Exception('Expected embed "' + description + '", Found no embeds')

        if message.embeds[0].description != description:
            found = message.embeds[0].description if message.embeds[0].description is not None else '[None]'
            raise Exception('Expected embed: "' + description + '" Found: "' + found + '"')

        if len(message.embeds[0].fields) != len(fields):
            expected_count = str(len(message.embeds[0].fields))
            raise Exception('Expected embed to have ' + expected_count + ', Found ' + str(len(fields)))

        for [i, expected] in enumerate(fields):
            for key, value in expected.items():
                if value != getattr(message.embeds[0].fields[i], key):
                    expected_field = str(i) + ' to have "' + key + '" = "' + value
                    actual = message.embeds[0].fields[i].name
                    raise Exception('Expected embed field ' + expected_field + '", Found: "' + actual + '"')

        future.set_result(True)

    return check


async def expect(channel: discord.TextChannel, expectation: CheckFunction) -> None:
    '''
    Expect a message from the bot under test.

    channel: The channel on which the message is expected.
    expectation: The value expected to be recevied.
    '''

    future = asyncio.get_running_loop().create_future()

    def check(message: discord.Message) -> typing.Coroutine[typing.Any, typing.Any, None]:
        '''
        Close around the completion future and pass it in to the expectation.
        '''

        return expectation(future, message)

    set_expecting(check)

    try:
        async with asyncio.timeout(3):
            await future
    except TimeoutError:
        raise Exception('Test timed out')
    finally:
        set_expecting(None)


def role(name: str) -> discord.Role:
    '''
    Fetch a user role by name.

    Raises an Exception if the role is not found.
    '''
    r = discord.utils.get(guild().roles, name=name)

    if r is None:
        raise Exception('Failed to find role: ' + name)

    return r
