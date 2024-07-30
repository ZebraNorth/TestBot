from testbot import expect, regex, text_channel


async def test_bigtext() -> None:
    '''
    Ensure that big text can be generated with emoticons.
    '''

    general = text_channel('hive-play-room')

    await general.send('hc!bigtext "a"')
    await expect(general, regex('> <:hex_a:\\d+>'))
