from tests.hexcorp import as_hive_mxtress
from testbot import any, expect, text, text_channel


@as_hive_mxtress
async def test_emergency_release() -> None:
    ch = text_channel()

    await ch.send('hc!emergency_release 3742')
    await expect(ch, text('Restrictions disabled for drone 3742.'))


@as_hive_mxtress
async def test_toggle_id_prepending() -> None:
    ch = text_channel()

    # Enforce ID prepending.
    await ch.send('hc!toggle_id_prepending 3742')
    await expect(ch, text('3742 :: ID prepending is now mandatory.'))

    # Disabling may trigger different messages.
    disabled = any(
        text('3742 :: Prepending? More like POST pending now that that\'s over! Haha!'),
        text('3742 :: ID prependment policy relaxed.')
    )

    # Unenforce ID prepending.
    await ch.send('hc!toggle_id_prepending 3742')
    await expect(ch, disabled)

    # Enforce ID prepending with a timeout.
    await ch.send('hc!toggle_id_prepending 3742 -minutes=3')
    await expect(ch, text('3742 :: ID prepending is now mandatory for 3 minute(s).'))

    # Unenforce ID prepending.
    await ch.send('hc!toggle_id_prepending 3742')
    await expect(ch, disabled)


@as_hive_mxtress
async def test_toggle_speech_optimization() -> None:
    ch = text_channel()

    # Enforce speech optimization.
    await ch.send('hc!toggle_speech_optimization 3742')
    await expect(ch, text('3742 :: Speech optimization is now active.'))

    # Unenforce speech optimization.
    await ch.send('hc!toggle_speech_optimization 3742')
    await expect(ch, text('3742 :: Speech optimization disengaged.'))

    # Enforce speech optimization with a timeout.
    await ch.send('hc!toggle_speech_optimization 3742 -minutes=3')
    await expect(ch, text('3742 :: Speech optimization is now active for 3 minute(s).'))

    # Unenforce speech optimization.
    await ch.send('hc!toggle_speech_optimization 3742')
    await expect(ch, text('3742 :: Speech optimization disengaged.'))


@as_hive_mxtress
async def test_toggle_enforce_identity() -> None:
    ch = text_channel()

    # Enforce identity.
    await ch.send('hc!toggle_enforce_identity 3742')
    await expect(ch, text('3742 :: Identity enforcement is now active.'))

    # Unenforce identity.
    await ch.send('hc!toggle_enforce_identity 3742')
    await expect(ch, text('3742 :: Identity enforcement disengaged.'))

    # Enforce identity with a timeout.
    await ch.send('hc!toggle_enforce_identity 3742 -minutes=3')
    await expect(ch, text('3742 :: Identity enforcement is now active for 3 minute(s).'))

    # Unenforce identity.
    await ch.send('hc!toggle_enforce_identity 3742')
    await expect(ch, text('3742 :: Identity enforcement disengaged.'))


@as_hive_mxtress
async def test_toggle_drone_glitch() -> None:
    ch = text_channel()

    # Disabling may trigger different messages.
    enabled = any(
        text(
            '3742 :: Uh.. it’s probably not a problem.. probably.. but I’m showing a small discrepancy in... well,'
            ' no, it’s well within acceptable bounds again. Sustaining sequence.'
        ),
        text('3742 :: Drone corruption at un̘͟s̴a̯f̺e͈͡ levels.')
    )

    # Enable glitching.
    await ch.send('hc!toggle_drone_glitch 3742')
    await expect(ch, enabled)

    # Disable glitching.
    await ch.send('hc!toggle_drone_glitch 3742')
    await expect(ch, text('3742 :: Drone corruption at acceptable levels.'))

    # Enable glitching with a timeout.
    await ch.send('hc!toggle_drone_glitch 3742 -minutes=3')
    await expect(ch, enabled)

    # Disable glitching.
    await ch.send('hc!toggle_drone_glitch 3742')
    await expect(ch, text('3742 :: Drone corruption at acceptable levels.'))


@as_hive_mxtress
async def test_rename() -> None:
    '''
    Ensure that a drone can have its ID reassigned by the Hive Mxtress
    '''

    ch = text_channel('hex-office')

    # Rename the drone.
    await ch.send('hc!rename 3742 7777')
    await expect(ch, text('Successfully renamed drone 3742 to 7777.'))

    # Try an ID that is already in use.
    await ch.send('hc!rename 7777 7777')
    await expect(ch, text('ID 7777 already in use.'))

    # Rename them back.
    await ch.send('hc!rename 7777 3742')
    await expect(ch, text('Successfully renamed drone 7777 to 3742.'))
