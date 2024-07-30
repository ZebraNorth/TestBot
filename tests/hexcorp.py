import discord
import functools
import logging
import testbot
import typing

log = logging.getLogger('testbot')

# The object being decorated is a function which accepts any arguments and returns any type.
AnyFunction = typing.Callable[..., typing.Any]

# The decorator factory returns a decorator, which i.
DecoratorType = typing.Callable[[AnyFunction], AnyFunction]


def get_role(name: str) -> discord.Role:
    '''
    Get a user role.

    Raises an exception if the role is not found in the current guild.
    '''

    role = discord.utils.get(testbot.guild().roles, name=name)

    if role is None:
        raise Exception('Could not find the role "' + name + '"')

    return role


def as_drone(func: AnyFunction) -> AnyFunction:
    '''
    Returns a wrapper around the given function.
    '''

    @functools.wraps(func)
    async def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        '''
        Give TestBot the Drone role and remove the Hive Mxtress role.
        '''

        me = testbot.guild().me

        if not discord.utils.get(me.roles, name='⬡-Drone'):
            log.debug('Removing Drove Hive Mxtress role')
            await me.remove_roles(get_role('Drone Hive Mxtress'))
            assignment_channel = testbot.text_channel('drone-hive-assignment')
            log.debug('Submitting to HexCorp')
            await assignment_channel.send('I submit myself to the HexCorp Drone Hive.')
            log.debug('Awaiting assignment')
            await testbot.expect(assignment_channel, testbot.text(me.mention + ': Assigned.'))
            log.debug('Assignment complete')

        return await func(*args, **kwargs)

    return wrapper


def as_hive_mxtress(func: AnyFunction) -> AnyFunction:
    '''
    Returns a wrapper around the given function.
    '''

    @functools.wraps(func)
    async def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        '''
        Give TestBot the Drone role and remove the Hive Mxtress role.
        '''

        me = testbot.guild().me

        if discord.utils.get(me.roles, name='⬡-Drone'):
            log.debug('Unassigning as drone')
            # Unassign in the moderation channel so it still works even if speech optimization is enabled.
            ch = testbot.text_channel('moderation-channel')
            await ch.send('hc!unassign')

            # The bot will try to respond with a DM but this will fail because bots cannot DM other bots.
            # await testbot.expect(ch, testbot.text('Drone with ID 3521 unassigned.'))
            await testbot.expect(me, testbot.remove_role('⬡-Drone'))

        if not discord.utils.get(me.roles, name='Drone Hive Mxtress'):
            log.debug('Acquiring Drone Hive Mxtress role')
            await me.add_roles(get_role('Drone Hive Mxtress'))
            log.debug('Waiting for role')
            await testbot.expect(me, testbot.add_role('Drone Hive Mxtress'))

        return await func(*args, **kwargs)

    return wrapper
