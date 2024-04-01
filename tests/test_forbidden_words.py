from testbot import embed, expect, guild, role, text_channel


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
