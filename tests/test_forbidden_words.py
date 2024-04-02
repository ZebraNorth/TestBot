from testbot import embed, expect, guild, role, text, text_channel


async def test_list_forbidden_words() -> None:
    await guild().me.add_roles(role('Drone Hive Mxtress'))
    office = text_channel('hex-office')
    await office.send('hc!list_forbidden_words')
    embeds = [
        {'name': 'think', 'value': 'Pattern: `t+h+i+n+k+`'},
        {'name': 'thought', 'value': 'Pattern: `t+h+o+u+g+h+t+`'},
        {'name': 'morning', 'value': 'Pattern: `m+o+r+n+i+n+g+`'},
    ]
    await expect(office, embed('These are the currently configured forbidden words.', *embeds))


async def test_add_remove_forbidden_word() -> None:
    await guild().me.add_roles(role('Drone Hive Mxtress'))
    office = text_channel('hex-office')

    # Add a new word.
    await office.send('hc!add_forbidden_word "test pattern" "hello.*world"')

    # Check for the success message.
    await expect(office, text('Successfully added forbidden word `test pattern` with pattern `hello.*world`.'))

    # Check that it has been added.
    await office.send('hc!list_forbidden_words')
    embeds = [
        {'name': 'think', 'value': 'Pattern: `t+h+i+n+k+`'},
        {'name': 'thought', 'value': 'Pattern: `t+h+o+u+g+h+t+`'},
        {'name': 'morning', 'value': 'Pattern: `m+o+r+n+i+n+g+`'},
        {'name': 'test pattern', 'value': 'Pattern: `hello.*world`'},
    ]
    await expect(office, embed('These are the currently configured forbidden words.', *embeds))

    # Remove the word.
    await office.send('hc!remove_forbidden_word "test pattern"')

    # Check for the success message.
    await expect(office, text('Successfully removed forbidden word with name `test pattern`.'))

    # Check that it has been removed.
    await office.send('hc!list_forbidden_words')
    embeds.pop()
    await expect(office, embed('These are the currently configured forbidden words.', *embeds))
