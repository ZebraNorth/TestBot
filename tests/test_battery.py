import tests.hexcorp
from testbot import expect, text, text_channel


@tests.hexcorp.as_hive_mxtress
async def test_set_battery_type() -> None:
    '''
    Ensure that a drone can have their battery type set.
    '''

    ch = text_channel()

    await ch.send('hc!set_battery_type 3742 high')
    await expect(ch, text('Battery type for drone 3742 is now: High'))

    await ch.send('hc!set_battery_type 3742 medium')
    await expect(ch, text('Battery type for drone 3742 is now: Medium'))

    await ch.send('hc!set_battery_type 3742 low')
    await expect(ch, text('Battery type for drone 3742 is now: Low'))
