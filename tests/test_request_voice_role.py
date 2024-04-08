import tests.hexcorp
from testbot import expect, text, text_channel


@tests.hexcorp.as_hive_mxtress
async def test_store_release() -> None:
    '''
    Ensure that a drone can be relased from storage
    '''

    storage_facility = text_channel('hive-storage-facility')
    ch = text_channel()

    # Store the drone.
    await storage_facility.send('0006 :: 3742 :: 1 :: Test storage')
    await expect(
        storage_facility,
        text(
            'Drone 3742 has been stored away in the Hive Storage Chambers by the Hive Mxtress'
            ' for 1 hour and for the following reason: Test storage'
        )
    )

    # Release the drone.
    await ch.send('hc!release 3742')
    await expect(ch, text('⬡-Drone #3742 has been released from storage.'))
