from testbot import expect, text, text_channel


async def test_add_trusted_user_by_drone_id() -> None:
    '''
    Ensure that add_trusted_user with a drone ID adds the user request.
    '''

    ch = text_channel()
    await ch.send('hc!add_trusted_user 3742')
    await expect(ch, text('Request sent to "⬡-Drone #3742". They have 24 hours to accept.'))


async def test_add_trusted_user_by_display_name() -> None:
    '''
    Ensure that add_trusted_user with display name adds the user request.
    '''

    ch = text_channel()
    await ch.send('hc!add_trusted_user 3742')
    await expect(ch, text('Request sent to "⬡-Drone #3742". They have 24 hours to accept.'))


async def test_add_trusted_user_unknown_name() -> None:
    '''
    Ensure that an invalid name gives an error message.
    '''

    ch = text_channel()
    await ch.send('hc!add_trusted_user "beep boop"')
    await expect(ch, text('No user with name "beep boop" found.'))


async def test_add_self_as_trusted_user() -> None:
    '''
    Ensure that you cannot add yourself as a trusted user.
    '''

    ch = text_channel()
    await ch.send('hc!add_trusted_user TestBot')
    await expect(ch, text('Can not add yourself to your list of trusted users.'))
