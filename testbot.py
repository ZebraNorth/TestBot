import asyncio
import discord
import functools
import logging
import re
import typing

log = logging.getLogger('testbot')
CheckFunction = typing.Callable[[typing.Any], typing.Coroutine[typing.Any, typing.Any, None]]

current_guild = None
expect_future = None
awaiting_from = 0
default_channel = None
bot_under_test = None
total_expectations = 0


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


def get_bot() -> discord.Member:
    '''
    Get the Member object for the bot under test.

    Raises an Exception if there is no bot under test.
    '''

    if bot_under_test is None:
        raise Exception('No bot under test')

    return bot_under_test


def find_bot() -> discord.Member | None:
    '''
    Get the Member object for the bot under test, or None.
    '''

    return bot_under_test


def set_bot(bot: discord.Member | None) -> None:
    '''
    Set the bot under test.
    '''

    global bot_under_test
    bot_under_test = bot


def get_total_expectations() -> int:
    '''
    Get the number of times that the expect() function has been called.
    '''

    return total_expectations


def member_update(member: discord.Member) -> None:
    '''
    Handle a change to a guild member.
    '''

    global expect_future

    if expect_future is not None and not expect_future.done():
        if member.id == awaiting_from:
            expect_future.set_result(member)


def receive_message(message: discord.Message) -> None:
    '''
    Handle a received message.
    '''

    global expect_future

    if expect_future is not None and not expect_future.done():
        if message.author.id == awaiting_from or message.channel.id == awaiting_from:
            expect_future.set_result(message)


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
    '''

    async def check(message: discord.Message) -> None:
        '''
        Check the text of the message.

        Raises an Exception if the actual text does not match the expected text.
        '''

        if message.content != value:
            raise Exception('Expected: "' + value + '" Found: "' + message.content + '"')

    return check


def regex(rx: str) -> CheckFunction:
    '''
    Expect a text message.

    rx: A regular expression matching the text expected to be received.
    '''

    async def check(message: discord.Message) -> None:
        '''
        Check the text of the message.

        Raises an Exception if the actual text does not match the expected text.
        '''

        if not re.fullmatch(rx, message.content):
            raise Exception('Expected: "' + rx + '" Found: "' + message.content + '"')

    return check


def add_role(role_name: str) -> CheckFunction:
    '''
    Expect a user to obtain the given role.
    '''

    async def check(member: discord.Member) -> None:
        '''
        Check that the member has a particular role.
        Raises an exception if the user does not have the role.
        '''

        if discord.utils.get(member.roles, name=role_name) is None:
            raise Exception('Expected role "' + role_name + '" to be added')

    return check


def remove_role(role_name: str) -> CheckFunction:
    '''
    Expect a user to have the given role removed.
    '''

    async def check(member: discord.Member) -> None:
        '''
        Check that the member has a particular role.
        Raises an exception if the user does not have the role.
        '''

        if discord.utils.get(member.roles, name=role_name) is not None:
            raise Exception('Expected role "' + role_name + '" to be removed')

    return check


def all(*checks: CheckFunction) -> CheckFunction:
    '''
    Require multiple checks to pass.
    '''

    async def check(arg: typing.Any) -> None:
        '''
        Call every check.
        Raises an exception if any of them fail.
        '''
        for c in checks:
            await c(arg)

    return check


def any(*checks: CheckFunction) -> CheckFunction:
    '''
    Require at least one of multiple checks to pass.
    '''

    async def check(arg: typing.Any) -> None:
        '''
        Call every check.
        Raises an exception if all of them fail.
        '''

        for c in checks:
            try:
                await c(arg)
                return
            except Exception:
                pass

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


def get_expectation_name(expectation: CheckFunction) -> str:
    '''
    Get a readable name for an expectation.
    '''

    expecting_func_name = expectation.__qualname__.split('.')[0]

    closure = getattr(expectation, '__closure__', None)

    if closure:
        func_params = ', '.join([str(c.cell_contents) for c in closure])
    else:
        func_params = ''

    return expecting_func_name + '(' + func_params + ')'


async def expect(sender: discord.TextChannel | discord.Member, expectation: CheckFunction) -> None:
    '''
    Expect a message from the bot under test.

    sender: The channel on which the message is expected or the user from which the message should originate.
    expectation: The value expected to be recevied.
    '''

    global expect_future
    global awaiting_from
    global total_expectations

    if not callable(expectation):
        raise Exception('expect() parameter 2 must be a CheckFunction, found a ' + str(type(expectation)))

    expectation_name = get_expectation_name(expectation)
    expect_future = asyncio.get_running_loop().create_future()
    awaiting_from = sender.id
    total_expectations += 1
    messages = []

    log.debug('Testing expectation ' + expectation_name)

    try:
        passed_synchronously = False

        # If the sender is a Member then try running the check synchronously.
        # A member_update event happens synchronously when adding or removing a role and so may
        # have already happened by the time we get here.
        # If it hasn't happened then keep waiting.
        if isinstance(sender, discord.Member):
            try:
                await expectation(sender)
                log.debug('Expectation passed synchronously')
                passed_synchronously = True
            except Exception:
                # Ignore exceptions and try again asynchronously
                pass

        if not passed_synchronously:
            async with asyncio.timeout(15):
                # Keep trying until the test passes or times out.
                while True:
                    # Wait for the response from the bot under test.
                    await expect_future

                    # Process the response.
                    try:
                        result = expect_future.result()
                        messages.append(result)
                        expect_future = asyncio.get_running_loop().create_future()
                        await expectation(result)
                        log.debug('Expectation passed asynchronously')
                        break
                    except Exception:
                        # Failed to match.
                        log.debug('Failed to meet expectations.  Retrying...')
    except TimeoutError as e:
        # TimeoutError does not have an error message, so create one.
        msg = 'Test timed out waiting for ' + expectation_name

        if len(messages):
            msg += '. Received: ' + ', '.join(messages)

        raise Exception(msg) from e
    finally:
        expect_future = None


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


# The object being decorated is a function which accepts any arguments and returns any type.
AnyFunction = typing.Callable[..., typing.Any]

# The decorator factory returns a decorator, which i.
DecoratorType = typing.Callable[[AnyFunction], AnyFunction]


def with_role(name: str) -> DecoratorType:
    '''
    A function decorator for giving TestBot a certain role for the duration of a test.

    The name parameter is the name of the role to assign.
    '''

    def decorator(func: AnyFunction) -> AnyFunction:
        '''
        Return a wrapper around the given function.
        '''

        @functools.wraps(func)
        async def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            '''
            Assign a role, call the wrapped function, then remove the role.
            '''

            role = discord.utils.get(guild().roles, name=name)

            if role is None:
                raise Exception('Could not find a role with the name: ' + name)

            await guild().me.add_roles(role)

            result = await func(*args, **kwargs)

            await guild().me.remove_roles(role)

            return result

        return wrapper

    return decorator
