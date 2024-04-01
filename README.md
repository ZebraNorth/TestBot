# TestBot

Testing framework for Discord bots.

## Installation

Clone the Git repository and run `code .` to launch Visual Studio Code.

Select "Reopen in Container" when prompted.

## Running

1. Open a terminal window with `Ctrl+'` and run: `python -m main <token>`
2. Go to https://discord.com/developers/ and log in.
3. Press "New Application" and enter "TestBot"
4. Under "Installation" select "Discord Provided Link"
5. Give it the "bot" scope and "Administrator" permissions.
6. Go to "Bot" and "Privileged Gateway Intents", and grant all privileges.
7. Go to the link given in #5 and add the bot to your server.
8. Type "start" in any channel.

## Creating Tests

Tests must be files in: `tests/test_*.py`

Test functions must be of the form:

```python
async def test_...():
    # ...
```

The general format of a test is to send a message to a channel and then check that the response from the bot is as expected.

```python
from testbot import guild, channel, expect, embed

async def test_my_command():
    ch = channel('general')
    await ch.send('!my_command')
    await expect(text('Command Response'))
```

## Function Reference

### guild() -> discord.Guild

Fetch the current guild.

### channel(name: str) -> discord.abc.GuildChannel

Fetch the channel with the given name.

### text_channel(name: str) -> discord.TextChannel

Fetch the text channel with the given name.

### voice_channel(name: str) -> discord.VoiceChannel

Fetch the voice channel with the given name.

### expect(channel: discord.textChannel, expectation)

Check for a message in the given channel with the expected format.

The expectation may be a `text` or `embed`.

### text(value: str)

Expect a normal text message.

```python
await expect(text('hello world'))
```

### embed(description: str, *fields: List[dict])

Expect an embed with the given description and fields.

Each field is a `dict` with an optional `name` and `value` attribute.

```python
await expect(embed('hello', {'name': 'a'}, {'name': 'b', 'value': 'c'}))
```
