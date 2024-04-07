import tests.hexcorp
from testbot import expect, text, text_channel


@tests.hexcorp.as_hive_mxtress
async def test_drain_energize() -> None:
    '''
    Ensure that a drone can have their battery drained.
    '''

    ch = text_channel()

    # Make sure that the drone is battery powered.
    await ch.send('hc!emergency_release 3742')
    await expect(ch, text('Restrictions disabled for drone 3742.'))

    await ch.send('hc!toggle_battery_power 3742 -minutes=60')
    await expect(ch, text('3742 :: Drone disconnected from HexCorp power grid for 60 minutes.'))

    await ch.send('hc!drain 3742')
    await expect(ch, text('3742 :: Drone battery has been forcibly drained. Remaining battery now at 90%'))

    await ch.send('hc!energize 3742')
    await expect(ch, text('3742 :: This unit is fully recharged. Thank you Hive Mxtress.'))

    await ch.send('hc!toggle_battery_power 3742')
    await expect(ch, text('3742 :: Drone reconnected to HexCorp power grid.'))


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
