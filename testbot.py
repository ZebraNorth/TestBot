import asyncio
import discord
import typing

CheckFunction = typing.Callable[[discord.Message], typing.Coroutine[typing.Any, typing.Any, None]]

current_guild = None
message_future = None
awaiting_from = 0
default_channel = None


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


def set_default_channel(c: discord.TextChannel) -> None:
    '''
    Set the default channel to be returned if no channel name is given to text_channel().
    '''

    global default_channel
    default_channel = c


def receive_message(message: discord.Message) -> None:
    '''
    Handle a received message.
    '''
    global message_future

    if message_future is not None and not message_future.done():
        if message.author.id == awaiting_from or message.channel.id == awaiting_from:
            message_future.set_result(message)


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


def text_channel(name: str = '') -> discord.TextChannel:
    '''
    Fetch a text channel.

    If the name is not specified then it selects the channel from which the "!test" command was issued.
    '''

    if not name:
        if default_channel is None:
            raise Exception('No default channel')

        return default_channel

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

    async def check(message: discord.Message) -> None:
        '''
        Check the text of the message.
        '''

        if message.content != value:
            raise Exception('Expected: "' + value + '" Found: "' + message.content + '"')

    return check


def embed(description: str, *fields: dict) -> CheckFunction:
    '''
    Expect a message with an embed.

    Expected fields are dicts with the optional keys 'name' and 'value'.

    description: The expected description of the embed.
    fields: The expected fields of the embed.

    Raises an Exception if the actual embed does not match the expected embed.
    '''

    async def check(message: discord.Message) -> None:
        '''
        Check the embeds within the message.
        '''

        if len(message.embeds) == 0:
            raise Exception('Expected embed "' + description + '", Found no embeds')

        if message.embeds[0].description != description:
            found = message.embeds[0].description if message.embeds[0].description is not None else '[None]'
            raise Exception('Expected embed: "' + description + '" Found: "' + found + '"')

        if len(message.embeds[0].fields) != len(fields):
            expected_count = str(len(message.embeds[0].fields))
            raise Exception('Expected embed to have ' + str(len(fields)) + ', Found ' + expected_count)

        for [i, expected] in enumerate(fields):
            for key, value in expected.items():
                if value != getattr(message.embeds[0].fields[i], key):
                    expected_field = str(i) + ' to have "' + key + '" = "' + value
                    actual = message.embeds[0].fields[i].name
                    raise Exception('Expected embed field ' + expected_field + '", Found: "' + actual + '"')

    return check


async def expect(sender: discord.TextChannel | discord.Member, expectation: CheckFunction) -> None:
    '''
    Expect a message from the bot under test.

    sender: The channel on which the message is expected or the user from which the message should originate.
    expectation: The value expected to be recevied.
    '''

    global message_future
    global awaiting_from

    message_future = asyncio.get_running_loop().create_future()
    awaiting_from = sender.id

    try:
        async with asyncio.timeout(8):
            # Wait for the response from the bot under test.
            await message_future

            # Process the response.
            await expectation(message_future.result())
    except TimeoutError as e:
        # TimeoutError does not have an error message, so create one.
        expecting_func_name = expectation.__qualname__.split('.')[0]

        closure = getattr(expectation, '__closure__', None)

        if closure:
            func_params = ', '.join([str(c.cell_contents) for c in closure])
        else:
            func_params = ''

        description = expecting_func_name + '(' + func_params + ')'
        raise Exception('Test timed out waiting for ' + description) from e
    finally:
        message_future = None


def role(name: str) -> discord.Role:
    '''
    Fetch a user role by name.

    Raises an Exception if the role is not found.
    '''
    r = discord.utils.get(guild().roles, name=name)

    if r is None:
        raise Exception('Failed to find role: ' + name)

    return r


def member(name: str) -> discord.Member:
    '''
    Fetch a member by name.
    '''

    u = discord.utils.get(guild().members, display_name=name)

    if u is None:
        raise Exception('Failed to find member: ' + name)

    return u
