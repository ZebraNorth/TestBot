import tests.hexcorp
from testbot import expect, text, text_channel


@tests.hexcorp.as_hive_mxtress
async def test_amplify() -> None:
    '''
    Ensure that Hive Mxtress can speak through other drones.
    '''

    office = text_channel('hex-office')
    general = text_channel('general')

    await office.send('hc!amplify "hello world" general 3742')
    await expect(general, text('3742 :: hello world'))
